from datetime import date
from decimal import Decimal

from models.finance import AccountRow, BalanceRow, HoldingRow


def test_account_row_from_csv_aliases():
    row = AccountRow.model_validate(
        {
            "Account ID": "1",
            "Name": "Checking",
            "Type": "Checking Account",
            "Institution": "Bank",
            "Note": "Primary",
        }
    )
    assert row.account_id == "1"
    assert row.note == "Primary"


def test_account_row_optional_note():
    row = AccountRow.model_validate(
        {
            "Account ID": "1",
            "Name": "Checking",
            "Type": "Checking Account",
            "Institution": "Bank",
        }
    )
    assert row.note is None


def test_balance_row_parses_flexible_date():
    row = BalanceRow.model_validate(
        {
            "Account ID": "1",
            "Date": "01/15/2025",
            "Balance": "1500.50",
        }
    )
    assert row.balance_date == date(2025, 1, 15)
    assert row.balance == Decimal("1500.50")


def test_holding_row_from_csv_aliases():
    row = HoldingRow.model_validate(
        {
            "Account ID": "3",
            "Symbol": "VOO",
            "Quantity": "10",
            "Cost Basis": "4000",
        }
    )
    assert row.symbol == "VOO"
    assert row.quantity == Decimal("10")
