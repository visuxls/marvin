"""
Helpers for reconciling client chat requests with persisted history.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, Literal

from fastapi import Request
from pydantic_ai.messages import ModelMessage
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from web.request import request_with_cached_body

VERCEL_AI_SDK_VERSION: Literal[6] = 6


def reconcile_chat_payload(
    payload: dict[str, Any],
    stored_messages: Sequence[ModelMessage],
    *,
    sdk_version: Literal[5, 6] = VERCEL_AI_SDK_VERSION,
) -> tuple[list[ModelMessage] | None, dict[str, Any]]:
    """
    Reconcile a chat request with persisted server history.

    Args:
        payload: Parsed Vercel AI chat request body.
        stored_messages: Messages persisted for the conversation.
        sdk_version: Vercel AI SDK version used by the frontend.

    Returns:
        Server history to pass to the agent (or ``None`` for regenerate and new
        conversations) and the payload with persisted client messages stripped when
        appending.
    """
    if not stored_messages:
        return None, payload

    trigger = payload.get("trigger", "submit-message")
    if trigger == "regenerate-message":
        return None, payload

    client_messages = payload.get("messages", [])
    stored_ui = VercelAIAdapter.dump_messages(stored_messages, sdk_version=sdk_version)
    new_messages = client_messages[len(stored_ui) :]
    stripped_payload = {**payload, "messages": new_messages}
    return list(stored_messages), stripped_payload


def request_with_payload(request: Request, payload: dict[str, Any]) -> Request:
    """
    Rebuild a request so downstream handlers see an updated JSON body.

    Args:
        request: Original incoming request.
        payload: Replacement JSON request body.

    Returns:
        Replayable request with the updated body.
    """
    body = json.dumps(payload).encode("utf-8")
    return request_with_cached_body(request, body)
