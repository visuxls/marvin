from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from agent.deps import build_deps
from agent.tools import (
    get_account_balances,
    get_account_breakdown,
    get_balance_history,
    get_holdings,
    get_holdings_market_value,
    get_liquidity_summary,
    get_monthly_burn,
    get_net_worth_market_value,
    get_net_worth_over_time,
    get_net_worth_summary,
    get_portfolio_allocation,
    get_runway_months,
    get_spending_breakdown,
    get_ticker_prices,
    get_transactions,
    get_unrealized_gains,
    get_user_profile,
    list_accounts,
)
from config import Settings
from ingestion.importer import import_all
from models.summaries import MonthlyBurnPoint, TickerPrice


@pytest.fixture
def tool_ctx(test_settings: Settings):
    import_all(settings=test_settings)
    deps = build_deps(test_settings)
    ctx = MagicMock()
    ctx.deps = deps
    return ctx


def test_list_accounts(tool_ctx):
    accounts = list_accounts(tool_ctx)
    assert len(accounts) == 2


def test_get_account_balances_all_and_filtered(tool_ctx):
    balances = get_account_balances(tool_ctx)
    assert len(balances) == 1
    filtered = get_account_balances(tool_ctx, account_id="1")
    assert len(filtered) == 1


def test_get_holdings_all_and_filtered(tool_ctx):
    holdings = get_holdings(tool_ctx)
    assert len(holdings) == 2
    filtered = get_holdings(tool_ctx, account_id="3")
    assert len(filtered) == 2


