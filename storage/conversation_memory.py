from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
)

from storage.db import utc_now_iso
from storage.session import db_connection

MAX_STORED_MESSAGES = 200
DEFAULT_CONVERSATION_ID = "default"
TITLE_MAX_LENGTH = 40


@dataclass(frozen=True)
class ConversationSummary:
    """
    Sidebar metadata for a stored conversation.
    """

    id: str
    title: str
    created_at: str
    pinned: bool
    model_id: str | None = None


def truncate_title(text: str, *, max_length: int = TITLE_MAX_LENGTH) -> str:
    """
    Trim and cap a sidebar title length.

    Args:
        text: Raw title text.
        max_length: Maximum visible characters before truncation.

    Returns:
        Trimmed title, with an ellipsis when truncated.
    """
    trimmed = text.strip()
    if len(trimmed) <= max_length:
        return trimmed
    return f"{trimmed[:max_length]}…"


def strip_system_messages(messages: Sequence[ModelMessage]) -> list[ModelMessage]:
    """
    Remove system prompt parts from conversation history.

    System prompts are re-injected on every agent run and should not appear in
    the chat UI when conversations are reloaded.

    Args:
        messages: Stored or in-flight model messages.

    Returns:
        Messages with ``SystemPromptPart`` entries removed.
    """
    filtered: list[ModelMessage] = []
    for message in messages:
        if not isinstance(message, ModelRequest):
            filtered.append(message)
            continue

        parts = [part for part in message.parts if not isinstance(part, SystemPromptPart)]
        if parts:
            filtered.append(ModelRequest(parts=parts))

    return filtered


def title_from_messages(messages: Sequence[ModelMessage]) -> str | None:
    """
    Derive a sidebar title from the first user text prompt.

    Args:
        messages: Stored model messages for a conversation.

    Returns:
        A trimmed title, or None when no user text exists.
    """
    for message in messages:
        if not isinstance(message, ModelRequest):
            continue
        for part in message.parts:
            if isinstance(part, UserPromptPart) and isinstance(part.content, str):
                text = part.content.strip()
                if not text:
                    continue
                return truncate_title(text)
    return None


def resolve_conversation_title(
    existing_title: str | None,
    messages: Sequence[ModelMessage],
    *,
    fallback_title: str | None = None,
) -> str:
    """
    Resolve the sidebar title for a conversation row.

    Args:
        existing_title: Title currently stored in SQLite.
        messages: Model messages being persisted.
        fallback_title: Optional title derived from the client request.

    Returns:
        A non-empty title when one can be inferred, otherwise an empty string.
    """
    current = (existing_title or "").strip()
    if current:
        return current
    return title_from_messages(messages) or (fallback_title or "").strip() or ""


def client_model_id_from_response_name(model_name: str) -> str:
    """
    Map a stored ``ModelResponse.model_name`` to the configure/UI model id.

    OpenRouter responses store a bare id (``provider/model``); the chat UI and
    configure endpoint use the ``openrouter:``-prefixed form.

    Args:
        model_name: Model name from a persisted assistant response.

    Returns:
        Model id suitable for the frontend model picker.
    """
    if model_name.startswith("openrouter:"):
        return model_name
    return f"openrouter:{model_name}"


def model_id_from_messages(messages: Sequence[ModelMessage]) -> str | None:
    """
    Derive the last-used model id from persisted assistant responses.

    Args:
        messages: Stored model messages for a conversation.

    Returns:
        Client model id from the most recent response, or None when absent.
    """
    for message in reversed(messages):
        if isinstance(message, ModelResponse) and message.model_name:
            return client_model_id_from_response_name(message.model_name)
    return None


def list_conversation_summaries(
    *,
    db_path: Path,
) -> list[ConversationSummary]:
    """
    List stored conversations for the sidebar.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Conversation summaries sorted newest-first, with pinned rows first.
    """
    with db_connection(db_path) as connection:
        rows = connection.execute(
            """
                        SELECT conversation_id, title, pinned, created_at, model_id, messages_json
                        FROM conversations
                        ORDER BY pinned DESC, created_at DESC
            """
        ).fetchall()

        summaries: list[ConversationSummary] = []
        for row in rows:
            title = (row["title"] or "").strip()
            model_id = row["model_id"]
            messages: list[ModelMessage] | None = None
            if not title or not model_id:
                messages = ModelMessagesTypeAdapter.validate_json(row["messages_json"])
            if not title:
                title = resolve_conversation_title(None, messages or []) or "New chat"
            if not model_id:
                model_id = model_id_from_messages(messages or [])

            summaries.append(
                ConversationSummary(
                    id=row["conversation_id"],
                    title=title,
                    created_at=row["created_at"],
                    pinned=bool(row["pinned"]),
                    model_id=model_id,
                )
            )

    return summaries


