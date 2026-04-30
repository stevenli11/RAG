"""FastAPI application entrypoint for the RAG backend."""

from __future__ import annotations

from fastapi import FastAPI

from .routes_chat import router as chat_router
from .routes_chat_stream import router as chat_stream_router
from .routes_debug import router as debug_router
from .routes_session import router as session_router


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Backend API", version="0.1.0")
    app.include_router(chat_router)
    app.include_router(chat_stream_router)
    app.include_router(debug_router)
    app.include_router(session_router)

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
