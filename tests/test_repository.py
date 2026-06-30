from models.finance import AccountRow, BalanceRow, HoldingRow, TransactionRow
from storage.repository import (
    get_account_ids,
    upsert_account,
    upsert_balance,
    upsert_holding,
    upsert_transaction,
)
from storage.session import db_connection


def _account(account_id: str = "1") -> AccountRow:
    return AccountRow.model_validate(
        {
            "Account ID": account_id,
            "Name": "Checking",
            "Type": "Checking Account",
            "Institution": "Bank",
        }
    )


def test_upsert_account_insert_and_update(db_path):
    with db_connection(db_path) as connection:
        assert upsert_account(connection, _account()) is True
        assert upsert_account(connection, _account()) is False
        assert get_account_ids(connection) == {"1"}


def test_upsert_balance_and_holding(db_path):
    with db_connection(db_path) as connection:
        upsert_account(connection, _account("3"))
        balance = BalanceRow.model_validate(
            {"Account ID": "3", "Date": "2025-01-01", "Balance": "100"}
        )
        holding = HoldingRow.model_validate(
            {
                "Account ID": "3",
                "Symbol": "VOO",
                "Quantity": "1",
                "Cost Basis": "100",
            }
        )
        assert upsert_balance(connection, balance) is True
        assert upsert_balance(connection, balance) is False
        assert upsert_holding(connection, holding) is True
        assert upsert_holding(connection, holding) is False


def test_upsert_transaction(db_path):
    with db_connection(db_path) as connection:
        upsert_account(connection, _account())
        transaction = TransactionRow.model_validate(
            {
                "Transaction ID": "tx-1",
                "Account ID": "1",
                "Date": "2026-04-01",
                "Amount": "-50.00",
                "Category": "Groceries",
                "Merchant": "Store",
                "Description": "Test purchase",
            }
        )
        assert upsert_transaction(connection, transaction) is True
        assert upsert_transaction(connection, transaction) is False
