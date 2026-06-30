from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, Request

from config import get_settings
from config.settings import Settings
from web.memory.runtime import ChatRuntime


def get_app_settings() -> Settings:
    """
    Return application settings for dependency injection.

    Returns:
        Resolved settings instance.
    """
    return get_settings()


def get_chat_runtime(request: Request) -> ChatRuntime[Any, Any]:
    """
    Return the chat runtime stored on the application.

    Args:
        request: Current HTTP request.

    Returns:
        Chat runtime built at application startup.
    """
    return request.app.state.chat_runtime


def get_html_source(request: Request) -> str | Path | None:
    """
    Return the configured chat UI HTML source override.

    Args:
        request: Current HTTP request.

    Returns:
        Optional HTML source path or URL from application state.
    """
    return request.app.state.html_source


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
ChatRuntimeDep = Annotated[ChatRuntime[Any, Any], Depends(get_chat_runtime)]
HtmlSourceDep = Annotated[str | Path | None, Depends(get_html_source)]
