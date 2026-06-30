import logging
from pathlib import Path

from scripts import import_data


def test_import_data_main(imports_dir: Path, db_path: Path, monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(
        "sys.argv",
        ["import_data", "--imports-dir", str(imports_dir), "--db-path", str(db_path)],
    )
    import_data.main()
    assert any("accounts.csv" in record.message for record in caplog.records)


def test_import_data_main_with_args(imports_dir: Path, db_path: Path, monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(
        "sys.argv",
        [
            "import_data",
            "--imports-dir",
            str(imports_dir),
            "--db-path",
            str(db_path),
        ],
    )
    import_data.main()
    assert any("accounts.csv" in record.message for record in caplog.records)
