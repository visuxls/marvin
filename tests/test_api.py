from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from starlette.responses import JSONResponse

from agent.deps import CFODeps
from agent.model import build_available_models
from config import Settings
from web.memory.routes import register_memory_routes
from web.memory.runtime import build_chat_runtime


def _build_api_app(agent, *, deps, models=None):
    app = FastAPI()
    app.state.chat_runtime = build_chat_runtime(agent=agent, models=models, deps=deps)
    register_memory_routes(app)
    return app


def test_health(api_app):
    client = TestClient(api_app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_configure(api_app):
    client = TestClient(api_app)
    response = client.get("/api/configure")
    assert response.status_code == 200
    assert "models" in response.json()


def test_configure_deduplicates_models(test_settings: Settings, monkeypatch):
    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)
    duplicate_model = TestModel()
    app = _build_api_app(
        agent,
        models={"Primary": duplicate_model, "Duplicate": duplicate_model},
        deps=CFODeps(
            db_path=test_settings.db_path,
            profile_path=test_settings.profile_path,
        ),
    )
    client = TestClient(app)
    response = client.get("/api/configure")
    model_ids = [model["id"] for model in response.json()["models"]]
    assert len(model_ids) == len(set(model_ids))


def test_configure_with_configured_models(test_settings: Settings, monkeypatch):
    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    test_settings.openrouter_models = [
        "GLM:z-ai/glm-5.2",
        "Claude:anthropic/claude-sonnet-4",
    ]
    agent = Agent(TestModel(), deps_type=CFODeps)
    app = _build_api_app(
        agent,
        models=build_available_models(test_settings),
        deps=CFODeps(
            db_path=test_settings.db_path,
            profile_path=test_settings.profile_path,
        ),
    )
    client = TestClient(app)
    response = client.get("/api/configure")
    models = response.json()["models"]
    assert [model["name"] for model in models] == ["GLM", "Claude"]


def test_configure_with_agent_without_default_model(test_settings: Settings, monkeypatch):
    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    agent = MagicMock()
    agent.model = None
    agent._cap_native_tools = []
    app = _build_api_app(
        agent,
        models=[TestModel()],
        deps=CFODeps(
            db_path=test_settings.db_path,
            profile_path=test_settings.profile_path,
        ),
    )
    client = TestClient(app)
    response = client.get("/api/configure")
    assert response.status_code == 200
    assert len(response.json()["models"]) == 1


def test_configure_without_models_or_agent_model(test_settings: Settings, monkeypatch):
    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    agent = MagicMock()
    agent.model = None
    agent._cap_native_tools = []
    app = _build_api_app(
        agent,
        deps=CFODeps(
            db_path=test_settings.db_path,
            profile_path=test_settings.profile_path,
        ),
    )
    client = TestClient(app)
    response = client.get("/api/configure")
    assert response.status_code == 200
    assert response.json()["models"] == []


def test_post_chat_validation_error(api_app):
    client = TestClient(api_app)
    with patch(
        "web.memory.routes.chat.VercelAIAdapter.from_request",
        side_effect=__import__("pydantic").ValidationError.from_exception_data(
            "ChatRequest",
            [{"type": "missing", "loc": ("messages",), "input": {}}],
        ),
    ):
        response = client.post("/api/chat", json={"messages": []})
    assert response.status_code == 422


def test_post_chat_invalid_request_options(api_app):
    adapter = MagicMock()
    adapter.run_input = MagicMock(__pydantic_extra__={"model": "missing-model"})

    with patch(
        "web.memory.routes.chat.VercelAIAdapter.from_request",
        new=AsyncMock(return_value=adapter),
    ):
        client = TestClient(api_app)
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )
    assert response.status_code == 400


def test_post_chat_dispatches_and_persists(test_settings: Settings, monkeypatch):
    from pydantic_ai.messages import ModelRequest, UserPromptPart

    from storage.conversation_memory import load_conversation_messages, save_conversation_messages

    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)
    app = _build_api_app(
        agent,
        deps=CFODeps(
            db_path=test_settings.db_path,
            profile_path=test_settings.profile_path,
        ),
    )

    stored = [ModelRequest(parts=[UserPromptPart(content="stored")])]
    save_conversation_messages("conv-1", stored, db_path=test_settings.db_path)

    captured = {}

    async def fake_dispatch(*args, **kwargs):
        captured["message_history"] = kwargs.get("message_history")

        class Result:
            def all_messages(self):
                return stored + [ModelRequest(parts=[UserPromptPart(content="new")])]

        await kwargs["on_complete"](Result())
        return JSONResponse({"ok": True})

    adapter = MagicMock()
    adapter.run_input = MagicMock(__pydantic_extra__={})
    adapter.dispatch_request = fake_dispatch

    with patch(
        "web.memory.routes.chat.VercelAIAdapter.from_request",
        new=AsyncMock(return_value=adapter),
    ):
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={
                "id": "conv-1",
                "messages": [
                    {
                        "id": "1",
                        "role": "user",
                        "parts": [{"type": "text", "text": "stored"}],
                    },
                    {
                        "id": "2",
                        "role": "user",
                        "parts": [{"type": "text", "text": "new"}],
                    },
                ],
            },
        )

    assert response.status_code == 200
    assert captured["message_history"] is not None
    loaded = load_conversation_messages("conv-1", db_path=test_settings.db_path)
    assert len(loaded) == 2


def test_post_chat_uses_client_history_when_longer(test_settings: Settings, monkeypatch):
    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)
    app = _build_api_app(
        agent,
        deps=CFODeps(
            db_path=test_settings.db_path,
            profile_path=test_settings.profile_path,
        ),
    )

    captured = {}

    async def fake_dispatch(*args, **kwargs):
        captured["message_history"] = kwargs.get("message_history")
        return JSONResponse({"ok": True})

    adapter = MagicMock()
    adapter.run_input = MagicMock(__pydantic_extra__={})
    adapter.dispatch_request = fake_dispatch

    with patch(
        "web.memory.routes.chat.VercelAIAdapter.from_request",
        new=AsyncMock(return_value=adapter),
    ):
        client = TestClient(app)
        client.post(
            "/api/chat",
            json={
                "id": "conv-2",
                "messages": [{"role": "user"}, {"role": "assistant"}],
            },
        )

    assert captured["message_history"] is None
