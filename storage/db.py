import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    institution TEXT NOT NULL,
    note TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS holdings (
    account_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    quantity TEXT NOT NULL,
    cost_basis TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, symbol),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE IF NOT EXISTS balances (
    account_id TEXT NOT NULL,
    date TEXT NOT NULL,
    balance TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, date),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    date TEXT NOT NULL,
    amount TEXT NOT NULL,
    category TEXT,
    merchant TEXT,
    description TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_account_date
    ON transactions (account_id, date);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    messages_json TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    pinned INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def utc_now_iso() -> str:
    """
    Get the current UTC timestamp as ISO 8601.

    Returns:
        The current UTC time formatted as an ISO 8601 string.
    """
    return datetime.now(UTC).isoformat()


def _migrate_conversations_schema(connection: sqlite3.Connection) -> None:
    """
    Add conversation metadata columns to existing databases.
    """
    columns = {row[1] for row in connection.execute("PRAGMA table_info(conversations)").fetchall()}
    if "title" not in columns:
        connection.execute("ALTER TABLE conversations ADD COLUMN title TEXT NOT NULL DEFAULT ''")
    if "pinned" not in columns:
        connection.execute("ALTER TABLE conversations ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
    if "created_at" not in columns:
        connection.execute("ALTER TABLE conversations ADD COLUMN created_at TEXT")
        connection.execute(
            "UPDATE conversations SET created_at = updated_at WHERE created_at IS NULL"
        )


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """
    Open a SQLite connection and initialize the application schema.

    Args:
        db_path: Optional database path override. Defaults to configured
            `DB_PATH`.

    Returns:
        A SQLite connection with foreign keys enabled and row access by name.
    """
    resolved = db_path or get_settings().db_path
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(resolved)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    _migrate_conversations_schema(connection)
    return connection
