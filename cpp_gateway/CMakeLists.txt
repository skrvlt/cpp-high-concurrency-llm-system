cmake_minimum_required(VERSION 3.16)
project(llm_gateway LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(llm_gateway
    src/main.cpp
    src/http_server.cpp
)

target_link_libraries(llm_gateway pthread)
