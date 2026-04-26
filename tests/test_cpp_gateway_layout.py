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
        self.assertIn("cmake", readme)
        self.assertIn("g++", readme)
        self.assertIn("validate_gateway_wsl.sh", validation)
        self.assertIn("API_MODE", validation)
