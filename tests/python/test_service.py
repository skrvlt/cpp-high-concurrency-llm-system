import asyncio
import unittest
from pathlib import Path
from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

from services.ai_service.app.service import (
    AppService,
    DemoModelClient,
    KnowledgeBase,
    create_repository_from_env,
    load_model_catalog,
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

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": "远程模型回复"}}]}

        class FakeAsyncClient:
            def __init__(self, *args, **kwargs):
                self.kwargs = kwargs

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

            async def post(self, url, json, headers):
                self.url = url
                self.payload = json
                self.headers = headers
                return FakeResponse()

        with patch.dict(
            "os.environ",
            {
                "LLM_API_URL": "https://example.com/v1/chat/completions",
                "LLM_API_KEY": "demo-key",
                "LLM_MODEL_NAME": "demo-remote-model",
            },
            clear=False,
        ):
            with patch(
                "services.ai_service.app.service.urlopen",
                side_effect=AssertionError("urlopen should not be used"),
                create=True,
            ):
                with patch("services.ai_service.app.service.httpx.AsyncClient", FakeAsyncClient):
                    answer = asyncio.run(client.answer_async("你好", "student", {"model_name": "local-model"}))

        self.assertEqual("远程模型回复", answer)

    def test_token_state_expires_and_is_cleaned_up(self):
        service = AppService()
        token = service.login("student", "student123")
        service.tokens[token].expires_at = datetime.now(UTC) - timedelta(seconds=1)

        with self.assertRaises(ValueError):
            service.get_token_state(token)

        self.assertNotIn(token, service.tokens)

    def test_overview_reports_configured_environment_model_name(self):
        service = AppService()
        token = service.login("admin", "admin123")

        with patch.dict("os.environ", {"LLM_MODEL_NAME": "deepseek-v4-flash"}, clear=False):
            overview = service.overview(token)

        self.assertEqual("deepseek-v4-flash", overview["model_name"])

    def test_demo_model_client_sync_wrapper_uses_async_remote_api(self):
        client = DemoModelClient()

        async def fake_answer(*args, **kwargs):
            return "async-wrapper-answer"

        with patch.object(client, "answer_async", side_effect=fake_answer):
            answer = client.answer("你好", "student", {"model_name": "local-model"})

        self.assertEqual("async-wrapper-answer", answer)

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

    def test_remote_model_failure_is_logged_as_fallback(self):
        class FailingAsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

            async def post(self, *args, **kwargs):
                raise TimeoutError("timeout")

        service = AppService()
        token = service.login("student", "student123")
        with patch.dict(
            "os.environ",
            {
                "LLM_API_URL": "https://example.invalid/v1/chat/completions",
                "LLM_API_KEY": "demo-key",
            },
            clear=False,
        ):
            with patch("services.ai_service.app.service.httpx.AsyncClient", FailingAsyncClient):
                reply = service.chat(token, "远程失败降级测试")

        self.assertIn("远程失败降级测试", reply.answer)
        self.assertTrue(
            any(log.event_type == "llm_remote_fallback" for log in service.repository.list_logs())
        )

    def test_knowledge_base_returns_matching_context(self):
        kb = KnowledgeBase(Path.cwd() / "knowledge_base")
        context = kb.search("Reactor 模式")

        self.assertIn("Reactor", context)

    def test_chat_uses_response_cache_for_repeated_question(self):
        class CountingClient:
            def __init__(self):
                self.calls = 0
                self.last_error = None
                self.last_provider = "counting"

            def answer(self, message, username, config, context="", provider=None, model=None):
                self.calls += 1
                return f"cached-answer-{self.calls}"

        service = AppService()
        service.model_client = CountingClient()
        token = service.login("student", "student123")

        first = service.chat(token, "缓存测试")
        second = service.chat(token, "缓存测试")

        self.assertEqual(first.answer, second.answer)
        self.assertEqual(1, service.model_client.calls)

    def test_model_catalog_contains_user_provided_models_without_secrets(self):
        catalog = load_model_catalog()
        names = {item.model for item in catalog}

        self.assertIn("deepseek-v4-pro", names)
        self.assertIn("deepseek-v4-flash", names)
        self.assertIn("mimo-v2.5-pro", names)
        self.assertIn("mimo-v2.5", names)
        serialized = str([item.__dict__ for item in catalog])
        self.assertNotIn("sk-", serialized)
        self.assertNotIn("tp-", serialized)
        self.assertIn("context_window", serialized)
        self.assertIn("max_output_tokens", serialized)

    def test_collaboration_runs_each_participant_and_combines_answers(self):
        class EchoClient:
            def __init__(self):
                self.last_error = None

            def answer(
                self,
                message,
                username,
                config,
                context="",
                provider=None,
                model=None,
            ):
                return f"{provider.name}:{model.model}:{message}"

        service = AppService()
        service.model_client = EchoClient()
        token = service.login("student", "student123")

        result = service.collaborate(
            token,
            "协作问题",
            [
                {"provider": "deepseek", "model": "deepseek-v4-pro"},
                {"provider": "mimo", "model": "mimo-v2.5"},
            ],
        )

        self.assertEqual(2, len(result["rounds"]))
        self.assertIn("deepseek-v4-pro", result["final_answer"])
        self.assertIn("mimo-v2.5", result["final_answer"])

    def test_cached_answer_does_not_log_remote_fallback_again(self):
        class FailingAsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

            async def post(self, *args, **kwargs):
                raise TimeoutError("timeout")

        service = AppService()
        token = service.login("student", "student123")
        with patch.dict(
            "os.environ",
            {
                "LLM_API_URL": "https://example.invalid/v1/chat/completions",
                "LLM_API_KEY": "demo-key",
            },
            clear=False,
        ):
            with patch("services.ai_service.app.service.httpx.AsyncClient", FailingAsyncClient):
                service.chat(token, "缓存后的降级日志测试")
                service.chat(token, "缓存后的降级日志测试")

        fallback_logs = [
            log
            for log in service.repository.list_logs()
            if log.event_type == "llm_remote_fallback"
        ]
        self.assertEqual(1, len(fallback_logs))
