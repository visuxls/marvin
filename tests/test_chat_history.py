import asyncio
import json

from tests.helpers import model_request
from web.chat_history import (
    VERCEL_AI_SDK_VERSION,
    reconcile_chat_payload,
    request_with_payload,
)


def _request_with_json(payload: dict):
    from starlette.requests import Request

    body = json.dumps(payload).encode("utf-8")

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/chat",
            "headers": [],
        },
        receive,
    )


def test_reconcile_chat_payload_uses_stored_tail():
    stored = [model_request("stored")]
    payload = {
        "trigger": "submit-message",
        "messages": [
            {"id": "1", "role": "user", "parts": [{"type": "text", "text": "stored"}]},
            {"id": "2", "role": "user", "parts": [{"type": "text", "text": "new"}]},
        ],
    }
    message_history, stripped = reconcile_chat_payload(
        payload,
        stored,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    assert message_history == stored
    assert len(stripped["messages"]) == 1
    assert stripped["messages"][0]["id"] == "2"


def test_reconcile_chat_payload_ignores_regenerate():
    stored = [model_request("stored")]
    payload = {
        "trigger": "regenerate-message",
        "messages": [{"id": "1", "role": "user", "parts": [{"type": "text", "text": "stored"}]}],
    }
    message_history, stripped = reconcile_chat_payload(
        payload,
        stored,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    assert message_history is None
    assert stripped == payload


def test_reconcile_chat_payload_without_stored_messages():
    payload = {"messages": [{"id": "1", "role": "user", "parts": []}]}
    message_history, stripped = reconcile_chat_payload(
        payload,
        [],
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    assert message_history is None
    assert stripped == payload


def test_reconcile_chat_payload_when_counts_match():
    stored = [model_request("stored")]
    payload = {
        "trigger": "submit-message",
        "messages": [
            {"id": "1", "role": "user", "parts": [{"type": "text", "text": "stored"}]},
        ],
    }
    message_history, stripped = reconcile_chat_payload(
        payload,
        stored,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    assert message_history == stored
    assert stripped["messages"] == []


def test_reconcile_chat_payload_with_stale_client_tab():
    stored = [
        model_request("first"),
        model_request("second"),
    ]
    payload = {
        "trigger": "submit-message",
        "messages": [
            {"id": "1", "role": "user", "parts": [{"type": "text", "text": "first"}]},
        ],
    }
    message_history, stripped = reconcile_chat_payload(
        payload,
        stored,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    assert message_history == stored
    assert stripped["messages"] == []


def test_request_with_payload_replays_body():
    request = _request_with_json({"messages": []})
    updated = request_with_payload(request, {"messages": [{"id": "1"}]})

    async def read_body() -> bytes:
        return await updated.body()

    body = asyncio.run(read_body())
    assert json.loads(body) == {"messages": [{"id": "1"}]}
