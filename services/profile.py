from pathlib import Path
from typing import Literal

from config import get_settings

_cached_mtime: float | None = None
_cached_content: str | None = None

_EMPTY_SYSTEM_MESSAGE = (
    "No user profile is configured yet. The user can add personal context to "
    "data/profile.txt, including age, education, employment status, and career "
    "goals."
)
_EMPTY_TOOL_MESSAGE = (
    "No user profile found. Add personal context to data/profile.txt, such as "
    "age, education level, employment status, and professional goals."
)


def load_profile(profile_path: Path | None = None) -> str:
    """
    Load the user's personal profile from disk.

    The profile is cached in memory and refreshed when the file changes.

    Args:
        profile_path: Optional profile path override.

    Returns:
        Profile text, or an empty string when the file is missing or blank.
    """
    global _cached_mtime, _cached_content

    path = profile_path or get_settings().profile_path
    if not path.exists():
        _cached_mtime = None
        _cached_content = None
        return ""

    mtime = path.stat().st_mtime
    if _cached_mtime == mtime and _cached_content is not None:
        return _cached_content

    content = path.read_text(encoding="utf-8").strip()
    _cached_mtime = mtime
    _cached_content = content
    return content


def format_profile_message(
    profile_path: Path | None = None,
    *,
    context: Literal["system", "tool"] = "system",
) -> str:
    """
    Format profile text for system prompt injection or the profile tool.

    Args:
        profile_path: Optional profile path override.
        context: Whether the message is for system prompt or tool output.

    Returns:
        Profile guidance or content for the requested context.
    """
    profile = load_profile(profile_path)
    if not profile:
        return _EMPTY_SYSTEM_MESSAGE if context == "system" else _EMPTY_TOOL_MESSAGE

    if context == "tool":
        return profile

    return (
        "Weight every recommendation against the user's stated goals, employment "
        "status, risk tolerance, and near-term priorities:\n\n"
        f"{profile}"
    )
