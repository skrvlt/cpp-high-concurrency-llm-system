import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

from services.ai_service.app.service import (
    AppService,
    DemoModelClient,
    create_repository_from_env,
)
from services.ai_service.app.repository import SQLiteRepository


class ServiceTests(unittest.TestCase):
    def test_login_and_chat_flow(self):
        service = AppService()
        token = service.login("admin", "admin123")
        self.assertTrue(token)

        reply = service.chat(token, "测试问题")
        self.assertIn("测试问题", reply.answer)

        history = service.history(token)
        self.assertEqual(1, len(history))

    def test_demo_model_client_uses_remote_api_when_env_is_configured(self):
        client = DemoModelClient()
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"choices":[{"message":{"content":"\xe8\xbf\x9c\xe7\xa8\x8b\xe6\xa8\xa1\xe5\x9e\x8b\xe5\x9b\x9e\xe5\xa4\x8d"}}]}'
        )
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_response
        mock_context.__exit__.return_value = False

        with patch.dict(
            "os.environ",
            {
                "LLM_API_URL": "https://example.com/v1/chat/completions",
                "LLM_API_KEY": "demo-key",
                "LLM_MODEL_NAME": "demo-remote-model",
            },
            clear=False,
        ):
            with patch("services.ai_service.app.service.urlopen", return_value=mock_context):
                answer = client.answer("你好", "student", {"model_name": "local-model"})

        self.assertEqual("远程模型回复", answer)

    def test_sqlite_repository_persists_sessions_config_and_logs(self):
        db_dir = Path.cwd() / "tmp" / "test-data"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / f"service-{uuid4().hex}.sqlite3"
        service = AppService(repository=SQLiteRepository(db_path))

        student_token = service.login("student", "student123")
        reply = service.chat(student_token, "持久化测试")
        self.assertIn("持久化测试", reply.answer)

        admin_token = service.login("admin", "admin123")
        service.update_config(admin_token, "model_name", "persisted-model")

        restored = SQLiteRepository(db_path)
        sessions = restored.list_sessions()
        self.assertTrue(any(session.username == "student" for session in sessions))
        student_sessions = [
            session for session in sessions if session.username == "student"
        ]
        self.assertEqual(1, len(student_sessions[-1].entries))
        self.assertEqual("持久化测试", student_sessions[-1].entries[0].user_message)
        self.assertEqual("persisted-model", restored.get_config()["model_name"])
        self.assertTrue(
            any(log.event_type == "config_update" for log in restored.list_logs())
        )

    def test_health_reports_storage_mode(self):
        memory_service = AppService()
        self.assertEqual("memory", memory_service.health()["storage_mode"])

        db_path = Path.cwd() / "tmp" / "test-data" / f"health-{uuid4().hex}.sqlite3"
        sqlite_service = AppService(repository=SQLiteRepository(db_path))
        self.assertEqual("sqlite", sqlite_service.health()["storage_mode"])

    def test_create_repository_from_env_uses_sqlite_storage(self):
        db_path = Path.cwd() / "tmp" / "test-data" / f"env-{uuid4().hex}.sqlite3"
        with patch.dict(
            "os.environ",
            {
                "APP_STORAGE": "sqlite",
                "SQLITE_DB_PATH": str(db_path),
            },
            clear=False,
        ):
            repository = create_repository_from_env()

        self.assertIsInstance(repository, SQLiteRepository)
