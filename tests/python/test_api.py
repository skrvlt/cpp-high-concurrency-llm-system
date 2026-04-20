import unittest

from fastapi.testclient import TestClient

from services.ai_service.app.main import app


client = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_http_login_and_chat(self):
        login = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        self.assertEqual(200, login.status_code)
        token = login.json()["token"]

        chat = client.post("/api/chat", json={"token": token, "message": "你好"})
        self.assertEqual(200, chat.status_code)
        self.assertIn("answer", chat.json())
