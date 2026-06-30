from agent.model import (
    build_available_models,
    build_model,
    build_model_settings,
    parse_model_entry,
)
from config import Settings


def test_parse_model_entry_with_label():
    assert parse_model_entry("GLM:z-ai/glm-5.2") == ("GLM", "z-ai/glm-5.2")


def test_parse_model_entry_without_label():
    assert parse_model_entry("z-ai/glm-5.2") == ("z-ai/glm-5.2", "z-ai/glm-5.2")


def test_build_available_models_defaults_to_single_model(test_settings: Settings):
    models = build_available_models(test_settings)
    assert list(models) == [test_settings.openrouter_model]
    assert models[test_settings.openrouter_model].model_name == test_settings.openrouter_model


def test_build_available_models_uses_configured_list(test_settings: Settings):
    test_settings.openrouter_models = [
        "GLM:z-ai/glm-5.2",
        "anthropic/claude-sonnet-4",
    ]
    models = build_available_models(test_settings)
    assert list(models) == ["GLM", "anthropic/claude-sonnet-4"]
    assert models["GLM"].model_name == "z-ai/glm-5.2"
    assert models["anthropic/claude-sonnet-4"].model_name == "anthropic/claude-sonnet-4"


def test_build_model(test_settings: Settings):
    model = build_model(test_settings)
    assert model.model_name == test_settings.openrouter_model


def test_build_model_uses_first_configured_model(test_settings: Settings):
    test_settings.openrouter_models = ["GLM:z-ai/glm-5.2", "anthropic/claude-sonnet-4"]
    model = build_model(test_settings)
    assert model.model_name == "z-ai/glm-5.2"


def test_build_model_settings(test_settings: Settings):
    settings = build_model_settings(test_settings)
    assert settings["openrouter_provider"]["order"] == ["deepinfra"]
    assert settings["openrouter_provider"]["allow_fallbacks"] is True
