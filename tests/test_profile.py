from pathlib import Path

import services.profile as profile
from services.profile import format_profile_message, load_profile


def test_load_profile_missing_file(tmp_path: Path):
    assert load_profile(tmp_path / "missing.txt") == ""


def test_load_profile_reads_and_caches(profile_path: Path):
    first = load_profile(profile_path)
    second = load_profile(profile_path)
    assert "Age: 30" in first
    assert first == second


def test_load_profile_refreshes_on_mtime_change(profile_path: Path):
    load_profile(profile_path)
    profile_path.write_text("Updated profile", encoding="utf-8")
    assert load_profile(profile_path) == "Updated profile"


def test_load_profile_blank_file(tmp_path: Path):
    path = tmp_path / "profile.txt"
    path.write_text("   \n", encoding="utf-8")
    assert load_profile(path) == ""


def test_load_profile_resets_cache_when_missing(profile_path: Path, tmp_path: Path):
    load_profile(profile_path)
    profile_path.unlink()
    profile._cached_mtime = 1.0
    profile._cached_content = "stale"
    assert load_profile(profile_path) == ""


def test_format_profile_message_system_context(profile_path: Path):
    message = format_profile_message(profile_path, context="system")
    assert "Age: 30" in message
    assert "Weight every recommendation" in message


def test_format_profile_message_tool_context(profile_path: Path):
    message = format_profile_message(profile_path, context="tool")
    assert message == load_profile(profile_path)


def test_format_profile_message_missing_system_context(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    message = format_profile_message(missing, context="system")
    assert "No user profile is configured" in message


def test_format_profile_message_missing_tool_context(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    message = format_profile_message(missing, context="tool")
    assert "No user profile found" in message
