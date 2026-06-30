import logging
import shutil
from pathlib import Path

from config import Settings, get_settings

logger = logging.getLogger(__name__)

SEED_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_CSV_FILES = ("accounts.csv", "balances.csv", "holdings.csv", "transactions.csv")


def ensure_demo_data(settings: Settings | None = None) -> list[Path]:
    """
    Copy demo templates for any missing CSV and profile files.

    Creates parent directories as needed. Existing files are never overwritten.
    ``marvin.db`` is not created here; it is populated by ``import_all()``.

    Args:
        settings: Optional settings override for tests.

    Returns:
        Paths of files created during this call.
    """
    resolved = settings or get_settings()
    resolved.imports_dir.mkdir(parents=True, exist_ok=True)
    resolved.profile_path.parent.mkdir(parents=True, exist_ok=True)
    resolved.db_path.parent.mkdir(parents=True, exist_ok=True)

    seeded: list[Path] = []

    for filename in _CSV_FILES:
        destination = resolved.imports_dir / filename
        if destination.exists():
            continue
        shutil.copy2(SEED_TEMPLATES_DIR / filename, destination)
        seeded.append(destination)
        logger.info("Seeded demo data: %s", destination)

    if not resolved.profile_path.exists():
        shutil.copy2(SEED_TEMPLATES_DIR / "profile.txt", resolved.profile_path)
        seeded.append(resolved.profile_path)
        logger.info("Seeded demo data: %s", resolved.profile_path)

    return seeded
