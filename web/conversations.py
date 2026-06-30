"""
Web-layer helpers for conversation sidebar and UI message hydration.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from storage.conversation_memory import (
    ConversationSummary,
    load_conversation_messages,
    truncate_title,
)
from web.schemas import ConversationSummaryResponse


def _iso_to_epoch_ms(iso_timestamp: str) -> int:
    """
    Convert an ISO timestamp to epoch milliseconds.

    Args:
        iso_timestamp: UTC ISO 8601 timestamp.

    Returns:
        Milliseconds since the Unix epoch.
    """
    return int(datetime.fromisoformat(iso_timestamp).timestamp() * 1000)


def title_from_ui_messages(messages: list[dict[str, Any]]) -> str | None:
    """
    Derive a sidebar title from Vercel AI UI messages.

    Args:
        messages: Client-submitted UI messages from the chat request.

    Returns:
        A trimmed title, or None when no user text exists.
    """
    for message in messages:
        if message.get("role") != "user":
            continue
        for part in message.get("parts", []):
            if part.get("type") != "text":
                continue
            text = str(part.get("text", "")).strip()
            if not text:
                continue
            return truncate_title(text)
    return None


def conversation_summary_response(summary: ConversationSummary) -> ConversationSummaryResponse:
    """
    Build a conversation summary response for the frontend API.

    Args:
        summary: Stored conversation metadata.

    Returns:
        Validated sidebar entry response model.
    """
    return ConversationSummaryResponse(
        id=summary.id,
        title=summary.title,
        created_at=_iso_to_epoch_ms(summary.created_at),
        pinned=summary.pinned,
    )


def load_conversation_ui_messages(
    conversation_id: str,
    *,
    db_path: Path,
    sdk_version: Literal[5, 6] = 6,
) -> list[dict[str, Any]]:
    """
    Load persisted messages in Vercel AI UI format.

    Args:
        conversation_id: Conversation identifier from the chat UI.
        db_path: Path to the SQLite database file.
        sdk_version: Vercel AI SDK version to target.

    Returns:
        UI messages suitable for ``useChat`` hydration.
    """
    messages = load_conversation_messages(conversation_id, db_path=db_path)
    if not messages:
        return []

    ui_messages = VercelAIAdapter.dump_messages(messages, sdk_version=sdk_version)
    return [
        message.model_dump(mode="json", by_alias=True)
        for message in ui_messages
        if message.role != "system"
    ]
