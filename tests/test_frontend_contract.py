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

    def test_frontend_uses_safe_dom_rendering(self):
        root = Path.cwd()
        for script_name in ["app.js", "admin.js"]:
            script = (root / "frontend" / script_name).read_text(encoding="utf-8")
            with self.subTest(script=script_name):
                self.assertIn("createTextElement", script)
                self.assertNotIn(".innerHTML =", script)

    def test_frontend_sends_tokens_with_authorization_header(self):
        root = Path.cwd()
        for script_name in ["app.js", "admin.js"]:
            script = (root / "frontend" / script_name).read_text(encoding="utf-8")
            with self.subTest(script=script_name):
                self.assertIn("Authorization", script)
                self.assertNotIn("?token=", script)

    def test_admin_frontend_displays_benchmark_cards(self):
        root = Path.cwd()
        admin_html = (root / "frontend" / "admin.html").read_text(encoding="utf-8")
        admin_js = (root / "frontend" / "admin.js").read_text(encoding="utf-8")

        self.assertIn("测试结果", admin_html)
        self.assertIn("benchmark-box", admin_html)
        self.assertIn("gateway-health.json", admin_js)
        self.assertIn("gateway-chat.json", admin_js)

    def test_user_frontend_supports_model_switching_and_collaboration(self):
        root = Path.cwd()
        index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
        app_js = (root / "frontend" / "app.js").read_text(encoding="utf-8")

        self.assertIn("model-select", index_html)
        self.assertIn("collaborate-btn", index_html)
        self.assertIn("/models", app_js)
        self.assertIn("/chat/collaborate", app_js)
        self.assertIn("provider", app_js)
        self.assertIn("model", app_js)

    def test_user_frontend_uses_stable_api_url_joining(self):
        app_js = (Path.cwd() / "frontend" / "app.js").read_text(encoding="utf-8")

        self.assertIn("function apiUrl", app_js)
        self.assertNotIn('replace("/api", "")', app_js)

    def test_video_demo_dashboard_exists_and_covers_system_modules(self):
        root = Path.cwd()
        demo_html = (root / "frontend" / "demo.html").read_text(encoding="utf-8")
        demo_js = (root / "frontend" / "demo.js").read_text(encoding="utf-8")

        for marker in [
            "视频录制演示驾驶舱",
            "C++ epoll 网关",
            "Python FastAPI 服务",
            "LLM 模型层",
            "多模型协作",
            "SQLite / 日志",
            "压测结果",
            "5 分钟录制脚本",
        ]:
            self.assertIn(marker, demo_html + demo_js)
        self.assertIn("gateway-health.json", demo_js)
        self.assertIn("gateway-chat.json", demo_js)
        self.assertIn("/api/health", demo_js)
