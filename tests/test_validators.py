from datetime import date, datetime

import pytest

from models.validators import parse_flexible_date


def test_parse_flexible_date_from_date():
    value = date(2025, 1, 15)
    assert parse_flexible_date(value) == value


def test_parse_flexible_date_from_datetime():
    value = datetime(2025, 1, 15, 12, 30)
    assert parse_flexible_date(value) == date(2025, 1, 15)


def test_parse_flexible_date_iso():
    assert parse_flexible_date("2025-01-15") == date(2025, 1, 15)


@pytest.mark.parametrize(
    "value",
    [
        "01/15/2025",
        "01/15/25",
        "01-15-2025",
        "01-15-25",
        "15/01/2025",
        "15/01/25",
        "15-01-2025",
        "15-01-25",
    ],
)
def test_parse_flexible_date_common_formats(value: str):
    assert parse_flexible_date(value) == date(2025, 1, 15)


def test_parse_flexible_date_strips_whitespace():
    assert parse_flexible_date("  2025-01-15  ") == date(2025, 1, 15)


def test_parse_flexible_date_rejects_non_string():
    with pytest.raises(ValueError, match="date must be a string"):
        parse_flexible_date(123)


def test_parse_flexible_date_rejects_empty():
    with pytest.raises(ValueError, match="date is required"):
        parse_flexible_date("   ")


def test_parse_flexible_date_rejects_unknown_format():
    with pytest.raises(ValueError, match="unsupported date format"):
        parse_flexible_date("not-a-date")
