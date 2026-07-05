from functools import lru_cache
from pathlib import Path
from typing import Annotated, cast

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and `.env`.
    """

    OPENROUTER_API_KEY: SecretStr
    OPENROUTER_MODEL: str = "z-ai/glm-5.2"
    OPENROUTER_MODELS: Annotated[list[str], NoDecode] = Field(default_factory=list)
    OPENROUTER_PROVIDER_ORDER: str = "deepinfra"
    OPENROUTER_ALLOW_FALLBACKS: bool = True

    DB_PATH: Path = Path("data/marvin.db")
    IMPORTS_DIR: Path = Path("data/imports")
    PROFILE_PATH: Path = Path("data/profile.txt")
    AUTO_IMPORT_ON_STARTUP: bool = True
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:3000", "http://localhost:3000"]
    )

    @field_validator("OPENROUTER_MODELS", mode="before")
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.

    Returns:
        Parsed settings instance loaded from the environment and `.env`.
    """
    return Settings()  # ty: ignore[missing-argument]
