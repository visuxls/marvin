import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from config import Settings, get_settings
from storage.session import db_connection


@dataclass
class CFODeps:
    """
    Dependencies available to Marvin's agent tools.
    """

    db_path: Path
    profile_path: Path


def build_deps(settings: Settings | None = None) -> CFODeps:
    """
    Build default agent dependencies from application settings.

    Args:
        settings: Optional settings override for tests.

    Returns:
        Dependency container for agent tool calls.
    """
    resolved = settings or get_settings()
    return CFODeps(
        db_path=resolved.db_path,
        profile_path=resolved.profile_path,
    )


@contextmanager
def with_db(deps: CFODeps) -> Iterator[sqlite3.Connection]:
    """
    Open a database connection scoped to agent tool execution.

    Args:
        deps: Agent dependency container.

    Yields:
        Open SQLite connection.
    """
    with db_connection(deps.db_path) as connection:
        yield connection
