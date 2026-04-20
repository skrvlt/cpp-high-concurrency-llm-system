from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List

from pydantic import BaseModel, Field


@dataclass
class User:
    id: int
    username: str
    password: str
    role: str


@dataclass
class ChatEntry:
    user_message: str
    assistant_message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SessionState:
    id: int
    title: str
    username: str
    entries: List[ChatEntry] = field(default_factory=list)


@dataclass
class LogEntry:
    level: str
    event_type: str
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TokenState:
    token: str
    username: str
    role: str
    session_id: int


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str
    session_id: int


class ChatRequest(BaseModel):
    token: str
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    session_id: int
    answer: str
    history_size: int


class HistoryResponse(BaseModel):
    session_id: int
    title: str
    messages: List[Dict[str, str]]

    def __len__(self) -> int:
        return len(self.messages)


class ConfigUpdateRequest(BaseModel):
    token: str
    config_key: str
    config_value: str
