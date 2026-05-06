from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from urllib.request import Request, urlopen

from .models import ChatResponse, HistoryResponse, LogEntry, TokenState
from .repository import InMemoryRepository, Repository, SQLiteRepository


DEFAULT_MODEL_PROVIDERS = [
    {
        "name": "deepseek",
        "api_url": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-v4-flash",
        "enabled": True,
    },
    {
        "name": "openai_compatible",
        "api_url": "",
        "model": "",
        "enabled": False,
    },
]


@dataclass
class ModelProvider:
    name: str
    api_url: str
    model: str
    enabled: bool = True


class KnowledgeBase:
    def __init__(self, root: str | Path = "knowledge_base") -> None:
        self.root = Path(root)

    def search(self, query: str, limit: int = 2) -> str:
        if not self.root.exists():
            return ""
        terms = [term.lower() for term in query.split() if term.strip()]
        if not terms:
            terms = [query.lower()]

        matches: list[tuple[int, str]] = []
        for path in self.root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            score = sum(lowered.count(term) for term in terms)
            if score == 0 and any(ch in text for ch in query[:12]):
                score = 1
            if score:
                snippet = text.strip().replace("\n", " ")[:240]
                matches.append((score, f"{path.name}: {snippet}"))

        matches.sort(key=lambda item: item[0], reverse=True)
        return "\n".join(snippet for _, snippet in matches[:limit])


def load_model_providers() -> list[ModelProvider]:
    configured = os.getenv("LLM_PROVIDERS_JSON", "").strip()
    if configured:
        try:
            raw_items = json.loads(configured)
            return [
                ModelProvider(
                    name=str(item.get("name", "provider")),
                    api_url=str(item.get("api_url", "")),
                    model=str(item.get("model", "")),
                    enabled=bool(item.get("enabled", True)),
                )
                for item in raw_items
            ]
        except Exception:
            pass

    return [
        ModelProvider(
            name=str(item["name"]),
            api_url=str(item["api_url"]),
            model=str(item["model"]),
            enabled=bool(item["enabled"]),
        )
        for item in DEFAULT_MODEL_PROVIDERS
    ]


class DemoModelClient:
    def __init__(self) -> None:
        self.last_error: str | None = None
        self.last_provider = "demo"

    def answer(
        self, message: str, username: str, config: Dict[str, str], context: str = ""
    ) -> str:
        self.last_error = None
        remote_answer = self._try_remote_answer(message, username, config, context)
        if remote_answer:
            return remote_answer

        model_name = config.get("model_name", "demo-llm")
        context_text = f"参考资料命中：{context}。" if context else ""
        return (
            f"[{model_name}] 已收到来自 {username} 的问题：{message}。"
            f"{context_text}"
            "这是第一版演示回答，后续可替换为真实大语言模型接口。"
        )

    def _try_remote_answer(
        self, message: str, username: str, config: Dict[str, str], context: str
    ) -> str | None:
        api_url = os.getenv("LLM_API_URL", "").strip() or config.get("llm_api_url", "")
        api_key = os.getenv("LLM_API_KEY", "").strip()
        model_name = os.getenv("LLM_MODEL_NAME", config.get("model_name", "demo-llm"))
        if not api_url:
            return None
        self.last_provider = os.getenv("LLM_PROVIDER", "openai_compatible")

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一个用于毕业设计演示的智能问答助手，请用简洁、专业的中文回答。"
                        f"可参考资料：{context}" if context else
                        "你是一个用于毕业设计演示的智能问答助手，请用简洁、专业的中文回答。"
                    ),
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
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            return None


def create_repository_from_env() -> Repository:
    storage = os.getenv("APP_STORAGE", "memory").strip().lower()
    if storage == "sqlite":
        db_path = os.getenv("SQLITE_DB_PATH", "runtime_data/app.sqlite3")
        return SQLiteRepository(db_path)
    return InMemoryRepository()


class AppService:
    def __init__(self, repository: Repository | None = None) -> None:
        self.repository = repository or create_repository_from_env()
        self.tokens: Dict[str, TokenState] = {}
        self.model_client = DemoModelClient()
        self.knowledge_base = KnowledgeBase()
        self.response_cache: Dict[str, str] = {}

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
        context = self.knowledge_base.search(message)
        cache_key = f"{state.username}|{config.get('model_name', 'demo-llm')}|{message}|{context}"
        if cache_key in self.response_cache:
            answer = self.response_cache[cache_key]
            used_cache = True
        else:
            answer = self.model_client.answer(message, state.username, config, context)
            self.response_cache[cache_key] = answer
            used_cache = False
        if not used_cache and getattr(self.model_client, "last_error", None):
            self.repository.add_log(
                LogEntry(
                    level="WARN",
                    event_type="llm_remote_fallback",
                    message=f"远程模型调用失败，已降级到演示模式: {self.model_client.last_error}",
                )
            )
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

    def model_providers(self, token: str):
        state = self.get_token_state(token)
        if state.role != "admin":
            raise PermissionError("仅管理员可查看模型配置")
        providers = load_model_providers()
        return [
            {
                "name": provider.name,
                "api_url": provider.api_url,
                "model": provider.model,
                "enabled": provider.enabled,
            }
            for provider in providers
        ]

    def health(self) -> Dict[str, int | str]:
        config = self.repository.get_config()
        runtime_mode = "remote" if os.getenv("LLM_API_URL", "").strip() else "demo"
        return {
            "status": "ok",
            "service": "ai_service",
            "runtime_mode": runtime_mode,
            "storage_mode": self.repository.storage_mode(),
            "model_name": os.getenv(
                "LLM_MODEL_NAME", config.get("model_name", "demo-llm")
            ),
            "provider_count": len([p for p in load_model_providers() if p.enabled]),
            "session_count": len(self.repository.list_sessions()),
        }


service = AppService()
