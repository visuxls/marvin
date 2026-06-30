from datetime import date as Date
from datetime import datetime


def parse_flexible_date(value: object) -> Date:
    """
    Parse a date from common CSV formats.

    Args:
        value: Raw cell value from a CSV row.

    Returns:
        Parsed calendar date.

    Raises:
        ValueError: When the value cannot be parsed as a supported date format.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, Date):
        return value
    if not isinstance(value, str):
        raise ValueError("date must be a string")
    if not value.strip():
        raise ValueError("date is required")

    text = value.strip()

    try:
        return Date.fromisoformat(text)
    except ValueError:
        pass

    for fmt in (
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m-%d-%Y",
        "%m-%d-%y",
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"unsupported date format: {text!r}")
