import unittest
from pathlib import Path


class FrontendContractTests(unittest.TestCase):
    def test_frontend_files_exist_and_reference_api(self):
        root = Path.cwd()
        app_js = (root / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn("/api/login", app_js)
        self.assertIn("/api/chat", app_js)
