import unittest
from pathlib import Path


class FrontendContractTests(unittest.TestCase):
    def test_frontend_files_exist_and_reference_api(self):
        root = Path.cwd()
        app_js = (root / "frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn("/api/login", app_js)
        self.assertIn("/api/chat", app_js)
        self.assertIn("window.APP_CONFIG", app_js)

    def test_admin_frontend_supports_overview_panel(self):
        root = Path.cwd()
        admin_html = (root / "frontend" / "admin.html").read_text(encoding="utf-8")
        admin_js = (root / "frontend" / "admin.js").read_text(encoding="utf-8")
        self.assertIn("系统概览", admin_html)
        self.assertIn("load-overview-btn", admin_html)
        self.assertIn("/admin/overview", admin_js)

    def test_frontend_contains_demo_and_session_panels(self):
        root = Path.cwd()
        index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
        admin_html = (root / "frontend" / "admin.html").read_text(encoding="utf-8")
        self.assertIn("session-title", index_html)
        self.assertIn("demo-grid", index_html)
        self.assertIn("overview-cards", admin_html)

    def test_frontend_has_runtime_config_file(self):
        root = Path.cwd()
        config_js = (root / "frontend" / "config.js").read_text(encoding="utf-8")
        self.assertIn("API_BASE", config_js)
        self.assertIn("gateway", config_js)
        self.assertIn("URLSearchParams", config_js)
        self.assertIn("http://127.0.0.1:8080/api", config_js)

    def test_frontend_displays_runtime_status_contract(self):
        root = Path.cwd()
        index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
        admin_html = (root / "frontend" / "admin.html").read_text(encoding="utf-8")
        app_js = (root / "frontend" / "app.js").read_text(encoding="utf-8")
        admin_js = (root / "frontend" / "admin.js").read_text(encoding="utf-8")

        for html in [index_html, admin_html]:
            self.assertIn("运行状态", html)
            self.assertIn("api-base-value", html)
            self.assertIn("health-runtime-mode", html)
            self.assertIn("health-storage-mode", html)
            self.assertIn("health-model-name", html)
            self.assertIn("health-session-count", html)
        for script in [app_js, admin_js]:
            self.assertIn("/health", script)
            self.assertIn("storage_mode", script)
            self.assertIn("session_count", script)
            self.assertIn("API_BASE", script)

    def test_admin_overview_uses_defense_friendly_metric_labels(self):
        root = Path.cwd()
        admin_js = (root / "frontend" / "admin.js").read_text(encoding="utf-8")

        for label in ["用户数", "会话数", "消息数", "日志数", "模型名称"]:
            self.assertIn(label, admin_js)
