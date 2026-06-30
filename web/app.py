from pathlib import Path
from typing import TypeVar

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.ui._web.api import ModelsParam  # private API

from config import get_settings
from web.lifespan import lifespan
from web.memory.routes import register_memory_routes
from web.memory.runtime import build_chat_runtime
from web.routes.ui import router as ui_router

AgentDepsT = TypeVar("AgentDepsT")
OutputDataT = TypeVar("OutputDataT")


def create_marvin_web_app(
    agent: Agent[AgentDepsT, OutputDataT],
    *,
    models: ModelsParam = None,
    deps=None,
    model_settings: ModelSettings | None = None,
    instructions: str | None = None,
    html_source: str | Path | None = None,
) -> FastAPI:
    """
    Create Marvin's web app with chat UI and persisted conversation memory.

    Args:
        agent: Marvin agent instance.
        models: Optional additional models for the UI.
        deps: Dependencies injected into each agent run.
        model_settings: Optional per-request model settings.
        instructions: Optional per-request instructions.
        html_source: Optional override for the chat UI HTML source.

    Returns:
        FastAPI application serving the chat UI and API.
    """
    app = FastAPI(lifespan=lifespan)

    app.state.chat_runtime = build_chat_runtime(
        agent,
        models=models,
        deps=deps,
        model_settings=model_settings,
        instructions=instructions,
    )
    app.state.html_source = html_source

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ui_router)
    register_memory_routes(app)
    return app
