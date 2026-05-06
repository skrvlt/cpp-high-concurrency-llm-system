import unittest
from pathlib import Path

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

    def test_cors_origin_policy_is_configurable(self):
        main_source = Path.cwd() / "services" / "ai_service" / "app" / "main.py"
        text = main_source.read_text(encoding="utf-8")
        self.assertIn("APP_CORS_ORIGINS", text)
        self.assertNotIn('allow_origins=["*"]', text)

    def test_http_login_and_chat(self):
        login = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        self.assertEqual(200, login.status_code)
        token = login.json()["token"]

        chat = client.post(
            "/api/chat",
            json={
                "token": token,
                "message": "你好",
                "provider": "deepseek",
                "model": "deepseek-v4-flash",
            },
        )
        self.assertEqual(200, chat.status_code)
        self.assertIn("answer", chat.json())
        self.assertEqual("deepseek", chat.json()["provider"])
        self.assertEqual("deepseek-v4-flash", chat.json()["model"])

    def test_models_endpoint_exposes_switchable_models_without_keys(self):
        models = client.get("/api/models")

        self.assertEqual(200, models.status_code)
        body = models.json()
        self.assertIn("items", body)
        names = {item["model"] for item in body["items"]}
        self.assertIn("deepseek-v4-pro", names)
        self.assertIn("deepseek-v4-flash", names)
        self.assertIn("mimo-v2.5-pro", names)
        self.assertIn("mimo-v2.5", names)
        serialized = str(body)
        self.assertNotIn("api_key", serialized.lower())
        self.assertNotIn("sk-", serialized)
        self.assertNotIn("tp-", serialized)

    def test_chat_collaboration_returns_model_answers_and_final_answer(self):
        login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        token = login.json()["token"]

        response = client.post(
            "/api/chat/collaborate",
            json={
                "token": token,
                "message": "多模型协作测试",
                "participants": [
                    {"provider": "deepseek", "model": "deepseek-v4-pro"},
                    {"provider": "mimo", "model": "mimo-v2.5"},
                ],
            },
        )

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertIn("final_answer", body)
        self.assertEqual(2, len(body["rounds"]))
        self.assertEqual("deepseek", body["rounds"][0]["provider"])
        self.assertEqual("mimo", body["rounds"][1]["provider"])
        self.assertIn("多模型协作测试", body["final_answer"])

    def test_chat_stream_endpoint_returns_text_event_stream(self):
        login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        token = login.json()["token"]

        with client.stream(
            "POST",
            "/api/chat/stream",
            json={"token": token, "message": "流式输出测试"},
        ) as response:
            body = "".join(response.iter_text())

        self.assertEqual(200, response.status_code)
        self.assertIn("text/event-stream", response.headers["content-type"])
        self.assertIn("data:", body)
        self.assertIn("[DONE]", body)

    def test_history_endpoint_returns_saved_message(self):
        login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        token = login.json()["token"]

        client.post("/api/chat", json={"token": token, "message": "毕业设计怎么开始"})
        history = client.get("/api/history", headers={"Authorization": f"Bearer {token}"})

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

        logs = client.get(
            "/api/admin/logs", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(200, logs.status_code)
        self.assertTrue(any(item["event_type"] == "config_update" for item in logs.json()["items"]))

    def test_student_cannot_read_admin_logs(self):
        login = client.post(
            "/api/login", json={"username": "student", "password": "student123"}
        )
        token = login.json()["token"]

        logs = client.get(
            "/api/admin/logs", headers={"Authorization": f"Bearer {token}"}
        )
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
        overview = client.get(
            "/api/admin/overview", headers={"Authorization": f"Bearer {admin_token}"}
        )

        self.assertEqual(200, overview.status_code)
        body = overview.json()
        self.assertIn("user_count", body)
        self.assertIn("session_count", body)
        self.assertIn("message_count", body)
        self.assertGreaterEqual(body["user_count"], 2)
        self.assertGreaterEqual(body["session_count"], 1)
        self.assertGreaterEqual(body["message_count"], 1)

    def test_admin_can_read_model_providers(self):
        admin_login = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        token = admin_login.json()["token"]
        providers = client.get(
            "/api/admin/model-providers",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(200, providers.status_code)
        body = providers.json()
        self.assertIn("items", body)
        self.assertTrue(any(item["name"] == "deepseek" for item in body["items"]))
