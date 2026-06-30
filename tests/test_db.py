import sqlite3
from pathlib import Path

from storage.db import connect


def test_connect_creates_schema(db_path: Path):
    connection = connect(db_path)
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "accounts" in tables
        assert "holdings" in tables
        assert "balances" in tables
        assert "transactions" in tables
        assert "conversations" in tables
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


def test_connect_migrates_legacy_conversations_table(tmp_path: Path):
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
                        CREATE TABLE conversations (
                            conversation_id TEXT PRIMARY KEY,
                            messages_json TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        )
            """
        )
        connection.execute(
            """
                        INSERT INTO conversations (conversation_id, messages_json, updated_at)
                        VALUES ('legacy', '[]', '2026-01-01T00:00:00+00:00')
            """
        )
        connection.commit()
    finally:
        connection.close()

    connection = connect(db_path)
    try:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(conversations)").fetchall()
        }
        assert "title" in columns
        assert "pinned" in columns
        assert "created_at" in columns
    finally:
        connection.close()


def test_connect_creates_parent_directory(tmp_path: Path):
    db_path = tmp_path / "nested" / "marvin.db"
    connection = connect(db_path)
    connection.close()
    assert db_path.exists()
