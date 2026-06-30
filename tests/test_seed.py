from pathlib import Path

import pytest
from pydantic import SecretStr

from config import Settings
from ingestion.importer import import_all
from ingestion.seed import SEED_TEMPLATES_DIR, ensure_demo_data
from storage.queries import get_holdings, list_accounts
from storage.session import db_connection


@pytest.fixture
def empty_settings(tmp_path: Path) -> Settings:
    """
    Build settings pointing at empty temporary paths.
    """
    return Settings(
        openrouter_api_key=SecretStr("test-key"),
        openrouter_models=[],
        db_path=tmp_path / "marvin.db",
        imports_dir=tmp_path / "imports",
        profile_path=tmp_path / "profile.txt",
        auto_import_on_startup=False,
    )


def test_ensure_demo_data_creates_missing_files(empty_settings: Settings):
    seeded = ensure_demo_data(settings=empty_settings)

    assert len(seeded) == 5
    assert (empty_settings.imports_dir / "accounts.csv").exists()
    assert (empty_settings.imports_dir / "balances.csv").exists()
    assert (empty_settings.imports_dir / "holdings.csv").exists()
    assert (empty_settings.imports_dir / "transactions.csv").exists()
    assert empty_settings.profile_path.exists()

    accounts_text = (empty_settings.imports_dir / "accounts.csv").read_text(encoding="utf-8")
    assert accounts_text == (SEED_TEMPLATES_DIR / "accounts.csv").read_text(encoding="utf-8")


def test_ensure_demo_data_skips_existing_files(empty_settings: Settings):
    empty_settings.imports_dir.mkdir(parents=True)
    existing_accounts = empty_settings.imports_dir / "accounts.csv"
    existing_accounts.write_text("custom content\n", encoding="utf-8")
    empty_settings.profile_path.write_text("custom profile\n", encoding="utf-8")

    seeded = ensure_demo_data(settings=empty_settings)

    assert existing_accounts not in seeded
    assert empty_settings.profile_path not in seeded
    assert existing_accounts.read_text(encoding="utf-8") == "custom content\n"
    assert empty_settings.profile_path.read_text(encoding="utf-8") == "custom profile\n"
    assert len(seeded) == 3
    assert (empty_settings.imports_dir / "balances.csv") in seeded
    assert (empty_settings.imports_dir / "holdings.csv") in seeded
    assert (empty_settings.imports_dir / "transactions.csv") in seeded


def test_ensure_demo_data_seeds_only_missing(empty_settings: Settings):
    empty_settings.imports_dir.mkdir(parents=True)
    (empty_settings.imports_dir / "accounts.csv").write_text(
        "Account ID,Name,Type,Institution\n1,Only,Checking,Bank\n",
        encoding="utf-8",
    )

    seeded = ensure_demo_data(settings=empty_settings)

    assert empty_settings.imports_dir / "accounts.csv" not in seeded
    assert len(seeded) == 4
    assert (empty_settings.imports_dir / "balances.csv") in seeded
    assert (empty_settings.imports_dir / "holdings.csv") in seeded
    assert (empty_settings.imports_dir / "transactions.csv") in seeded
    assert empty_settings.profile_path in seeded


def test_demo_data_imports_cleanly(empty_settings: Settings):
    ensure_demo_data(settings=empty_settings)
    results = import_all(settings=empty_settings)

    assert results[0].inserted == 3
    assert results[1].inserted == 6
    assert results[2].inserted == 3
    assert results[3].inserted == 197
    assert results[1].skipped == 0
    assert results[2].skipped == 0
    assert results[3].skipped == 0

    with db_connection(empty_settings.db_path) as connection:
        assert len(list_accounts(connection)) == 3
        assert len(get_holdings(connection)) == 3
