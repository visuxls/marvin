from unittest.mock import MagicMock

from agent.deps import CFODeps
from agent.initialize_agent import build_agent
from agent.prompt import profile_system_prompt, runtime_system_prompt


def test_build_agent_registers_tools():
    agent = build_agent()
    assert agent is not None
    assert len(agent._function_toolset.tools) >= 14


def test_registered_system_prompts(profile_path, tmp_path):
    ctx = MagicMock()
    ctx.deps = CFODeps(db_path=tmp_path / "db", profile_path=profile_path)
    runtime = runtime_system_prompt(ctx)
    profile = profile_system_prompt(ctx)
    assert runtime is not None
    assert profile is not None
    assert "Today is" in runtime
    assert "Age: 30" in profile
