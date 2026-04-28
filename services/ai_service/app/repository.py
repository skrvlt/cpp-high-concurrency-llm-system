from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional, Protocol

from .models import ChatEntry, LogEntry, SessionState, User


class Repository(Protocol):
    def storage_mode(self) -> str: ...

    def get_user(self, username: str) -> Optional[User]: ...

    def create_session(self, username: str, title: str) -> SessionState: ...

    def get_session(self, session_id: int) -> SessionState: ...

    def append_message(
        self, session_id: int, user_message: str, assistant_message: str
    ) -> SessionState: ...

    def add_log(self, entry: LogEntry) -> None: ...

    def list_logs(self) -> List[LogEntry]: ...

    def get_config(self) -> Dict[str, str]: ...

    def update_config(self, key: str, value: str) -> Dict[str, str]: ...

    def list_users(self) -> List[User]: ...

    def list_sessions(self) -> List[SessionState]: ...


DEFAULT_USERS = {
    "admin": User(id=1, username="admin", password="admin123", role="admin"),
    "student": User(id=2, username="student", password="student123", role="student"),
}

DEFAULT_CONFIG = {
    "model_name": "demo-llm",
    "gateway_timeout_ms": "5000",
    "history_window": "6",
}


class InMemoryRepository:
    def __init__(self) -> None:
        self.users: Dict[str, User] = dict(DEFAULT_USERS)
        self.sessions: Dict[int, SessionState] = {}
        self.logs: List[LogEntry] = []
        self.config: Dict[str, str] = dict(DEFAULT_CONFIG)
        self._session_counter = 1

    def storage_mode(self) -> str:
        return "memory"

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


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.now(UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


class SQLiteRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        if self.db_path != Path(":memory:"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._initialize_schema()
            self._seed_defaults()

    def storage_mode(self) -> str:
        return "sqlite"

    def _initialize_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_session (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_code TEXT NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            );

            CREATE TABLE IF NOT EXISTS chat_message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_session(id)
            );

            CREATE TABLE IF NOT EXISTS system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT NOT NULL UNIQUE,
                config_value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def _seed_defaults(self) -> None:
        now = datetime.now(UTC).isoformat()
        for user in DEFAULT_USERS.values():
            self._conn.execute(
                """
                INSERT INTO user (id, username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username) DO NOTHING
                """,
                (user.id, user.username, user.password, user.role, now),
            )
        for key, value in DEFAULT_CONFIG.items():
            self._conn.execute(
                """
                INSERT INTO system_config (config_key, config_value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(config_key) DO NOTHING
                """,
                (key, value, now),
            )
        self._conn.commit()

    def get_user(self, username: str) -> Optional[User]:
        with self._lock:
            row = self._conn.execute(
                "SELECT id, username, password_hash, role FROM user WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            return None
        return User(
            id=int(row["id"]),
            username=str(row["username"]),
            password=str(row["password_hash"]),
            role=str(row["role"]),
        )

    def create_session(self, username: str, title: str) -> SessionState:
        user = self.get_user(username)
        if user is None:
            raise KeyError(username)
        now = datetime.now(UTC).isoformat()
        with self._lock:
            cursor = self._conn.execute(
                """
                INSERT INTO chat_session (session_code, user_id, title, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (uuid.uuid4().hex, user.id, title, now),
            )
            self._conn.commit()
            session_id = int(cursor.lastrowid)
        return SessionState(id=session_id, title=title, username=username)

    def get_session(self, session_id: int) -> SessionState:
        with self._lock:
            session_row = self._conn.execute(
                """
                SELECT s.id, s.title, u.username
                FROM chat_session s
                JOIN user u ON u.id = s.user_id
                WHERE s.id = ?
                """,
                (session_id,),
            ).fetchone()
            if session_row is None:
                raise KeyError(session_id)
            message_rows = self._conn.execute(
                """
                SELECT user_message, assistant_message, created_at
                FROM chat_message
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        return SessionState(
            id=int(session_row["id"]),
            title=str(session_row["title"]),
            username=str(session_row["username"]),
            entries=[
                ChatEntry(
                    user_message=str(row["user_message"]),
                    assistant_message=str(row["assistant_message"]),
                    created_at=_parse_datetime(str(row["created_at"])),
                )
                for row in message_rows
            ],
        )

    def append_message(
        self, session_id: int, user_message: str, assistant_message: str
    ) -> SessionState:
        session = self.get_session(session_id)
        title = session.title
        with self._lock:
            if title == "默认会话":
                title = (user_message[:18] + "...") if len(user_message) > 18 else user_message
                self._conn.execute(
                    "UPDATE chat_session SET title = ? WHERE id = ?",
                    (title, session_id),
                )
            self._conn.execute(
                """
                INSERT INTO chat_message
                    (session_id, user_message, assistant_message, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_message,
                    assistant_message,
                    datetime.now(UTC).isoformat(),
                ),
            )
            self._conn.commit()
        return self.get_session(session_id)

    def add_log(self, entry: LogEntry) -> None:
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO system_log (level, event_type, message, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    entry.level,
                    entry.event_type,
                    entry.message,
                    entry.created_at.isoformat(),
                ),
            )
            self._conn.commit()

    def list_logs(self) -> List[LogEntry]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT level, event_type, message, created_at
                FROM system_log
                ORDER BY id ASC
                """
            ).fetchall()
        return [
            LogEntry(
                level=str(row["level"]),
                event_type=str(row["event_type"]),
                message=str(row["message"]),
                created_at=_parse_datetime(str(row["created_at"])),
            )
            for row in rows
        ]

    def get_config(self) -> Dict[str, str]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT config_key, config_value FROM system_config ORDER BY id ASC"
            ).fetchall()
        return {str(row["config_key"]): str(row["config_value"]) for row in rows}

    def update_config(self, key: str, value: str) -> Dict[str, str]:
        now = datetime.now(UTC).isoformat()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO system_config (config_key, config_value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(config_key) DO UPDATE SET
                    config_value = excluded.config_value,
                    updated_at = excluded.updated_at
                """,
                (key, value, now),
            )
            self._conn.commit()
        return self.get_config()

    def list_users(self) -> List[User]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, username, password_hash, role FROM user ORDER BY id ASC"
            ).fetchall()
        return [
            User(
                id=int(row["id"]),
                username=str(row["username"]),
                password=str(row["password_hash"]),
                role=str(row["role"]),
            )
            for row in rows
        ]

    def list_sessions(self) -> List[SessionState]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id FROM chat_session ORDER BY id ASC"
            ).fetchall()
        return [self.get_session(int(row["id"])) for row in rows]
