from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class OkResponse(BaseModel):
    """
    Generic success response for mutating API operations.
    """

    ok: bool = True


class HealthResponse(BaseModel):
    """
    Health-check response payload.
    """

    ok: bool = True


class ErrorDetail(BaseModel):
    """
    Error body returned in HTTP exception details.
    """

    error: str


class ConversationPatch(BaseModel):
    """
    Partial update payload for conversation sidebar metadata.
    """

    model_config = ConfigDict(strict=True)

    title: str | None = None
    pinned: bool | None = None


class ConversationSummaryResponse(BaseModel):
    """
    Sidebar conversation entry returned by the list API.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    title: str
    created_at: int
    pinned: bool


class ConversationMessagesResponse(BaseModel):
    """
    Persisted Vercel AI UI messages for a conversation.
    """

    messages: list[dict[str, Any]]
