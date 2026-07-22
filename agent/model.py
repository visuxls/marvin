from typing import Literal

from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings
from pydantic_ai.providers.openrouter import OpenRouterProvider

from config import Settings, get_settings

ReasoningSelection = Literal["off", "minimal", "low", "medium", "high", "xhigh"]

DEFAULT_REASONING_EFFORT: ReasoningSelection = "off"

REASONING_EFFORT_OPTIONS: list[tuple[ReasoningSelection, str]] = [
    ("off", "Off"),
    ("minimal", "Minimal"),
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("xhigh", "Extra high"),
]


def parse_model_entry(entry: str) -> tuple[str, str]:
    """
    Parse a configured model entry into a display label and model id.

    Entries may be ``model-id`` or ``label:model-id``.

    Args:
        entry: Single model entry from settings.

    Returns:
        Display label and OpenRouter model id.
    """
    if ":" in entry:
        label, model_id = entry.split(":", 1)
        return label.strip(), model_id.strip()
    model_id = entry.strip()
    return model_id, model_id


def _openrouter_provider(settings: Settings) -> OpenRouterProvider:
    """
    Create an OpenRouter provider from application settings.

    Args:
        settings: Application settings.

    Returns:
        Configured OpenRouter provider.
    """
    return OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY.get_secret_value())


def _default_model_id(settings: Settings) -> str:
    """
    Resolve the default OpenRouter model id from settings.

    Args:
        settings: Application settings.

    Returns:
        Model id for the agent default and single-model UI fallback.
    """
    if settings.OPENROUTER_MODELS:
        _, model_id = parse_model_entry(settings.OPENROUTER_MODELS[0])
        return model_id
    return settings.OPENROUTER_MODEL


def build_available_models(settings: Settings | None = None) -> dict[str, OpenRouterModel]:
    """
    Build labeled OpenRouter models exposed in the chat UI.

    Args:
        settings: Optional settings override for tests.

    Returns:
        Mapping of display label to configured OpenRouter model.
    """
    resolved = settings or get_settings()
    provider = _openrouter_provider(resolved)
    if resolved.OPENROUTER_MODELS:
        return {
            label: OpenRouterModel(model_id, provider=provider)
            for label, model_id in (
                parse_model_entry(entry) for entry in resolved.OPENROUTER_MODELS
            )
        }
    model_id = _default_model_id(resolved)
    return {model_id: OpenRouterModel(model_id, provider=provider)}


def build_model(settings: Settings | None = None) -> OpenRouterModel:
    """
    Create the OpenRouter model configured for Marvin.

    Args:
        settings: Optional settings override for tests.

    Returns:
        Configured OpenRouter model instance.
    """
    resolved = settings or get_settings()
    return OpenRouterModel(
        _default_model_id(resolved),
        provider=_openrouter_provider(resolved),
    )


def _openrouter_model_slug(model_id: str) -> str:
    """
    Normalize a UI or OpenRouter model id to ``org/model`` form.

    Args:
        model_id: Model id, optionally prefixed with ``openrouter:``.

    Returns:
        Bare OpenRouter model slug.
    """
    return model_id.removeprefix("openrouter:")


def is_deepseek_model(model_id: str) -> bool:
    """
    Return whether ``model_id`` is a DeepSeek-hosted OpenRouter model.

    Args:
        model_id: UI or OpenRouter model id.

    Returns:
        True when the model org slug is ``deepseek``.
    """
    return _openrouter_model_slug(model_id).startswith("deepseek/")


def build_model_settings(
    *,
    reasoning_effort: ReasoningSelection | None = None,
    session_id: str | None = None,
    model_id: str | None = None,
) -> OpenRouterModelSettings:
    """
    Create OpenRouter model settings for an agent run.

    DeepSeek models are locked to DeepSeek's own inference endpoints. Other
    models omit explicit provider routing so OpenRouter can pick a cheap
    endpoint and sticky-route follow-ups. When ``session_id`` is set (typically
    the chat conversation id), sticky routing activates on the first successful
    request.

    Args:
        reasoning_effort: Optional per-request reasoning effort from the UI.
        session_id: Optional OpenRouter session id for provider sticky routing.
        model_id: Optional selected model id used for provider routing rules.

    Returns:
        OpenRouter model settings for agent runs.
    """
    selected_effort = reasoning_effort or DEFAULT_REASONING_EFFORT
    model_settings: OpenRouterModelSettings = {}
    if session_id:
        model_settings["extra_body"] = {"session_id": session_id}
    if model_id and is_deepseek_model(model_id):
        model_settings["openrouter_provider"] = {
            "only": ["deepseek"],
            "allow_fallbacks": False,
        }
    if selected_effort != "off":
        model_settings["openrouter_reasoning"] = {
            "effort": selected_effort,
            "enabled": True,
        }
    return OpenRouterModelSettings(**model_settings)