def load_conversation_messages(
    conversation_id: str,
    *,
    db_path: Path,
) -> list[ModelMessage]:
    """
    Load persisted model messages for a conversation.

    Args:
        conversation_id: Conversation identifier from the chat UI.
        db_path: Path to the SQLite database file.

    Returns:
        Stored model messages, or an empty list when none exist.
    """
    with db_connection(db_path) as connection:
        row = connection.execute(
            """
                        SELECT messages_json
                        FROM conversations
                        WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

    if row is None:
        return []

    messages = ModelMessagesTypeAdapter.validate_json(row["messages_json"])
    return strip_system_messages(messages)


def save_conversation_messages(
    conversation_id: str,
    messages: Sequence[ModelMessage],
    *,
    db_path: Path,
    fallback_title: str | None = None,
    model_id: str | None = None,
) -> None:
    """
    Persist model messages for a conversation.

    Args:
        conversation_id: Conversation identifier from the chat UI.
        messages: Full model message history for the conversation.
        db_path: Path to the SQLite database file.
        fallback_title: Optional title derived from the client request.
        model_id: Optional client model id last used for this conversation.
            When omitted on update, the existing stored model id is preserved.
    """
    messages = strip_system_messages(messages)
    if len(messages) > MAX_STORED_MESSAGES:
        messages = messages[-MAX_STORED_MESSAGES:]

    payload = ModelMessagesTypeAdapter.dump_json(messages).decode("utf-8")
    timestamp = utc_now_iso()

    with db_connection(db_path) as connection:
        existing = connection.execute(
            """
                        SELECT title, created_at, model_id
                        FROM conversations
                        WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

        title = resolve_conversation_title(
            existing["title"] if existing is not None else None,
            messages,
            fallback_title=fallback_title,
        )
        resolved_model_id = (
            model_id if model_id is not None else (existing["model_id"] if existing else None)
        )

        if existing is None:
            connection.execute(
                """
                                INSERT INTO conversations (
                                    conversation_id,
                                    messages_json,
                                    title,
                                    pinned,
                                    model_id,
                                    created_at,
                                    updated_at
                                )
                                VALUES (?, ?, ?, 0, ?, ?, ?)
                """,
                (conversation_id, payload, title, resolved_model_id, timestamp, timestamp),
            )
        else:
            connection.execute(
                """
                                UPDATE conversations
                                SET messages_json = ?,
                                    title = ?,
                                    model_id = ?,
                                    updated_at = ?
                                WHERE conversation_id = ?
                """,
                (payload, title, resolved_model_id, timestamp, conversation_id),
            )
        connection.commit()


def update_conversation_metadata(
    conversation_id: str,
    *,
    db_path: Path,
    title: str | None = None,
    pinned: bool | None = None,
) -> bool:
    """
    Update sidebar metadata for a conversation.

    Args:
        conversation_id: Conversation identifier from the chat UI.
        db_path: Path to the SQLite database file.
        title: Optional new title.
        pinned: Optional pinned flag.

    Returns:
        True when the conversation exists and was updated.
    """
    updates: list[str] = []
    values: list[object] = []

    if title is not None:
        updates.append("title = ?")
        values.append(title)
    if pinned is not None:
        updates.append("pinned = ?")
        values.append(int(pinned))

    if not updates:
        return False

    updates.append("updated_at = ?")
    values.append(utc_now_iso())
    values.append(conversation_id)

    with db_connection(db_path) as connection:
        cursor = connection.execute(
            f"""
            UPDATE conversations
            SET {", ".join(updates)}
            WHERE conversation_id = ?
            """,
            values,
        )
        connection.commit()
        return cursor.rowcount > 0


def delete_conversation(
    conversation_id: str,
    *,
    db_path: Path,
) -> bool:
    """
    Delete a conversation and its stored messages.

    Args:
        conversation_id: Conversation identifier from the chat UI.
        db_path: Path to the SQLite database file.

    Returns:
        True when a row was deleted.
    """
    with db_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM conversations WHERE conversation_id = ?",
            (conversation_id,),
        )
        connection.commit()
        return cursor.rowcount > 0
