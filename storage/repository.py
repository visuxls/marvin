import sqlite3

from models.finance import AccountRow, BalanceRow, HoldingRow, TransactionRow
from storage.db import utc_now_iso


def _now() -> str:
    """
    Get the current UTC timestamp.

    Returns:
        The current UTC time formatted as an ISO 8601 string.
    """
    return utc_now_iso()


def upsert_account(connection: sqlite3.Connection, row: AccountRow) -> bool:
    """
    Insert or update an account keyed by account_id.

    Args:
        connection: Open SQLite connection used for the write.
        row: Validated account row from accounts.csv.

    Returns:
        True if a new row was inserted, False if an existing row was updated.
    """
    existing = connection.execute(
        "SELECT 1 FROM accounts WHERE account_id = ?",
        (row.account_id,),
    ).fetchone()
    connection.execute(
        """
                INSERT INTO accounts (account_id, name, type, institution, note, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    name = excluded.name,
                    type = excluded.type,
                    institution = excluded.institution,
                    note = excluded.note,
                    updated_at = excluded.updated_at
        """,
        (
            row.account_id,
            row.name,
            row.type,
            row.institution,
            row.note,
            _now(),
        ),
    )
    return existing is None


def upsert_holding(connection: sqlite3.Connection, row: HoldingRow) -> bool:
    """
    Insert or update a holding keyed by account_id and symbol.

    Args:
        connection: Open SQLite connection used for the write.
        row: Validated holding row from holdings.csv.

    Returns:
        True if a new row was inserted, False if an existing row was updated.
    """
    existing = connection.execute(
        "SELECT 1 FROM holdings WHERE account_id = ? AND symbol = ?",
        (row.account_id, row.symbol),
    ).fetchone()
    connection.execute(
        """
                INSERT INTO holdings (account_id, symbol, quantity, cost_basis, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(account_id, symbol) DO UPDATE SET
                    quantity = excluded.quantity,
                    cost_basis = excluded.cost_basis,
                    updated_at = excluded.updated_at
        """,
        (
            row.account_id,
            row.symbol,
            str(row.quantity),
            str(row.cost_basis),
            _now(),
        ),
    )
    return existing is None


def upsert_balance(connection: sqlite3.Connection, row: BalanceRow) -> bool:
    """
    Insert or update a balance snapshot keyed by account_id and date.

    Args:
        connection: Open SQLite connection used for the write.
        row: Validated balance row from balances.csv.

    Returns:
        True if a new row was inserted, False if an existing row was updated.
    """
    existing = connection.execute(
        "SELECT 1 FROM balances WHERE account_id = ? AND date = ?",
        (row.account_id, row.balance_date.isoformat()),
    ).fetchone()
    connection.execute(
        """
                INSERT INTO balances (account_id, date, balance, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(account_id, date) DO UPDATE SET
                    balance = excluded.balance,
                    updated_at = excluded.updated_at
        """,
        (
            row.account_id,
            row.balance_date.isoformat(),
            str(row.balance),
            _now(),
        ),
    )
    return existing is None


def upsert_transaction(connection: sqlite3.Connection, row: TransactionRow) -> bool:
    """
    Insert or update a transaction keyed by transaction_id.

    Args:
        connection: Open SQLite connection used for the write.
        row: Validated transaction row from transactions.csv.

    Returns:
        True if a new row was inserted, False if an existing row was updated.
    """
    existing = connection.execute(
        "SELECT 1 FROM transactions WHERE transaction_id = ?",
        (row.transaction_id,),
    ).fetchone()
    connection.execute(
        """
                INSERT INTO transactions (
                    transaction_id,
                    account_id,
                    date,
                    amount,
                    category,
                    merchant,
                    description,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    account_id = excluded.account_id,
                    date = excluded.date,
                    amount = excluded.amount,
                    category = excluded.category,
                    merchant = excluded.merchant,
                    description = excluded.description,
                    updated_at = excluded.updated_at
        """,
        (
            row.transaction_id,
            row.account_id,
            row.transaction_date.isoformat(),
            str(row.amount),
            row.category,
            row.merchant,
            row.description,
            _now(),
        ),
    )
    return existing is None


def get_account_ids(connection: sqlite3.Connection) -> set[str]:
    """
    List all account IDs stored in the database.

    Args:
        connection: Open SQLite connection used for the lookup.

    Returns:
        A set of all account IDs currently stored in the database.
    """
    rows = connection.execute("SELECT account_id FROM accounts").fetchall()
    return {row["account_id"] for row in rows}
