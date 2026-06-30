from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from agent.deps import CFODeps, build_deps
from config import Settings
from web.app import create_marvin_web_app


@pytest.fixture
def web_app(test_settings: Settings, monkeypatch):
    monkeypatch.setattr("web.app.get_settings", lambda: test_settings)
    monkeypatch.setattr("web.lifespan.get_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)
    return create_marvin_web_app(agent, deps=build_deps(test_settings))


def test_index_route_returns_html(web_app):
    client = TestClient(web_app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_index_route_with_conversation_id(web_app):
    client = TestClient(web_app)
    response = client.get("/thread-1")
    assert response.status_code == 200


def test_lifespan_runs_import_when_enabled(test_settings: Settings, monkeypatch):
    test_settings.auto_import_on_startup = True
    monkeypatch.setattr("web.app.get_settings", lambda: test_settings)
    monkeypatch.setattr("web.lifespan.get_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)

    with (
        patch("web.lifespan.ensure_demo_data", return_value=[]) as seed_mock,
        patch("web.lifespan.import_all", return_value=[]) as import_mock,
        patch("web.lifespan.log_import_results") as log_mock,
        TestClient(create_marvin_web_app(agent, deps=build_deps(test_settings))),
    ):
        seed_mock.assert_called_once()
        import_mock.assert_called_once()
        log_mock.assert_called_once()


def test_lifespan_skips_import_when_disabled(test_settings: Settings, monkeypatch):
    test_settings.auto_import_on_startup = False
    monkeypatch.setattr("web.app.get_settings", lambda: test_settings)
    monkeypatch.setattr("web.lifespan.get_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)

    with (
        patch("web.lifespan.ensure_demo_data", return_value=[]) as seed_mock,
        patch("web.lifespan.import_all") as import_mock,
        TestClient(create_marvin_web_app(agent, deps=build_deps(test_settings))),
    ):
        seed_mock.assert_called_once()
        import_mock.assert_not_called()


def test_cors_allows_frontend_origin(web_app):
    client = TestClient(web_app)
    response = client.options(
        "/api/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
