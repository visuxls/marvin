from pathlib import Path

from pydantic import SecretStr

from config import Settings, get_settings
from config.settings import Settings as SettingsClass


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    get_settings.cache_clear()
    settings = get_settings()
    assert Path("data/marvin.db") == settings.DB_PATH
    assert settings.AUTO_IMPORT_ON_STARTUP is True


def test_settings_override(test_settings: Settings):
    assert test_settings.AUTO_IMPORT_ON_STARTUP is False
    assert test_settings.OPENROUTER_MODEL == "z-ai/glm-5.2"


def test_settings_parse_openrouter_models(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret")
    monkeypatch.setenv(
        "OPENROUTER_MODELS",
        "GLM:z-ai/glm-5.2, anthropic/claude-sonnet-4",
    )
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.OPENROUTER_MODELS == [
        "GLM:z-ai/glm-5.2",
        "anthropic/claude-sonnet-4",
    ]


def test_settings_openrouter_models_accepts_list():
    settings = SettingsClass(
        OPENROUTER_API_KEY=SecretStr("secret"),
        OPENROUTER_MODELS=["model-a", "model-b"],
    )
    assert settings.OPENROUTER_MODELS == ["model-a", "model-b"]


def test_settings_openrouter_models_empty_string():
    settings = SettingsClass.model_validate(
        {
            "OPENROUTER_API_KEY": "secret",
            "OPENROUTER_MODELS": "",
        }
    )
    assert settings.OPENROUTER_MODELS == []


def test_settings_openrouter_models_unknown_value_returns_empty():
    assert SettingsClass.parse_openrouter_models(123) == []
