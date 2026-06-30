from unittest.mock import MagicMock

from agent.deps import CFODeps
from agent.prompt import profile_system_prompt, runtime_system_prompt


def test_runtime_system_prompt():
    ctx = MagicMock()
    prompt = runtime_system_prompt(ctx)
    assert prompt.startswith("Today is ")


def test_profile_system_prompt_with_profile(profile_path):
    ctx = MagicMock()
    ctx.deps = CFODeps(db_path=profile_path.parent / "db", profile_path=profile_path)
    prompt = profile_system_prompt(ctx)
    assert "Age: 30" in prompt


def test_profile_system_prompt_missing(profile_path, tmp_path):
    missing = tmp_path / "missing.txt"
    ctx = MagicMock()
    ctx.deps = CFODeps(db_path=tmp_path / "db", profile_path=missing)
    prompt = profile_system_prompt(ctx)
    assert "No user profile is configured" in prompt
