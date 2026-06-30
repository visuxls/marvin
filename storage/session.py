import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from storage.db import connect


@contextmanager
def db_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    """
    Open a database connection and close it when the context exits.

    Args:
        db_path: Path to the SQLite database file.

    Yields:
        Open SQLite connection.
    """
    connection = connect(db_path)
    try:
        yield connection
    finally:
        connection.close()
