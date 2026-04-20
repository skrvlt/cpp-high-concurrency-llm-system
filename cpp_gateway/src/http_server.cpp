#include "http_server.h"

#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace {
constexpr int kMaxEvents = 64;
constexpr int kBufferSize = 8192;
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
    char buffer[kBufferSize];
    std::memset(buffer, 0, sizeof(buffer));
    const int bytes = read(client_fd, buffer, sizeof(buffer) - 1);
    if (bytes <= 0) {
        close(client_fd);
        return;
    }

    std::string request(buffer, bytes);
    const auto request_line_end = request.find("\r\n");
    if (request_line_end == std::string::npos) {
        const std::string error = BuildErrorResponse("invalid request line");
        send(client_fd, error.c_str(), error.size(), 0);
        close(client_fd);
        return;
    }

    const std::string request_line = request.substr(0, request_line_end);
    const auto method_end = request_line.find(' ');
    const auto path_end = request_line.find(' ', method_end + 1);
    if (method_end == std::string::npos || path_end == std::string::npos) {
        const std::string error = BuildErrorResponse("invalid request format");
        send(client_fd, error.c_str(), error.size(), 0);
        close(client_fd);
        return;
    }

    const std::string method = request_line.substr(0, method_end);
    const std::string path = request_line.substr(method_end + 1, path_end - method_end - 1);
    const auto pos = request.find("\r\n\r\n");
    std::string body = pos == std::string::npos ? "{}" : request.substr(pos + 4);
    if (method != "POST" && method != "GET") {
        const std::string error = BuildErrorResponse("only GET and POST are supported");
        send(client_fd, error.c_str(), error.size(), 0);
        close(client_fd);
        return;
    }

    std::string response = ForwardToUpstream(path, body);
    send(client_fd, response.c_str(), response.size(), 0);
    close(client_fd);
}

std::string HttpServer::ForwardToUpstream(const std::string &path, const std::string &body) const {
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

    if (connect(upstream_fd, reinterpret_cast<sockaddr *>(&upstream_addr), sizeof(upstream_addr)) < 0) {
        close(upstream_fd);
        return BuildErrorResponse("failed to connect upstream");
    }

    std::ostringstream req;
    req << "POST " << path << " HTTP/1.1\r\n";
    req << "Host: " << upstream_host_ << ":" << upstream_port_ << "\r\n";
    req << "Content-Type: application/json\r\n";
    req << "Content-Length: " << body.size() << "\r\n";
    req << "Connection: close\r\n\r\n";
    req << body;
    const std::string raw_request = req.str();
    send(upstream_fd, raw_request.c_str(), raw_request.size(), 0);

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
    json << "{\"error\":\"" << message << "\"}";

    std::ostringstream stream;
    stream << "HTTP/1.1 502 Bad Gateway\r\n";
    stream << "Content-Type: application/json; charset=utf-8\r\n";
    stream << "Content-Length: " << json.str().size() << "\r\n";
    stream << "Connection: close\r\n\r\n";
    stream << json.str();
    return stream.str();
}
