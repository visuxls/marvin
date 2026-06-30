import logging
from pathlib import Path

import pytest

from config import Settings
from ingestion.importer import import_all, log_import_results


def test_import_all_inserts_rows(test_settings: Settings):
    results = import_all(settings=test_settings)
    assert len(results) == 4
    assert results[0].inserted == 2
    assert results[1].inserted == 2
    assert results[2].inserted == 2
    assert results[3].inserted == 3


def test_import_all_is_idempotent(test_settings: Settings):
    import_all(settings=test_settings)
    results = import_all(settings=test_settings)
    assert results[0].updated == 2
    assert results[1].updated == 2
    assert results[2].updated == 2
    assert results[3].updated == 3


def test_import_skips_unknown_account(tmp_path: Path, test_settings: Settings):
    balances = tmp_path / "imports" / "balances.csv"
    balances.write_text(
        "Account ID,Date,Balance\n99,2025-01-01,100\n",
        encoding="utf-8",
    )
    results = import_all(settings=test_settings)
    balance_result = results[1]
    assert balance_result.skipped == 1
    assert any("unknown Account ID" in error for error in balance_result.errors)


def test_log_import_results(caplog: pytest.LogCaptureFixture):
    from ingestion.importer import ImportResult

    caplog.set_level(logging.INFO)
    results = [
        ImportResult(file="accounts.csv", inserted=1, errors=["bad row"]),
    ]
    log_import_results(results)
    assert "accounts.csv: 1 inserted" in caplog.text
    assert "bad row" in caplog.text
