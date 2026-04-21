#include "http_server.h"

#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
int ReadIntEnv(const char *name, int fallback) {
    const char *value = std::getenv(name);
    if (value == nullptr || *value == '\0') {
        return fallback;
    }
    try {
        return std::stoi(value);
    } catch (const std::exception &) {
        return fallback;
    }
}

std::string ReadStringEnv(const char *name, const std::string &fallback) {
    const char *value = std::getenv(name);
    if (value == nullptr || *value == '\0') {
        return fallback;
    }
    return value;
}
}  // namespace

int main() {
    try {
        const int gateway_port = ReadIntEnv("GATEWAY_PORT", 8080);
        const std::string upstream_host =
            ReadStringEnv("UPSTREAM_HOST", "127.0.0.1");
        const int upstream_port = ReadIntEnv("UPSTREAM_PORT", 8000);

        HttpServer server(gateway_port, upstream_host, upstream_port);
        std::cout << "LLM gateway listening on 0.0.0.0:" << gateway_port
                  << ", upstream=" << upstream_host << ":" << upstream_port
                  << std::endl;
        server.Run();
    } catch (const std::exception &ex) {
        std::cerr << "Gateway failed: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
