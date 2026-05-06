#include "http_server.h"

#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <sys/epoll.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <cstring>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace {
constexpr int kMaxEvents = 64;
constexpr int kBufferSize = 8192;
constexpr int kUpstreamConnectTimeoutSeconds = 3;
constexpr int kUpstreamIoTimeoutSeconds = 10;

std::string JsonEscape(const std::string &input) {
    std::string output;
    output.reserve(input.size());
    for (char ch : input) {
        if (ch == '"' || ch == '\\') {
            output.push_back('\\');
        }
        output.push_back(ch);
    }
    return output;
}

bool SetSocketBlocking(int fd, bool blocking) {
    const int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        return false;
    }
    const int updated_flags = blocking ? (flags & ~O_NONBLOCK) : (flags | O_NONBLOCK);
    return fcntl(fd, F_SETFL, updated_flags) == 0;
}

void SetSocketTimeouts(int fd) {
    timeval timeout{};
    timeout.tv_sec = kUpstreamIoTimeoutSeconds;
    timeout.tv_usec = 0;
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
}

bool WaitForUpstreamConnect(int fd) {
    fd_set write_fds;
    FD_ZERO(&write_fds);
    FD_SET(fd, &write_fds);

    timeval timeout{};
    timeout.tv_sec = kUpstreamConnectTimeoutSeconds;
    timeout.tv_usec = 0;

    const int selected = select(fd + 1, nullptr, &write_fds, nullptr, &timeout);
    if (selected <= 0) {
        return false;
    }

    int socket_error = 0;
    socklen_t error_length = sizeof(socket_error);
    if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &socket_error, &error_length) < 0) {
        return false;
    }
    return socket_error == 0;
}

bool SendAll(int fd, const std::string &data) {
    std::size_t total_sent = 0;
    while (total_sent < data.size()) {
        const ssize_t sent = send(fd, data.data() + total_sent, data.size() - total_sent, 0);
        if (sent < 0) {
            if (errno == EINTR) {
                continue;
            }
            return false;
        }
        if (sent == 0) {
            return false;
        }
        total_sent += static_cast<std::size_t>(sent);
    }
    return true;
}

std::size_t ParseContentLength(const std::string &request) {
    const std::string marker = "Content-Length:";
    const auto header_end = request.find("\r\n\r\n");
    if (header_end == std::string::npos) {
        return 0;
    }

    const auto marker_pos = request.substr(0, header_end).find(marker);
    if (marker_pos == std::string::npos) {
        return 0;
    }

    std::size_t value_start = marker_pos + marker.size();
    while (value_start < header_end &&
           (request[value_start] == ' ' || request[value_start] == '\t')) {
        ++value_start;
    }
    const auto value_end = request.find("\r\n", value_start);
    const std::string value = request.substr(value_start, value_end - value_start);
    try {
        return static_cast<std::size_t>(std::stoul(value));
    } catch (...) {
        return 0;
    }
}

std::string ReadClientRequest(int client_fd) {
    SetSocketTimeouts(client_fd);

    std::string request;
    char buffer[kBufferSize];
    while (true) {
        const int bytes = recv(client_fd, buffer, sizeof(buffer), 0);
        if (bytes <= 0) {
            break;
        }
        request.append(buffer, bytes);

        const auto header_end = request.find("\r\n\r\n");
        if (header_end == std::string::npos) {
            continue;
        }

        const std::size_t expected_request_size =
            header_end + 4 + ParseContentLength(request);
        if (request.size() >= expected_request_size) {
            break;
        }
    }
    return request;
}
}

HttpServer::HttpServer(int port, std::string upstream_host, int upstream_port)
    : port_(port),
      upstream_host_(std::move(upstream_host)),
      upstream_port_(upstream_port),
      pool_(4) {}

void HttpServer::Run() {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        throw std::runtime_error("socket create failed");
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port_);

    if (bind(listen_fd, reinterpret_cast<sockaddr *>(&addr), sizeof(addr)) < 0) {
        close(listen_fd);
        throw std::runtime_error("bind failed");
    }
    if (listen(listen_fd, SOMAXCONN) < 0) {
        close(listen_fd);
        throw std::runtime_error("listen failed");
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        close(listen_fd);
        throw std::runtime_error("epoll create failed");
    }

    epoll_event ev{};
    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

    epoll_event events[kMaxEvents];
    while (true) {
        int count = epoll_wait(epoll_fd, events, kMaxEvents, -1);
        for (int i = 0; i < count; ++i) {
            int fd = events[i].data.fd;
            if (fd == listen_fd) {
                sockaddr_in client_addr{};
                socklen_t len = sizeof(client_addr);
                int client_fd = accept(listen_fd, reinterpret_cast<sockaddr *>(&client_addr), &len);
                if (client_fd >= 0) {
                    epoll_event client_event{};
                    client_event.events = EPOLLIN | EPOLLET;
                    client_event.data.fd = client_fd;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &client_event);
                }
            } else {
                epoll_ctl(epoll_fd, EPOLL_CTL_DEL, fd, nullptr);
                pool_.Enqueue([this, fd]() { HandleClient(fd); });
            }
        }
    }
}

