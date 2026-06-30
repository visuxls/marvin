from pathlib import Path

from pydantic import SecretStr

from config import Settings, get_settings
from config.settings import Settings as SettingsClass


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.db_path == Path("data/marvin.db")
    assert settings.auto_import_on_startup is True


def test_settings_override(test_settings: Settings):
    assert test_settings.auto_import_on_startup is False
    assert test_settings.openrouter_model == "z-ai/glm-5.2"


def test_settings_parse_openrouter_models(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    monkeypatch.setenv(
        "OPENROUTER_MODELS",
        "GLM:z-ai/glm-5.2, anthropic/claude-sonnet-4",
    )
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.openrouter_models == [
        "GLM:z-ai/glm-5.2",
        "anthropic/claude-sonnet-4",
    ]


def test_settings_openrouter_models_accepts_list():
    settings = SettingsClass(
        openrouter_api_key=SecretStr("secret"),
        openrouter_models=["model-a", "model-b"],
    )
    assert settings.openrouter_models == ["model-a", "model-b"]


def test_settings_openrouter_models_empty_string():
    settings = SettingsClass.model_validate(
        {
            "openrouter_api_key": "secret",
            "openrouter_models": "",
        }
    )
    assert settings.openrouter_models == []


def test_settings_openrouter_models_unknown_value_returns_empty():
    assert SettingsClass.parse_openrouter_models(123) == []
