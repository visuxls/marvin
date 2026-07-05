import asyncio
import json

from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from tests.helpers import model_request
from web.chat_history import (
    VERCEL_AI_SDK_VERSION,
    _extract_new_client_messages,
    _stored_user_texts,
    _user_message_text,
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


def test_reconcile_chat_payload_with_merged_client_assistants():
    stored = [
        model_request("What are my holdings?"),
        ModelResponse(
            parts=[
                ThinkingPart(content="Need holdings."),
                ToolCallPart(tool_name="get_holdings", args={}, tool_call_id="call-1"),
            ]
        ),
        ModelRequest(
            parts=[ToolReturnPart(tool_name="get_holdings", content=[], tool_call_id="call-1")]
        ),
        ModelResponse(parts=[TextPart(content="Here are your holdings.")]),
    ]
    stored_ui = VercelAIAdapter.dump_messages(stored, sdk_version=VERCEL_AI_SDK_VERSION)
    stored_ui_json = [message.model_dump(mode="json", by_alias=True) for message in stored_ui]
    merged_assistant = {
        "id": "live-assistant",
        "role": "assistant",
        "parts": [
            *stored_ui_json[1]["parts"],
            *stored_ui_json[2]["parts"],
        ],
    }
    payload = {
        "trigger": "submit-message",
        "messages": [
            stored_ui_json[0],
            merged_assistant,
            {
                "id": "new-user",
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Is there any stocks I should sell to pivot into something else?",
                    }
                ],
            },
        ],
    }

    message_history, stripped = reconcile_chat_payload(
        payload,
        stored,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )

    assert message_history == stored
    assert len(stripped["messages"]) == 1
    assert stripped["messages"][0]["id"] == "new-user"


def test_user_message_text_returns_empty_for_non_user():
    assert _user_message_text({"role": "assistant", "parts": []}) == ""


def test_stored_user_texts_skips_non_text_parts():
    class Part:
        type = "file"

    class BlankTextPart:
        type = "text"
        text = "   "

    class Message:
        role = "user"
        parts = [Part(), BlankTextPart()]

    assert _stored_user_texts([Message()]) == set()


def test_extract_new_client_messages_with_empty_client():
    assert _extract_new_client_messages([], []) == []


def test_reconcile_chat_payload_with_empty_client_messages():
    stored = [model_request("stored")]
    payload = {"trigger": "submit-message", "messages": []}
    message_history, stripped = reconcile_chat_payload(
        payload,
        stored,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    assert message_history == stored
    assert stripped["messages"] == []


def test_reconcile_chat_payload_when_last_client_message_is_assistant():
    stored = [model_request("stored"), ModelResponse(parts=[TextPart(content="done")])]
    stored_ui = VercelAIAdapter.dump_messages(stored, sdk_version=VERCEL_AI_SDK_VERSION)
    payload = {
        "trigger": "submit-message",
        "messages": [message.model_dump(mode="json", by_alias=True) for message in stored_ui],
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
