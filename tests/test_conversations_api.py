import pytest
from fastapi.testclient import TestClient

from storage.conversation_memory import save_conversation_messages
from tests.helpers import model_request


def test_list_conversations_route(api_app):
    client = TestClient(api_app)
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.json() == []


def test_conversation_routes_round_trip(api_app, db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    client = TestClient(api_app)

    listed = client.get("/api/conversations")
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "alpha"

    messages = client.get("/api/conversations/chat-a/messages")
    assert messages.status_code == 200
    assert len(messages.json()["messages"]) == 1

    patched = client.patch(
        "/api/conversations/chat-a",
        json={"pinned": True, "title": "Pinned alpha"},
    )
    assert patched.status_code == 200

    deleted = client.delete("/api/conversations/chat-a")
    assert deleted.status_code == 200
    assert client.get("/api/conversations").json() == []


def test_patch_conversation_invalid_json(api_app):
    client = TestClient(api_app)
    response = client.patch(
        "/api/conversations/missing",
        content=b"not-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_patch_conversation_non_object_json(api_app):
    client = TestClient(api_app)
    response = client.patch("/api/conversations/missing", json=[])
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("payload", "status_code"),
    [
        ({"title": 1}, 422),
        ({"pinned": "yes"}, 422),
        ({}, 400),
    ],
)
def test_patch_conversation_validation_errors(api_app, payload, status_code):
    client = TestClient(api_app)
    response = client.patch("/api/conversations/missing", json=payload)
    assert response.status_code == status_code
    if status_code == 400:
        assert response.json()["detail"] == {"error": "No updates provided"}


def test_patch_conversation_not_found(api_app):
    client = TestClient(api_app)
    response = client.patch("/api/conversations/missing", json={"title": "New"})
    assert response.status_code == 404


def test_delete_conversation_not_found(api_app):
    client = TestClient(api_app)
    response = client.delete("/api/conversations/missing")
    assert response.status_code == 404
