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
    const auto pos = request.find("\r\n\r\n");
    std::string body = pos == std::string::npos ? "{}" : request.substr(pos + 4);
    std::string upstream_response = ForwardToUpstream(body);
    std::string response = BuildHttpResponse(upstream_response);
    send(client_fd, response.c_str(), response.size(), 0);
    close(client_fd);
}

std::string HttpServer::ForwardToUpstream(const std::string &body) const {
    std::ostringstream json;
    json << "{"
         << "\"gateway\":\"cpp\","
         << "\"forwarded_body\":" << "\"" << body << "\""
         << "}";
    return json.str();
}

std::string HttpServer::BuildHttpResponse(const std::string &json_body) const {
    std::ostringstream stream;
    stream << "HTTP/1.1 200 OK\r\n";
    stream << "Content-Type: application/json; charset=utf-8\r\n";
    stream << "Content-Length: " << json_body.size() << "\r\n";
    stream << "Connection: close\r\n\r\n";
    stream << json_body;
    return stream.str();
}
