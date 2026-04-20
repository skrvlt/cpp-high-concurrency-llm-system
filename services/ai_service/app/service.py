from __future__ import annotations

import json
import os
import secrets
from typing import Dict
from urllib.request import Request, urlopen

from .models import ChatResponse, HistoryResponse, LogEntry, TokenState
from .repository import InMemoryRepository


class DemoModelClient:
    def answer(self, message: str, username: str, config: Dict[str, str]) -> str:
        remote_answer = self._try_remote_answer(message, username, config)
        if remote_answer:
            return remote_answer

        model_name = config.get("model_name", "demo-llm")
        return (
            f"[{model_name}] 已收到来自 {username} 的问题：{message}。"
            "这是第一版演示回答，后续可替换为真实大语言模型接口。"
        )

    def _try_remote_answer(
        self, message: str, username: str, config: Dict[str, str]
    ) -> str | None:
        api_url = os.getenv("LLM_API_URL", "").strip()
        api_key = os.getenv("LLM_API_KEY", "").strip()
        model_name = os.getenv("LLM_MODEL_NAME", config.get("model_name", "demo-llm"))
        if not api_url:
            return None

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个用于毕业设计演示的智能问答助手，请用简洁、专业的中文回答。",
                },
                {
                    "role": "user",
                    "content": f"用户 {username} 的问题是：{message}",
                },
            ],
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        request = Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
            return (
                body.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
                or None
            )
        except Exception:
            return None


class AppService:
    def __init__(self) -> None:
        self.repository = InMemoryRepository()
        self.tokens: Dict[str, TokenState] = {}
        self.model_client = DemoModelClient()

    def login(self, username: str, password: str) -> str:
        user = self.repository.get_user(username)
        if not user or user.password != password:
            self.repository.add_log(
                LogEntry(
                    level="WARN",
                    event_type="login_failed",
                    message=f"登录失败: {username}",
                )
            )
            raise ValueError("用户名或密码错误")

        session = self.repository.create_session(username=username, title="默认会话")
        token = secrets.token_hex(16)
        self.tokens[token] = TokenState(
            token=token, username=user.username, role=user.role, session_id=session.id
        )
        self.repository.add_log(
            LogEntry(
                level="INFO",
                event_type="login_success",
                message=f"用户 {username} 登录成功",
            )
        )
        return token

    def get_token_state(self, token: str) -> TokenState:
        state = self.tokens.get(token)
        if not state:
            raise ValueError("无效 token")
        return state

    def chat(self, token: str, message: str) -> ChatResponse:
        state = self.get_token_state(token)
        config = self.repository.get_config()
        answer = self.model_client.answer(message, state.username, config)
        session = self.repository.append_message(state.session_id, message, answer)
        self.repository.add_log(
            LogEntry(
                level="INFO",
                event_type="chat",
                message=f"用户 {state.username} 发起问答",
            )
        )
        return ChatResponse(
            session_id=session.id, answer=answer, history_size=len(session.entries)
        )

    def history(self, token: str) -> HistoryResponse:
        state = self.get_token_state(token)
        session = self.repository.get_session(state.session_id)
        return HistoryResponse(
            session_id=session.id,
            title=session.title,
            messages=[
                {
                    "user_message": item.user_message,
                    "assistant_message": item.assistant_message,
                    "created_at": item.created_at.isoformat(),
                }
                for item in session.entries
            ],
        )

    def logs(self, token: str):
        state = self.get_token_state(token)
        if state.role != "admin":
            raise PermissionError("仅管理员可查看日志")
        return [
            {
                "level": entry.level,
                "event_type": entry.event_type,
                "message": entry.message,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in self.repository.list_logs()
        ]

    def get_config(self, token: str) -> Dict[str, str]:
        state = self.get_token_state(token)
        if state.role != "admin":
            raise PermissionError("仅管理员可查看配置")
        return self.repository.get_config()

    def update_config(self, token: str, key: str, value: str) -> Dict[str, str]:
        state = self.get_token_state(token)
        if state.role != "admin":
            raise PermissionError("仅管理员可修改配置")
        updated = self.repository.update_config(key, value)
        self.repository.add_log(
            LogEntry(
                level="INFO",
                event_type="config_update",
                message=f"管理员 {state.username} 更新配置 {key}",
            )
        )
        return updated

    def overview(self, token: str) -> Dict[str, int | str]:
        state = self.get_token_state(token)
        if state.role != "admin":
            raise PermissionError("仅管理员可查看系统概览")

        sessions = self.repository.list_sessions()
        users = self.repository.list_users()
        logs = self.repository.list_logs()
        message_count = sum(len(session.entries) for session in sessions)
        active_users = len({session.username for session in sessions})
        return {
            "user_count": len(users),
            "active_user_count": active_users,
            "session_count": len(sessions),
            "message_count": message_count,
            "log_count": len(logs),
            "model_name": self.repository.get_config().get("model_name", "demo-llm"),
        }


service = AppService()
