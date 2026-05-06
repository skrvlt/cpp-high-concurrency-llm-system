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


def load_local_env(path: str | Path = ".env.local") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_env()


DEFAULT_MODEL_PROVIDERS = [
    {
        "name": "deepseek",
        "display_name": "DeepSeek",
        "api_url": "https://api.deepseek.com/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
        "enabled": True,
    },
    {
        "name": "mimo",
        "display_name": "MiMo (小米)",
        "api_url": "https://api.xiaomimimo.com/v1/chat/completions",
        "api_key_env": "MIMO_API_KEY",
        "api_key_fallback_env": "XIAOMI_API_KEY",
        "enabled": True,
    },
]

DEFAULT_MODEL_CATALOG = [
    {
        "provider": "deepseek",
        "model": "deepseek-v4-pro",
        "alias": "DS-Pro",
        "context_window": 1_000_000,
        "max_output_tokens": 65_536,
        "enabled": True,
    },
    {
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "alias": "DS-Flash",
        "context_window": 1_000_000,
        "max_output_tokens": 65_536,
        "enabled": True,
    },
    {
        "provider": "mimo",
        "model": "mimo-v2.5-pro",
        "alias": "MiMo-Pro",
        "context_window": 1_000_000,
        "max_output_tokens": 65_536,
        "enabled": True,
    },
    {
        "provider": "mimo",
        "model": "mimo-v2.5",
        "alias": "MiMo",
        "context_window": 1_000_000,
        "max_output_tokens": 65_536,
        "enabled": True,
    },
]


@dataclass
class ModelProvider:
    name: str
    api_url: str
    display_name: str
    api_key_env: str
    api_key_fallback_env: str = ""
    enabled: bool = True


@dataclass
class ModelCatalogItem:
    provider: str
    model: str
    alias: str
    context_window: int
    max_output_tokens: int
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
                    display_name=str(item.get("display_name", item.get("name", "provider"))),
                    api_key_env=str(item.get("api_key_env", "")),
                    api_key_fallback_env=str(item.get("api_key_fallback_env", "")),
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
            display_name=str(item["display_name"]),
            api_key_env=str(item["api_key_env"]),
            api_key_fallback_env=str(item.get("api_key_fallback_env", "")),
            enabled=bool(item["enabled"]),
        )
        for item in DEFAULT_MODEL_PROVIDERS
    ]


def load_model_catalog() -> list[ModelCatalogItem]:
    configured = os.getenv("LLM_MODELS_JSON", "").strip()
    if configured:
        try:
            raw_items = json.loads(configured)
            return [
                ModelCatalogItem(
                    provider=str(item.get("provider", "")),
                    model=str(item.get("model", "")),
                    alias=str(item.get("alias", item.get("model", ""))),
                    context_window=int(item.get("context_window", 0)),
                    max_output_tokens=int(item.get("max_output_tokens", 0)),
                    enabled=bool(item.get("enabled", True)),
                )
                for item in raw_items
            ]
        except Exception:
            pass

    return [
        ModelCatalogItem(
            provider=str(item["provider"]),
            model=str(item["model"]),
            alias=str(item["alias"]),
            context_window=int(item["context_window"]),
            max_output_tokens=int(item["max_output_tokens"]),
            enabled=bool(item["enabled"]),
        )
        for item in DEFAULT_MODEL_CATALOG
    ]


def resolve_provider(name: str | None) -> ModelProvider:
    providers = [provider for provider in load_model_providers() if provider.enabled]
    if name:
        for provider in providers:
            if provider.name == name:
                return provider
        raise ValueError(f"未知模型供应商: {name}")
    return providers[0]


def resolve_model(provider_name: str, model_name: str | None) -> ModelCatalogItem:
    models = [
        item
        for item in load_model_catalog()
        if item.enabled and item.provider == provider_name
    ]
    if model_name:
        for item in models:
            if item.model == model_name:
                return item
        raise ValueError(f"未知模型: {provider_name}/{model_name}")
    if not models:
        raise ValueError(f"模型供应商没有可用模型: {provider_name}")
    return models[0]


