from pathlib import Path

from ingestion.csv_loader import _is_blank_row, load_csv_rows
from models.finance import AccountRow


def test_is_blank_row():
    assert _is_blank_row({"a": "", "b": "  "}) is True
    assert _is_blank_row({"a": "x"}) is False


def test_load_csv_rows_missing_file(tmp_path: Path):
    rows, errors = load_csv_rows(tmp_path / "missing.csv", AccountRow)
    assert rows == []
    assert errors == ["missing.csv: file not found"]


def test_load_csv_rows_missing_header(tmp_path: Path):
    path = tmp_path / "accounts.csv"
    path.write_text("", encoding="utf-8")
    rows, errors = load_csv_rows(path, AccountRow)
    assert rows == []
    assert errors == ["accounts.csv: missing header row"]


def test_load_csv_rows_skips_blank_rows(tmp_path: Path):
    path = tmp_path / "accounts.csv"
    path.write_text(
        "Account ID,Name,Type,Institution\n1,Checking,Checking Account,Bank\n,,,\n",
        encoding="utf-8",
    )
    rows, errors = load_csv_rows(path, AccountRow)
    assert len(rows) == 1
    assert errors == []


def test_load_csv_rows_collects_validation_errors(tmp_path: Path):
    path = tmp_path / "accounts.csv"
    path.write_text(
        "Account ID,Name,Type,Institution\n1,Missing\n",
        encoding="utf-8",
    )
    rows, errors = load_csv_rows(path, AccountRow)
    assert rows == []
    assert len(errors) >= 1


def test_load_csv_rows_valid_file(imports_dir: Path):
    rows, errors = load_csv_rows(imports_dir / "accounts.csv", AccountRow)
    assert len(rows) == 2
    assert errors == []
