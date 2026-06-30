"""ASGI entry point for Marvin's FastAPI web application."""

from agent.deps import build_deps
from agent.initialize_agent import build_agent
from agent.model import build_available_models
from web.app import create_marvin_web_app

agent = build_agent()

app = create_marvin_web_app(
    agent,
    deps=build_deps(),
    models=build_available_models(),
)
