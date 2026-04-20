#pragma once

#include "thread_pool.h"

#include <string>

class HttpServer {
public:
    HttpServer(int port, std::string upstream_host, int upstream_port);
    void Run();

private:
    int port_;
    std::string upstream_host_;
    int upstream_port_;
    ThreadPool pool_;

    void HandleClient(int client_fd);
    std::string ForwardToUpstream(const std::string &body) const;
    std::string BuildHttpResponse(const std::string &json_body) const;
};
