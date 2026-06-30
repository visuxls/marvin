from fastapi import FastAPI

from .chat import router as chat_router
from .configure import router as configure_router
from .conversations import router as conversations_router
from .health import router as health_router

API_PREFIX = "/api"


def register_memory_routes(app: FastAPI) -> None:
    """
    Mount all chat-memory API routers on the application.

    Args:
        app: FastAPI application instance.
    """
    app.include_router(health_router, prefix=API_PREFIX)
    app.include_router(configure_router, prefix=API_PREFIX)
    app.include_router(chat_router, prefix=API_PREFIX)
    app.include_router(conversations_router, prefix=API_PREFIX)
