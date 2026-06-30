from decimal import Decimal

import pytest

from config import Settings
from ingestion.importer import import_all
from storage import queries
from storage.session import db_connection


@pytest.fixture
def seeded_db(test_settings: Settings):
    import_all(settings=test_settings)
    return test_settings.db_path


def test_list_accounts(seeded_db):
    with db_connection(seeded_db) as connection:
        accounts = queries.list_accounts(connection)
    assert len(accounts) == 2
    assert accounts[0].name == "Brokerage"


def test_get_latest_balances_all_and_filtered(seeded_db):
    with db_connection(seeded_db) as connection:
        all_balances = queries.get_latest_balances(connection)
        filtered = queries.get_latest_balances(connection, account_id="1")
    assert len(all_balances) == 1
    assert all_balances[0].balance == Decimal("2000.00")
    assert len(filtered) == 1
    assert filtered[0].account_id == "1"


def test_get_holdings_all_and_filtered(seeded_db):
    with db_connection(seeded_db) as connection:
        all_holdings = queries.get_holdings(connection)
        filtered = queries.get_holdings(connection, account_id="3")
    assert len(all_holdings) == 2
    assert len(filtered) == 2
    assert {holding.symbol for holding in filtered} == {"VOO", "BTC"}


def test_get_net_worth_summary(seeded_db):
    with db_connection(seeded_db) as connection:
        summary = queries.get_net_worth_summary(connection)
    assert summary.cash_and_credit_balance_total == Decimal("2000.00")
    assert summary.investment_cost_basis_total == Decimal("29000.00")
    assert summary.net_worth_total == Decimal("31000.00")
    assert summary.accounts_with_balances == 1
    assert summary.accounts_with_holdings == 1


def test_get_balance_history_all_and_filtered(seeded_db):
    with db_connection(seeded_db) as connection:
        all_history = queries.get_balance_history(connection)
        filtered = queries.get_balance_history(connection, account_id="1")
    assert len(all_history) == 2
    assert all_history[0].date == "2025-01-15"
    assert all_history[1].balance == Decimal("2000.00")
    assert len(filtered) == 2


def test_count_transactions(seeded_db):
    with db_connection(seeded_db) as connection:
        assert queries.count_transactions(connection) == 3


def test_get_transactions(seeded_db):
    with db_connection(seeded_db) as connection:
        summary = queries.get_transactions(
            connection,
            start_date="2026-04-01",
            end_date="2026-06-30",
        )
        filtered = queries.get_transactions(connection, account_id="1", limit=1)
    assert summary.has_data is True
    assert summary.total_count == 3
    assert len(summary.transactions) == 3
    assert summary.transactions[0].amount == Decimal("-85.50")
    assert len(filtered.transactions) == 1


def test_get_spending_by_category(seeded_db):
    with db_connection(seeded_db) as connection:
        categories = queries.get_spending_by_category(
            connection,
            "2026-04-01",
            "2026-06-30",
        )
        filtered = queries.get_spending_by_category(
            connection,
            "2026-04-01",
            "2026-06-30",
            account_id="1",
        )
    assert len(categories) == 2
    assert categories[0].category == "Rent"
    assert categories[0].amount == Decimal("1200.00")
    assert filtered[0].amount == Decimal("1200.00")


def test_get_period_income(seeded_db):
    with db_connection(seeded_db) as connection:
        income = queries.get_period_income(connection, "2026-04-01", "2026-06-30")
        filtered = queries.get_period_income(
            connection,
            "2026-04-01",
            "2026-06-30",
            account_id="1",
        )
    assert income == Decimal("3500.00")
    assert filtered == Decimal("3500.00")


def test_get_monthly_cashflow(seeded_db):
    with db_connection(seeded_db) as connection:
        points = queries.get_monthly_cashflow(connection, months=6)
        filtered = queries.get_monthly_cashflow(connection, months=6, account_id="1")
    assert len(points) == 3
    assert points[0].month == "2026-04"
    assert points[-1].spending == Decimal("85.5")
    assert len(filtered) == 3
