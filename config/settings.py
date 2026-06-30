from functools import lru_cache
from pathlib import Path
from typing import Annotated, cast

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and `.env`.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: SecretStr
    openrouter_model: str = "z-ai/glm-5.2"
    openrouter_models: Annotated[list[str], NoDecode] = Field(default_factory=list)
    openrouter_provider_order: str = "deepinfra"
    openrouter_allow_fallbacks: bool = True

    @field_validator("openrouter_models", mode="before")
    @classmethod
    def parse_openrouter_models(cls, value: object) -> list[str]:
        """
        Parse comma-separated model entries from environment variables.

        Args:
            value: Raw setting value from the environment or tests.

        Returns:
            Trimmed model entries.
        """
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [entry.strip() for entry in value.split(",") if entry.strip()]
        if isinstance(value, list):
            return cast(list[str], value)
        return []

    db_path: Path = Path("data/marvin.db")
    imports_dir: Path = Path("data/imports")
    profile_path: Path = Path("data/profile.txt")
    auto_import_on_startup: bool = True
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:3000", "http://localhost:3000"]
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.

    Returns:
        Parsed settings instance loaded from the environment and `.env`.
    """
    return Settings()  # ty: ignore[missing-argument]
