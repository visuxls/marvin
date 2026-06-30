import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from config import Settings, get_settings
from ingestion.csv_loader import load_csv_rows
from models.finance import AccountChildRow, AccountRow, BalanceRow, HoldingRow, TransactionRow
from storage.repository import (
    get_account_ids,
    upsert_account,
    upsert_balance,
    upsert_holding,
    upsert_transaction,
)
from storage.session import db_connection

RowT = TypeVar("RowT", bound=AccountChildRow)

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """
    Summary of a single CSV import run.
    """

    file: str
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def import_accounts(connection: sqlite3.Connection, imports_dir: Path) -> ImportResult:
    """
    Load accounts.csv and upsert each row into the database.

    Args:
        connection: Open SQLite connection used for the import.
        imports_dir: Directory containing accounts.csv.

    Returns:
        Import summary with insert/update counts and validation errors.
    """
    path = imports_dir / "accounts.csv"
    rows, errors = load_csv_rows(path, AccountRow)
    result = ImportResult(file=path.name, errors=errors)

    for row in rows:
        if upsert_account(connection, row):
            result.inserted += 1
        else:
            result.updated += 1

    return result


def _import_account_children(
    connection: sqlite3.Connection,
    imports_dir: Path,
    *,
    filename: str,
    model: type[RowT],
    upsert: Callable[[sqlite3.Connection, RowT], bool],
    row_label: Callable[[RowT], str],
) -> ImportResult:
    """
    Import a child CSV that references accounts by account ID.

    Args:
        connection: Open SQLite connection used for the import.
        imports_dir: Directory containing the CSV file.
        filename: CSV filename to import.
        model: Pydantic model used to validate each row.
        upsert: Repository upsert function for the row type.
        row_label: Builds an error label for skipped rows.

    Returns:
        Import summary with insert/update/skip counts and validation errors.
    """
    path = imports_dir / filename
    rows, errors = load_csv_rows(path, model)
    result = ImportResult(file=path.name, errors=errors)
    known_accounts = get_account_ids(connection)

    for row in rows:
        if row.account_id not in known_accounts:
            result.skipped += 1
            result.errors.append(
                f"{path.name}: skipped {row_label(row)} — unknown Account ID '{row.account_id}'"
            )
            continue

        if upsert(connection, row):
            result.inserted += 1
        else:
            result.updated += 1

    return result


def import_balances(connection: sqlite3.Connection, imports_dir: Path) -> ImportResult:
    """
    Load balances.csv and upsert each row into the database.

    Args:
        connection: Open SQLite connection used for the import.
        imports_dir: Directory containing balances.csv.

    Returns:
        Import summary with insert/update/skip counts and validation errors.
    """
    return _import_account_children(
        connection,
        imports_dir,
        filename="balances.csv",
        model=BalanceRow,
        upsert=upsert_balance,
        row_label=lambda row: str(row.balance_date),
    )


def import_holdings(connection: sqlite3.Connection, imports_dir: Path) -> ImportResult:
    """
    Load holdings.csv and upsert each row into the database.

    Args:
        connection: Open SQLite connection used for the import.
        imports_dir: Directory containing holdings.csv.

    Returns:
        Import summary with insert/update/skip counts and validation errors.
    """
    return _import_account_children(
        connection,
        imports_dir,
        filename="holdings.csv",
        model=HoldingRow,
        upsert=upsert_holding,
        row_label=lambda row: row.symbol,
    )


def import_transactions(connection: sqlite3.Connection, imports_dir: Path) -> ImportResult:
    """
    Load transactions.csv and upsert each row into the database.

    Args:
        connection: Open SQLite connection used for the import.
        imports_dir: Directory containing transactions.csv.

    Returns:
        Import summary with insert/update/skip counts and validation errors.
    """
    return _import_account_children(
        connection,
        imports_dir,
        filename="transactions.csv",
        model=TransactionRow,
        upsert=upsert_transaction,
        row_label=lambda row: row.transaction_id,
    )


def log_import_results(results: list[ImportResult]) -> None:
    """
    Log import summaries and row-level errors.

    Args:
        results: Import results for each CSV file.
    """
    for result in results:
        logger.info(
            "%s: %s inserted, %s updated, %s skipped",
            result.file,
            result.inserted,
            result.updated,
            result.skipped,
        )
        for error in result.errors:
            logger.warning("  %s", error)


def import_all(
    imports_dir: Path | None = None,
    db_path: Path | None = None,
    settings: Settings | None = None,
) -> list[ImportResult]:
    """
    Import accounts first, then balances, holdings, and transactions, and commit.

    Args:
        imports_dir: Optional imports directory override.
        db_path: Optional database path override.
        settings: Optional settings override for tests.

    Returns:
        Import results for accounts.csv, balances.csv, holdings.csv, and transactions.csv.
    """
    resolved = settings or get_settings()
    resolved_imports_dir = imports_dir or resolved.imports_dir
    resolved_db_path = db_path or resolved.db_path

    with db_connection(resolved_db_path) as connection:
        results = [
            import_accounts(connection, resolved_imports_dir),
            import_balances(connection, resolved_imports_dir),
            import_holdings(connection, resolved_imports_dir),
            import_transactions(connection, resolved_imports_dir),
        ]
        connection.commit()
        return results