class DemoModelClient:
    def __init__(self) -> None:
        self.last_error: str | None = None
        self.last_provider = "demo"

    def answer(
        self,
        message: str,
        username: str,
        config: Dict[str, str],
        context: str = "",
        provider: ModelProvider | None = None,
        model: ModelCatalogItem | None = None,
    ) -> str:
        self.last_error = None
        remote_answer = self._try_remote_answer(
            message, username, config, context, provider, model
        )
        if remote_answer:
            return remote_answer

        model_name = model.model if model else config.get("model_name", "demo-llm")
        context_text = f"参考资料命中：{context}。" if context else ""
        return (
            f"[{model_name}] 已收到来自 {username} 的问题：{message}。"
            f"{context_text}"
            "这是第一版演示回答，后续可替换为真实大语言模型接口。"
        )

    def _try_remote_answer(
        self,
        message: str,
        username: str,
        config: Dict[str, str],
        context: str,
        provider: ModelProvider | None,
        model: ModelCatalogItem | None,
    ) -> str | None:
        api_url = (
            provider.api_url
            if provider
            else os.getenv("LLM_API_URL", "").strip() or config.get("llm_api_url", "")
        )
        api_key = ""
        if provider:
            api_key = os.getenv(provider.api_key_env, "").strip()
            if not api_key and provider.api_key_fallback_env:
                api_key = os.getenv(provider.api_key_fallback_env, "").strip()
            if not api_key:
                api_key = os.getenv("LLM_API_KEY", "").strip()
        else:
            api_key = os.getenv("LLM_API_KEY", "").strip()
        model_name = (
            model.model
            if model
            else os.getenv("LLM_MODEL_NAME", config.get("model_name", "demo-llm"))
        )
        if not api_url:
            return None
        self.last_provider = provider.name if provider else os.getenv(
            "LLM_PROVIDER", "openai_compatible"
        )
        if not api_key:
            return None

        system_prompt = "你是一个用于毕业设计演示的智能问答助手，请用简洁、专业的中文回答。"
        if context:
            system_prompt = f"{system_prompt} 可参考资料：{context}"

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"用户 {username} 的问题是：{message}",
                },
            ],
            "max_tokens": model.max_output_tokens if model else 2048,
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

    def chat(
        self, token: str, message: str, provider_name: str | None = None, model_name: str | None = None
    ) -> ChatResponse:
        state = self.get_token_state(token)
        config = self.repository.get_config()
        provider = resolve_provider(provider_name or os.getenv("LLM_PROVIDER", "deepseek"))
        model = resolve_model(
            provider.name,
            model_name or os.getenv("LLM_MODEL_NAME", ""),
        )
        context = self.knowledge_base.search(message)
        cache_key = f"{state.username}|{provider.name}|{model.model}|{message}|{context}"
        if cache_key in self.response_cache:
            answer = self.response_cache[cache_key]
            used_cache = True
        else:
            answer = self.model_client.answer(
                message, state.username, config, context, provider, model
            )
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
            session_id=session.id,
            answer=answer,
            history_size=len(session.entries),
            provider=provider.name,
            model=model.model,
        )

    def models(self):
        providers = {provider.name: provider for provider in load_model_providers()}
        return [
            {
                "provider": item.provider,
                "provider_name": providers.get(item.provider).display_name
                if providers.get(item.provider)
                else item.provider,
                "model": item.model,
                "alias": item.alias,
                "context_window": item.context_window,
                "max_output_tokens": item.max_output_tokens,
                "enabled": item.enabled and providers.get(item.provider, None) is not None,
            }
            for item in load_model_catalog()
        ]

    def collaborate(self, token: str, message: str, participants: list[dict[str, str]]):
        state = self.get_token_state(token)
        config = self.repository.get_config()
        context = self.knowledge_base.search(message)
        selected = participants or [
            {"provider": "deepseek", "model": "deepseek-v4-pro"},
            {"provider": "mimo", "model": "mimo-v2.5"},
        ]

        rounds = []
        prior_answers = ""
        for index, participant in enumerate(selected, start=1):
            provider = resolve_provider(participant.get("provider"))
            model = resolve_model(provider.name, participant.get("model"))
            prompt = message
            if prior_answers:
                prompt = (
                    f"用户原问题：{message}\n"
                    f"其他模型已有回答：{prior_answers}\n"
                    "请你指出可以补充或修正的地方，并给出自己的答案。"
                )
            answer = self.model_client.answer(
                prompt, state.username, config, context, provider, model
            )
            if getattr(self.model_client, "last_error", None):
                self.repository.add_log(
                    LogEntry(
                        level="WARN",
                        event_type="llm_remote_fallback",
                        message=(
                            f"{provider.name}/{model.model} 远程模型调用失败，"
                            f"已降级到演示模式: {self.model_client.last_error}"
                        ),
                    )
                )
            rounds.append(
                {
                    "round": index,
                    "provider": provider.name,
                    "model": model.model,
                    "answer": answer,
                }
            )
            prior_answers = f"{prior_answers}\n[{provider.name}/{model.model}] {answer}".strip()

        final_answer = (
            f"多模型协作结果：针对“{message}”，系统综合 "
            f"{len(rounds)} 个模型的回答后得到以下结论。\n"
            f"{prior_answers}"
        )
        session = self.repository.append_message(state.session_id, message, final_answer)
        self.repository.add_log(
            LogEntry(
                level="INFO",
                event_type="model_collaboration",
                message=f"用户 {state.username} 发起多模型协作问答",
            )
        )
        return {
            "session_id": session.id,
            "final_answer": final_answer,
            "rounds": rounds,
            "history_size": len(session.entries),
        }

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
                "display_name": provider.display_name,
                "api_key_env": provider.api_key_env,
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
