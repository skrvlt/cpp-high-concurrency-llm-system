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
