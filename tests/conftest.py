import os
from pathlib import Path

import pytest
from pydantic import SecretStr
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from agent.deps import CFODeps, build_deps
from config import Settings, get_settings
from web.app import create_marvin_web_app

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _reset_caches():
    """
    Clear module-level caches between tests.
    """
    get_settings.cache_clear()

    import services.market_data as market_data
    import services.profile as profile

    market_data._price_cache.clear()
    profile._cached_mtime = None
    profile._cached_content = None
    yield
    get_settings.cache_clear()
    market_data._price_cache.clear()
    profile._cached_mtime = None
    profile._cached_content = None


@pytest.fixture
def imports_dir(tmp_path: Path) -> Path:
    """
    Copy fixture CSVs into a temporary imports directory.
    """
    target = tmp_path / "imports"
    target.mkdir()
    for name in ("accounts.csv", "balances.csv", "holdings.csv", "transactions.csv"):
        target.joinpath(name).write_text(
            FIXTURES_DIR.joinpath(name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    return target


@pytest.fixture
def profile_path(tmp_path: Path) -> Path:
    """
    Return a temporary profile file.
    """
    path = tmp_path / "profile.txt"
    path.write_text(
        FIXTURES_DIR.joinpath("profile.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """
    Return a temporary database path.
    """
    return tmp_path / "test.db"


@pytest.fixture
def test_settings(
    db_path: Path,
    imports_dir: Path,
    profile_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Settings:
    """
    Build settings pointing at temporary paths.
    """
    settings = Settings(
        openrouter_api_key=SecretStr("test-key"),
        openrouter_models=[],
        db_path=db_path,
        imports_dir=imports_dir,
        profile_path=profile_path,
        auto_import_on_startup=False,
    )
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.setenv("IMPORTS_DIR", str(imports_dir))
    monkeypatch.setenv("PROFILE_PATH", str(profile_path))
    monkeypatch.setenv("AUTO_IMPORT_ON_STARTUP", "false")
    get_settings.cache_clear()
    return settings


@pytest.fixture
def api_app(test_settings: Settings, monkeypatch: pytest.MonkeyPatch):
    """
    Build a test API app with temporary settings.
    """
    monkeypatch.setattr("web.dependencies.get_app_settings", lambda: test_settings)
    agent = Agent(TestModel(), deps_type=CFODeps)
    return create_marvin_web_app(agent, deps=build_deps(test_settings))
