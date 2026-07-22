from agent.model import (
    build_available_models,
    build_model,
    build_model_settings,
    is_deepseek_model,
    parse_model_entry,
)
from config import Settings


def test_parse_model_entry_with_label():
    assert parse_model_entry("GLM:z-ai/glm-5.2") == ("GLM", "z-ai/glm-5.2")


def test_parse_model_entry_without_label():
    assert parse_model_entry("z-ai/glm-5.2") == ("z-ai/glm-5.2", "z-ai/glm-5.2")


def test_is_deepseek_model():
    assert is_deepseek_model("deepseek/deepseek-v4-pro")
    assert is_deepseek_model("openrouter:deepseek/deepseek-chat")
    assert not is_deepseek_model("z-ai/glm-5.2")
    assert not is_deepseek_model("openrouter:anthropic/claude-opus-4.8")


def test_build_available_models_defaults_to_single_model(test_settings: Settings):
    models = build_available_models(test_settings)
    assert list(models) == [test_settings.OPENROUTER_MODEL]
    assert models[test_settings.OPENROUTER_MODEL].model_name == test_settings.OPENROUTER_MODEL


def test_build_available_models_uses_configured_list(test_settings: Settings):
    test_settings.OPENROUTER_MODELS = [
        "GLM:z-ai/glm-5.2",
        "anthropic/claude-sonnet-4",
    ]
    models = build_available_models(test_settings)
    assert list(models) == ["GLM", "anthropic/claude-sonnet-4"]
    assert models["GLM"].model_name == "z-ai/glm-5.2"
    assert models["anthropic/claude-sonnet-4"].model_name == "anthropic/claude-sonnet-4"


def test_build_model(test_settings: Settings):
    model = build_model(test_settings)
    assert model.model_name == test_settings.OPENROUTER_MODEL


def test_build_model_uses_first_configured_model(test_settings: Settings):
    test_settings.OPENROUTER_MODELS = ["GLM:z-ai/glm-5.2", "anthropic/claude-sonnet-4"]
    model = build_model(test_settings)
    assert model.model_name == "z-ai/glm-5.2"


def test_build_model_settings():
    settings = build_model_settings()
    assert "openrouter_provider" not in settings
    assert "extra_body" not in settings
    assert "openrouter_reasoning" not in settings


def test_build_model_settings_with_session_id():
    settings = build_model_settings(session_id="conv-1")
    assert settings["extra_body"] == {"session_id": "conv-1"}
    assert "openrouter_provider" not in settings


def test_build_model_settings_locks_deepseek_provider():
    settings = build_model_settings(model_id="openrouter:deepseek/deepseek-v4-pro")
    assert settings["openrouter_provider"] == {
        "only": ["deepseek"],
        "allow_fallbacks": False,
    }


def test_build_model_settings_does_not_lock_non_deepseek():
    settings = build_model_settings(model_id="openrouter:z-ai/glm-5.2")
    assert "openrouter_provider" not in settings


def test_build_model_settings_with_reasoning():
    settings = build_model_settings(reasoning_effort="high")
    assert settings["openrouter_reasoning"] == {"effort": "high", "enabled": True}


def test_build_model_settings_with_xhigh_reasoning():
    settings = build_model_settings(reasoning_effort="xhigh")
    assert settings["openrouter_reasoning"] == {"effort": "xhigh", "enabled": True}


def test_build_model_settings_with_reasoning_off():
    settings = build_model_settings(reasoning_effort="off")
    assert "openrouter_reasoning" not in settings
