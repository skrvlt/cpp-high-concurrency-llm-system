import unittest

from services.ai_service.app.service import AppService


class ServiceTests(unittest.TestCase):
    def test_login_and_chat_flow(self):
        service = AppService()
        token = service.login("admin", "admin123")
        self.assertTrue(token)

        reply = service.chat(token, "测试问题")
        self.assertIn("测试问题", reply.answer)

        history = service.history(token)
        self.assertEqual(1, len(history))