async def test_get_ticker_prices(monkeypatch):
    async def fake_fetch(symbols):
        return [TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100"))]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    prices = await get_ticker_prices(MagicMock(), ["VOO"])
    assert prices[0].price == Decimal("100")


async def test_get_holdings_market_value(tool_ctx, monkeypatch):
    async def fake_fetch(symbols):
        return [
            TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
            TickerPrice(symbol="BTC", market_symbol="BTC-USD", price=Decimal("50000")),
        ]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    valuations = await get_holdings_market_value(tool_ctx)
    assert len(valuations) == 2


async def test_get_holdings_market_value_empty(tool_ctx, monkeypatch):
    _ = tool_ctx.deps.db_path  # ensure db exists
    from storage.session import db_connection

    with db_connection(tool_ctx.deps.db_path) as connection:
        connection.execute("DELETE FROM holdings")
        connection.commit()
    assert await get_holdings_market_value(tool_ctx) == []


async def test_get_net_worth_market_value(tool_ctx, monkeypatch):
    async def fake_fetch(symbols):
        return [
            TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
            TickerPrice(symbol="BTC", market_symbol="BTC-USD", price=Decimal("50000")),
        ]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    summary = await get_net_worth_market_value(tool_ctx)
    assert summary.net_worth_total > Decimal("0")


def test_get_net_worth_summary(tool_ctx):
    summary = get_net_worth_summary(tool_ctx)
    assert summary.net_worth_total == Decimal("31000.00")


def test_get_user_profile_with_and_without(tool_ctx, tmp_path):
    assert "Age: 30" in get_user_profile(tool_ctx)
    tool_ctx.deps.profile_path = tmp_path / "missing.txt"
    assert "No user profile found" in get_user_profile(tool_ctx)


def test_get_balance_history_all_and_filtered(tool_ctx):
    history = get_balance_history(tool_ctx)
    assert len(history) == 2
    filtered = get_balance_history(tool_ctx, account_id="1")
    assert len(filtered) == 2


def test_get_net_worth_over_time(tool_ctx):
    summary = get_net_worth_over_time(tool_ctx)
    assert len(summary.points) == 2
    assert summary.points[-1].net_worth_total == Decimal("31000.00")


async def test_get_portfolio_allocation(tool_ctx, monkeypatch):
    async def fake_fetch(symbols):
        return [
            TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
            TickerPrice(symbol="BTC", market_symbol="BTC-USD", price=Decimal("50000")),
        ]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    summary = await get_portfolio_allocation(tool_ctx)
    assert summary.total_market_value > Decimal("0")
    assert len(summary.slices) == 2


async def test_get_unrealized_gains(tool_ctx, monkeypatch):
    async def fake_fetch(symbols):
        return [
            TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
            TickerPrice(symbol="BTC", market_symbol="BTC-USD", price=Decimal("50000")),
        ]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    summary = await get_unrealized_gains(tool_ctx)
    assert summary.total_cost_basis == Decimal("29000.00")
    assert len(summary.holdings) == 2


async def test_get_liquidity_summary(tool_ctx, monkeypatch):
    async def fake_fetch(symbols):
        return [
            TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
            TickerPrice(symbol="BTC", market_symbol="BTC-USD", price=Decimal("50000")),
        ]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    summary = await get_liquidity_summary(tool_ctx)
    assert summary.total > Decimal("0")
    assert summary.categories


async def test_get_liquidity_summary_without_holdings(tool_ctx, monkeypatch):
    from storage.session import db_connection

    with db_connection(tool_ctx.deps.db_path) as connection:
        connection.execute("DELETE FROM holdings")
        connection.commit()
    summary = await get_liquidity_summary(tool_ctx)
    assert summary.total == Decimal("2000.00")


async def test_get_account_breakdown(tool_ctx, monkeypatch):
    async def fake_fetch(symbols):
        return [
            TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
            TickerPrice(symbol="BTC", market_symbol="BTC-USD", price=Decimal("50000")),
        ]

    monkeypatch.setattr("agent.tools.fetch_ticker_prices", fake_fetch)
    summary = await get_account_breakdown(tool_ctx)
    assert summary.net_worth_total > Decimal("0")
    assert len(summary.accounts) == 2


async def test_get_account_breakdown_without_holdings(tool_ctx, monkeypatch):
    from storage.session import db_connection

    with db_connection(tool_ctx.deps.db_path) as connection:
        connection.execute("DELETE FROM holdings")
        connection.commit()
    summary = await get_account_breakdown(tool_ctx)
    assert summary.net_worth_total == Decimal("2000.00")
    assert len(summary.accounts) == 1


def test_get_transactions(tool_ctx):
    summary = get_transactions(tool_ctx, start_date="2026-04-01", end_date="2026-06-30")
    assert summary.has_data is True
    assert summary.total_count == 3


def test_get_spending_breakdown(tool_ctx):
    summary = get_spending_breakdown(
        tool_ctx,
        start_date="2026-04-01",
        end_date="2026-06-30",
    )
    assert summary.has_data is True
    assert summary.total_spending == Decimal("1285.50")
    assert summary.total_income == Decimal("3500.00")


def test_get_monthly_burn(tool_ctx):
    summary = get_monthly_burn(tool_ctx, months=6)
    assert summary.has_data is True
    assert len(summary.points) == 3


def test_get_runway_months(tool_ctx):
    summary = get_runway_months(tool_ctx, months=6)
    assert summary.has_data is True
    assert summary.liquid_cash == Decimal("2000.00")
    assert summary.runway_months is None
    assert summary.note is not None


def test_get_runway_months_with_positive_burn(tool_ctx, monkeypatch):
    def fake_cashflow(connection, months, account_id=None):
        return [
            MonthlyBurnPoint(
                month="2026-05",
                spending=Decimal("3000"),
                income=Decimal("1000"),
                net_burn=Decimal("2000"),
            ),
            MonthlyBurnPoint(
                month="2026-06",
                spending=Decimal("2500"),
                income=Decimal("500"),
                net_burn=Decimal("2000"),
            ),
        ]

    monkeypatch.setattr("agent.tools.queries.get_monthly_cashflow", fake_cashflow)
    summary = get_runway_months(tool_ctx, months=2)
    assert summary.runway_months == Decimal("1.0")
    assert summary.note is None


def test_get_runway_months_without_transactions(test_settings: Settings):
    imports_dir = test_settings.imports_dir
    (imports_dir / "transactions.csv").unlink()
    import_all(settings=test_settings)
    deps = build_deps(test_settings)
    ctx = MagicMock()
    ctx.deps = deps
    summary = get_runway_months(ctx)
    assert summary.has_data is False
    assert summary.note is not None
