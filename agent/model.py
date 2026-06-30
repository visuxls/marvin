from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings
from pydantic_ai.providers.openrouter import OpenRouterProvider

from config import Settings, get_settings


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
    return OpenRouterProvider(api_key=settings.openrouter_api_key.get_secret_value())


def _default_model_id(settings: Settings) -> str:
    """
    Resolve the default OpenRouter model id from settings.

    Args:
        settings: Application settings.

    Returns:
        Model id for the agent default and single-model UI fallback.
    """
    if settings.openrouter_models:
        _, model_id = parse_model_entry(settings.openrouter_models[0])
        return model_id
    return settings.openrouter_model


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
    if resolved.openrouter_models:
        return {
            label: OpenRouterModel(model_id, provider=provider)
            for label, model_id in (
                parse_model_entry(entry) for entry in resolved.openrouter_models
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


def build_model_settings(settings: Settings | None = None) -> OpenRouterModelSettings:
    """
    Create provider routing settings for the OpenRouter model.

    Args:
        settings: Optional settings override for tests.

    Returns:
        OpenRouter model settings for agent runs.
    """
    resolved = settings or get_settings()
    return OpenRouterModelSettings(
        openrouter_provider={
            "order": [
                provider.strip()
                for provider in resolved.openrouter_provider_order.split(",")
                if provider.strip()
            ],
            "allow_fallbacks": resolved.openrouter_allow_fallbacks,
        }
    )