void HttpServer::HandleClient(int client_fd) {
    std::string request = ReadClientRequest(client_fd);
    if (request.empty()) {
        close(client_fd);
        return;
    }

    const auto request_line_end = request.find("\r\n");
    if (request_line_end == std::string::npos) {
        const std::string error = BuildErrorResponse("invalid request line");
        SendAll(client_fd, error);
        close(client_fd);
        return;
    }

    const std::string request_line = request.substr(0, request_line_end);
    const auto method_end = request_line.find(' ');
    const auto path_end = request_line.find(' ', method_end + 1);
    if (method_end == std::string::npos || path_end == std::string::npos) {
        const std::string error = BuildErrorResponse("invalid request format");
        SendAll(client_fd, error);
        close(client_fd);
        return;
    }

    const std::string method = request_line.substr(0, method_end);
    const std::string path = request_line.substr(method_end + 1, path_end - method_end - 1);
    const auto pos = request.find("\r\n\r\n");
    std::string body = pos == std::string::npos ? "{}" : request.substr(pos + 4);
    if (method != "POST" && method != "GET") {
        const std::string error = BuildErrorResponse("only GET and POST are supported");
        SendAll(client_fd, error);
        close(client_fd);
        return;
    }

    std::string response = ForwardToUpstream(method, path, body);
    SendAll(client_fd, response);
    close(client_fd);
}

std::string HttpServer::ForwardToUpstream(
    const std::string &method,
    const std::string &path,
    const std::string &body) const {
    int upstream_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (upstream_fd < 0) {
        return BuildErrorResponse("failed to create upstream socket");
    }

    sockaddr_in upstream_addr{};
    upstream_addr.sin_family = AF_INET;
    upstream_addr.sin_port = htons(upstream_port_);
    if (inet_pton(AF_INET, upstream_host_.c_str(), &upstream_addr.sin_addr) <= 0) {
        close(upstream_fd);
        return BuildErrorResponse("invalid upstream host");
    }

    if (!SetSocketBlocking(upstream_fd, false)) {
        close(upstream_fd);
        return BuildErrorResponse("failed to configure upstream socket");
    }

    const int connect_result =
        connect(upstream_fd, reinterpret_cast<sockaddr *>(&upstream_addr), sizeof(upstream_addr));
    if (connect_result < 0) {
        if (errno != EINPROGRESS || !WaitForUpstreamConnect(upstream_fd)) {
            close(upstream_fd);
            return BuildErrorResponse("failed to connect upstream");
        }
    }
    SetSocketBlocking(upstream_fd, true);
    SetSocketTimeouts(upstream_fd);

    std::ostringstream req;
    req << method << " " << path << " HTTP/1.1\r\n";
    req << "Host: " << upstream_host_ << ":" << upstream_port_ << "\r\n";
    if (method == "POST") {
        req << "Content-Type: application/json\r\n";
        req << "Content-Length: " << body.size() << "\r\n";
    } else {
        req << "Content-Length: 0\r\n";
    }
    req << "Connection: close\r\n\r\n";
    if (method == "POST") {
        req << body;
    }
    const std::string raw_request = req.str();
    if (!SendAll(upstream_fd, raw_request)) {
        close(upstream_fd);
        return BuildErrorResponse("failed to send upstream request");
    }

    std::string response;
    char response_buffer[kBufferSize];
    while (true) {
        const int received = recv(upstream_fd, response_buffer, sizeof(response_buffer), 0);
        if (received <= 0) {
            break;
        }
        response.append(response_buffer, received);
    }
    close(upstream_fd);

    if (response.empty()) {
        return BuildErrorResponse("empty upstream response");
    }
    return response;
}

std::string HttpServer::BuildErrorResponse(const std::string &message) const {
    std::ostringstream json;
    json << "{\"error\":\"" << JsonEscape(message) << "\"}";

    std::ostringstream stream;
    stream << "HTTP/1.1 502 Bad Gateway\r\n";
    stream << "Content-Type: application/json; charset=utf-8\r\n";
    stream << "Content-Length: " << json.str().size() << "\r\n";
    stream << "Connection: close\r\n\r\n";
    stream << json.str();
    return stream.str();
}
