import argparse
import logging
from pathlib import Path

from config import get_settings
from ingestion.importer import import_all, log_import_results
from ingestion.seed import ensure_demo_data


def main() -> None:
    """
    Run the CSV import pipeline and print a summary for each file.

    Parses command-line arguments for the imports directory and database path,
    then prints insert, update, and skip counts along with any row errors.
    """
    parser = argparse.ArgumentParser(description="Import finance CSVs into Marvin.")
    parser.add_argument(
        "--imports-dir",
        type=Path,
        default=None,
        help="Directory containing accounts.csv, balances.csv, holdings.csv, and transactions.csv",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="SQLite database path",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    if args.imports_dir is not None:
        settings = settings.model_copy(update={"imports_dir": args.imports_dir})
    if args.db_path is not None:
        settings = settings.model_copy(update={"db_path": args.db_path})
    ensure_demo_data(settings)
    results = import_all(settings=settings)
    log_import_results(results)


if __name__ == "__main__":
    main()
