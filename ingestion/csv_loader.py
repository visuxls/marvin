import csv
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _is_blank_row(row: dict[str, str]) -> bool:
    """
    Check whether a CSV row contains no meaningful data.

    Args:
        row: A CSV row mapping column names to string values.

    Returns:
        True when every cell in the row is empty or whitespace.
    """
    return not any(value.strip() for value in row.values())


def load_csv_rows(path: Path, model: type[T]) -> tuple[list[T], list[str]]:
    """
    Read a CSV file and validate each row against a Pydantic model.

    Blank rows are skipped. Invalid rows are collected without stopping
    validation of the remaining file.

    Args:
        path: Path to the CSV file to read.
        model: Pydantic model class used to validate each row.

    Returns:
        A tuple containing validated rows and human-readable error messages.
    """
    if not path.exists():
        return [], [f"{path.name}: file not found"]

    errors: list[str] = []
    rows: list[T] = []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [], [f"{path.name}: missing header row"]

        for line_number, raw_row in enumerate(reader, start=2):
            if _is_blank_row(raw_row):
                continue

            try:
                rows.append(model.model_validate(raw_row))
            except ValidationError as exc:
                for error in exc.errors():
                    location = ".".join(str(part) for part in error["loc"])
                    errors.append(f"{path.name} row {line_number}: {location}: {error['msg']}")

    return rows, errors
