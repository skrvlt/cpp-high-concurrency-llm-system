import unittest

from fastapi.testclient import TestClient

from services.ai_service.app.main import app


client = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_health_endpoint_returns_runtime_contract(self):
        response = client.get("/api/health")

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("ok", body["status"])
        self.assertEqual("ai_service", body["service"])
        self.assertIn(body["runtime_mode"], {"demo", "remote"})
        self.assertIn("model_name", body)
        self.assertIn("session_count", body)
        self.assertEqual("memory", body["storage_mode"])

    def test_http_login_and_chat(self):
        login = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        self.assertEqual(200, login.status_code)
        token = login.json()["token"]

        chat = client.post("/api/chat", json={"token": token, "message": "你好"})
        self.assertEqual(200, chat.status_code)
        self.assertIn("answer", chat.json())

    def test_history_endpoint_returns_saved_message(self):
        login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        token = login.json()["token"]

        client.post("/api/chat", json={"token": token, "message": "毕业设计怎么开始"})
        history = client.get(f"/api/history?token={token}")

        self.assertEqual(200, history.status_code)
        self.assertEqual(1, len(history.json()["messages"]))
        self.assertIn("毕业设计怎么开始", history.json()["messages"][0]["user_message"])
        self.assertIn("title", history.json())
        self.assertTrue(history.json()["title"])

    def test_admin_can_read_logs_and_update_config(self):
        login = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        token = login.json()["token"]

        update = client.post(
            "/api/admin/config",
            json={
                "token": token,
                "config_key": "model_name",
                "config_value": "graduation-demo-model",
            },
        )
        self.assertEqual(200, update.status_code)
        self.assertEqual("graduation-demo-model", update.json()["model_name"])

        logs = client.get(f"/api/admin/logs?token={token}")
        self.assertEqual(200, logs.status_code)
        self.assertTrue(any(item["event_type"] == "config_update" for item in logs.json()["items"]))

    def test_student_cannot_read_admin_logs(self):
        login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        token = login.json()["token"]

        logs = client.get(f"/api/admin/logs?token={token}")
        self.assertEqual(403, logs.status_code)

    def test_admin_can_read_system_overview(self):
        student_login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        student_token = student_login.json()["token"]
        client.post(
            "/api/chat",
            json={"token": student_token, "message": "帮我概括一下毕业设计系统的目标"},
        )

        admin_login = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        admin_token = admin_login.json()["token"]
        overview = client.get(f"/api/admin/overview?token={admin_token}")

        self.assertEqual(200, overview.status_code)
        body = overview.json()
        self.assertIn("user_count", body)
        self.assertIn("session_count", body)
        self.assertIn("message_count", body)
        self.assertGreaterEqual(body["user_count"], 2)
        self.assertGreaterEqual(body["session_count"], 1)
        self.assertGreaterEqual(body["message_count"], 1)
