from __future__ import annotations

from typing import Dict, List, Optional

from .models import ChatEntry, LogEntry, SessionState, User


class InMemoryRepository:
    def __init__(self) -> None:
        self.users: Dict[str, User] = {
            "admin": User(id=1, username="admin", password="admin123", role="admin"),
            "student": User(
                id=2, username="student", password="student123", role="student"
            ),
        }
        self.sessions: Dict[int, SessionState] = {}
        self.logs: List[LogEntry] = []
        self.config: Dict[str, str] = {
            "model_name": "demo-llm",
            "gateway_timeout_ms": "5000",
            "history_window": "6",
        }
        self._session_counter = 1

    def get_user(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def create_session(self, username: str, title: str) -> SessionState:
        session = SessionState(id=self._session_counter, title=title, username=username)
        self.sessions[session.id] = session
        self._session_counter += 1
        return session

    def get_session(self, session_id: int) -> SessionState:
        return self.sessions[session_id]

    def append_message(
        self, session_id: int, user_message: str, assistant_message: str
    ) -> SessionState:
        session = self.get_session(session_id)
        if session.title == "默认会话":
            session.title = (user_message[:18] + "...") if len(user_message) > 18 else user_message
        session.entries.append(
            ChatEntry(
                user_message=user_message,
                assistant_message=assistant_message,
            )
        )
        return session

    def add_log(self, entry: LogEntry) -> None:
        self.logs.append(entry)

    def list_logs(self) -> List[LogEntry]:
        return list(self.logs)

    def get_config(self) -> Dict[str, str]:
        return dict(self.config)

    def update_config(self, key: str, value: str) -> Dict[str, str]:
        self.config[key] = value
        return self.get_config()

    def list_users(self) -> List[User]:
        return list(self.users.values())

    def list_sessions(self) -> List[SessionState]:
        return list(self.sessions.values())
