import unittest
from pathlib import Path


class CppGatewayLayoutTests(unittest.TestCase):
    def test_cpp_gateway_files_exist(self):
        root = Path.cwd()
        required = [
            root / "cpp_gateway" / "CMakeLists.txt",
            root / "cpp_gateway" / "src" / "main.cpp",
            root / "cpp_gateway" / "src" / "http_server.cpp",
        ]
        self.assertTrue(all(p.exists() for p in required))

    def test_cpp_gateway_docs_cover_wsl_validation(self):
        root = Path.cwd()
        readme = (root / "cpp_gateway" / "README.md").read_text(encoding="utf-8")
        validation = (root / "docs" / "gateway-validation.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("WSL", readme)
        self.assertIn("Linux", readme)
        self.assertIn("8080", validation)
        self.assertIn("/api/chat", validation)
        self.assertIn("/api/health", validation)
        self.assertIn("GATEWAY_PORT", readme)
        self.assertIn("UPSTREAM_PORT", readme)

    def test_cpp_gateway_documents_bad_gateway_behavior(self):
        validation = (Path.cwd() / "docs" / "gateway-validation.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("网关实现审查记录", validation)
        self.assertIn("UPSTREAM_PORT=65530", validation)
        self.assertIn("502 Bad Gateway", validation)
        self.assertIn("failed to connect upstream", validation)
        self.assertIn("epoll_wait", validation)
        self.assertIn("ThreadPool", validation)

    def test_gateway_build_scripts_have_cmake_fallback(self):
        root = Path.cwd()
        for script_name in ["build_gateway_wsl.sh", "start_gateway_wsl.sh"]:
            script = (root / "scripts" / script_name).read_text(encoding="utf-8")
            with self.subTest(script=script_name):
                self.assertIn("command -v cmake", script)
                self.assertIn("g++ -std=c++17", script)
                self.assertIn("src/http_server.cpp", script)

    def test_wsl_verification_scripts_bypass_local_proxy(self):
        root = Path.cwd()
        for script_name in ["verify_runtime.sh", "verify_gateway_smoke.sh"]:
            script = (root / "scripts" / script_name).read_text(encoding="utf-8")
            with self.subTest(script=script_name):
                self.assertIn('--noproxy "*"', script)

    def test_cpp_gateway_uses_timed_nonblocking_upstream_connect(self):
        source = (Path.cwd() / "cpp_gateway" / "src" / "http_server.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("EINPROGRESS", source)
        self.assertIn("select(", source)
        self.assertIn("SO_ERROR", source)
        self.assertIn("SetSocketBlocking", source)
        self.assertIn("failed to connect upstream", source)
