import unittest
from unittest.mock import MagicMock, patch

from services.ai_service.app.service import AppService, DemoModelClient


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
