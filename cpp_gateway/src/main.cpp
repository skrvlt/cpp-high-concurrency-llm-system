#include "http_server.h"

#include <iostream>

int main() {
    try {
        HttpServer server(8080, "127.0.0.1", 8000);
        std::cout << "LLM gateway listening on 0.0.0.0:8080" << std::endl;
        server.Run();
    } catch (const std::exception &ex) {
        std::cerr << "Gateway failed: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
