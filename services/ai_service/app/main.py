import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router


app = FastAPI(title="LLM Interaction System", version="1.0.0")


def cors_origins() -> list[str]:
    configured = os.getenv(
        "APP_CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
