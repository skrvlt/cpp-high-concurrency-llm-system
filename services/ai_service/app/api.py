from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query

from .models import (
    ChatRequest,
    ConfigUpdateRequest,
    LoginRequest,
    LoginResponse,
)
from .service import service


router = APIRouter(prefix="/api")


def resolve_token(
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
) -> str:
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value.strip():
            return value.strip()
        raise ValueError("无效 Authorization 请求头")
    if token:
        return token
    raise ValueError("缺少 token")


@router.get("/health")
def health():
    return service.health()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    try:
        token = service.login(payload.username, payload.password)
        state = service.get_token_state(token)
        return LoginResponse(
            token=token,
            username=state.username,
            role=state.role,
            session_id=state.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/chat")
def chat(payload: ChatRequest):
    try:
        return service.chat(payload.token, payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/history")
def history(
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    try:
        token = resolve_token(token, authorization)
        return service.history(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/admin/logs")
def logs(
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    try:
        token = resolve_token(token, authorization)
        return {"items": service.logs(token)}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/admin/config")
def get_config(
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    try:
        token = resolve_token(token, authorization)
        return service.get_config(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/admin/overview")
def overview(
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    try:
        token = resolve_token(token, authorization)
        return service.overview(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/admin/config")
def update_config(payload: ConfigUpdateRequest):
    try:
        return service.update_config(payload.token, payload.config_key, payload.config_value)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
