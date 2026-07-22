from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel
from pydantic_ai.ui._web.api import BuiltinToolInfo, ModelInfo  # private API

from agent.model import DEFAULT_REASONING_EFFORT, REASONING_EFFORT_OPTIONS, ReasoningSelection


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
    model: str | None = None


class ConversationMessagesResponse(BaseModel):
    """
    Persisted Vercel AI UI messages for a conversation.
    """

    messages: list[dict[str, Any]]


class ReasoningEffortOption(BaseModel):
    """
    Reasoning effort choice exposed in the chat composer.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: ReasoningSelection
    label: str


class ConfigureResponse(BaseModel):
    """
    Frontend configuration for models, tools, and reasoning controls.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    models: list[ModelInfo]
    builtin_tools: list[BuiltinToolInfo]
    reasoning_efforts: list[ReasoningEffortOption]
    default_reasoning_effort: ReasoningSelection = DEFAULT_REASONING_EFFORT


class ChatRequestOptions(BaseModel):
    """
    Marvin-specific fields accepted on chat requests alongside the Vercel AI payload.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    reasoning_effort: ReasoningSelection | None = None

    @field_validator("reasoning_effort", mode="before")
    @classmethod
    def normalize_reasoning_effort(cls, value: object) -> object:
        """
        Treat blank values as omitted reasoning effort.

        Args:
            value: Raw request field value.

        Returns:
            Normalized effort id or None.
        """
        if value is None or value == "":
            return None
        return value


def build_configure_response(
    *,
    models: list[ModelInfo],
    builtin_tools: list[BuiltinToolInfo],
) -> ConfigureResponse:
    """
    Build the Marvin configure payload for the chat UI.

    Args:
        models: Models available in the composer.
        builtin_tools: Native tools available in the composer.

    Returns:
        Configure response including reasoning effort options.
    """
    return ConfigureResponse(
        models=models,
        builtin_tools=builtin_tools,
        reasoning_efforts=[
            ReasoningEffortOption(id=effort_id, label=label)
            for effort_id, label in REASONING_EFFORT_OPTIONS
        ],
        default_reasoning_effort=DEFAULT_REASONING_EFFORT,
    )


def resolve_reasoning_effort(
    options: ChatRequestOptions | None,
) -> ReasoningSelection:
    """
    Resolve the reasoning effort for a chat request.

    Args:
        options: Parsed Marvin chat request options.

    Returns:
        Reasoning effort to apply for the request.
    """
    if options is None or options.reasoning_effort is None:
        return DEFAULT_REASONING_EFFORT
    return options.reasoning_effort
