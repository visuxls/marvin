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


def _user_message_text(message: dict[str, Any]) -> str:
    """
    Extract trimmed text from a Vercel AI user message.

    Args:
        message: UI message from the chat client.

    Returns:
        Combined user text, or an empty string when none exists.
    """
    if message.get("role") != "user":
        return ""

    parts: list[dict[str, Any]] = message.get("parts", [])
    chunks = [
        str(part.get("text", "")).strip()
        for part in parts
        if part.get("type") == "text" and str(part.get("text", "")).strip()
    ]
    return "\n".join(chunks)


def _stored_user_texts(stored_ui: Sequence[object]) -> set[str]:
    """
    Collect user prompt text already present in persisted UI history.

    Args:
        stored_ui: UI messages produced by ``VercelAIAdapter.dump_messages``.

    Returns:
        Trimmed user prompt strings from stored history.
    """
    texts: set[str] = set()
    for message in stored_ui:
        role = getattr(message, "role", None)
        if role != "user":
            continue
        for part in getattr(message, "parts", []):
            if getattr(part, "type", None) != "text":
                continue
            text = str(getattr(part, "text", "")).strip()
            if text:
                texts.add(text)
    return texts


def _extract_new_client_messages(
    client_messages: list[dict[str, Any]],
    stored_ui: Sequence[object],
) -> list[dict[str, Any]]:
    """
    Return client UI messages that are not already persisted.

    Length-based slicing works when the client transcript matches the server
    shape. After live streaming, consecutive assistant steps are often merged
    into one UI message while persisted history keeps them split, so a new user
    prompt can share the same message count as stored history.

    Args:
        client_messages: UI messages submitted by the chat client.
        stored_ui: UI messages produced from persisted model history.

    Returns:
        Only the client messages that should be appended to stored history.
    """
    if len(client_messages) > len(stored_ui):
        return client_messages[len(stored_ui) :]

    if not client_messages:
        return []

    last = client_messages[-1]
    last_text = _user_message_text(last)
    if last_text and last_text not in _stored_user_texts(stored_ui):
        return [last]

    return client_messages[len(stored_ui) :]


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
    new_messages = _extract_new_client_messages(client_messages, stored_ui)
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
