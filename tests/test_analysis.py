from decimal import Decimal

from models.summaries import (
    AccountSummary,
    BalanceHistoryEntry,
    BalanceSummary,
    HoldingValuation,
)
from services.analysis import (
    account_type_category,
    build_net_worth_history,
    summarize_account_breakdown,
    summarize_liquidity,
    summarize_portfolio_allocation,
    summarize_unrealized_gains,
)


def test_account_type_category():
    assert account_type_category("Checking Account") == "cash"
    assert account_type_category("Roth IRA Brokerage") == "retirement"
    assert account_type_category("Taxable Crypto Holdings") == "crypto"
    assert account_type_category("Taxable Brokerage") == "taxable_investments"
    assert account_type_category("Credit Card") == "credit"
    assert account_type_category("Something Else") == "other"


def test_build_net_worth_history():
    history = [
        BalanceHistoryEntry(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-01-15",
            balance=Decimal("1500.50"),
        ),
        BalanceHistoryEntry(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-02-01",
            balance=Decimal("2000.00"),
        ),
    ]
    summary = build_net_worth_history(history, Decimal("29000"))
    assert len(summary.points) == 2
    assert summary.points[0].net_worth_total == Decimal("30500.50")
    assert summary.points[1].net_worth_total == Decimal("31000.00")
    assert summary.investment_values_are_current_snapshot is True


def test_build_net_worth_history_multiple_accounts():
    history = [
        BalanceHistoryEntry(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-02-01",
            balance=Decimal("2000"),
        ),
        BalanceHistoryEntry(
            account_id="2",
            account_name="Savings",
            account_type="Savings Account",
            date="2025-03-01",
            balance=Decimal("500"),
        ),
    ]
    summary = build_net_worth_history(history, Decimal("0"))
    assert summary.points[0].cash_and_credit_total == Decimal("2000")
    assert summary.points[1].cash_and_credit_total == Decimal("2500")


def test_build_net_worth_history_empty():
    summary = build_net_worth_history([], Decimal("0"))
    assert summary.points == []


def test_summarize_portfolio_allocation():
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("10"),
            cost_basis=Decimal("4000"),
            price=Decimal("100"),
            market_value=Decimal("1000"),
        ),
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="BTC",
            quantity=Decimal("0.5"),
            cost_basis=Decimal("25000"),
            price=Decimal("50000"),
            market_value=Decimal("25000"),
        ),
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="ETH",
            quantity=Decimal("1"),
            cost_basis=Decimal("1000"),
            price=None,
            market_value=None,
            error="bad",
        ),
    ]
    summary = summarize_portfolio_allocation(valuations)
    assert summary.total_market_value == Decimal("26000")
    assert summary.holdings_missing_prices == 1
    assert summary.slices[0].symbol == "BTC"
    assert summary.slices[0].weight_pct == Decimal("96.15")


def test_summarize_portfolio_allocation_empty():
    summary = summarize_portfolio_allocation([])
    assert summary.total_market_value == Decimal("0")
    assert summary.slices == []


def test_summarize_unrealized_gains():
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("10"),
            cost_basis=Decimal("400"),
            price=Decimal("100"),
            market_value=Decimal("1000"),
        ),
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="BTC",
            quantity=Decimal("0.5"),
            cost_basis=Decimal("50000"),
            price=None,
            market_value=None,
            error="bad",
        ),
    ]
    summary = summarize_unrealized_gains(valuations)
    assert summary.total_cost_basis == Decimal("29000")
    assert summary.total_market_value is None
    assert summary.holdings[0].gain_loss == Decimal("-3000")
    assert summary.holdings[0].gain_loss_pct == Decimal("-75.00")


def test_summarize_liquidity():
    balances = [
        BalanceSummary(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-02-01",
            balance=Decimal("2000"),
        )
    ]
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("10"),
            cost_basis=Decimal("4000"),
            price=Decimal("100"),
            market_value=Decimal("1000"),
        )
    ]
    summary = summarize_liquidity(
        balances,
        valuations,
        {"1": "Checking Account", "3": "Taxable Brokerage"},
    )
    assert summary.total == Decimal("3000")
    assert len(summary.categories) == 2


def test_summarize_liquidity_empty():
    summary = summarize_liquidity([], [], {})
    assert summary.total == Decimal("0")
    assert summary.categories == []


def test_summarize_unrealized_gains_with_zero_cost_basis():
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("1"),
            cost_basis=Decimal("0"),
            price=Decimal("100"),
            market_value=Decimal("100"),
        )
    ]
    summary = summarize_unrealized_gains(valuations)
    assert summary.holdings[0].gain_loss_pct is None
    assert summary.total_gain_loss == Decimal("100")


def test_summarize_liquidity_skips_missing_prices():
    balances = [
        BalanceSummary(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-02-01",
            balance=Decimal("2000"),
        )
    ]
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="BTC",
            quantity=Decimal("0.5"),
            cost_basis=Decimal("25000"),
            price=None,
            market_value=None,
            error="bad",
        )
    ]
    summary = summarize_liquidity(
        balances,
        valuations,
        {"3": "Taxable Brokerage"},
    )
    assert summary.total == Decimal("2000")
    assert len(summary.categories) == 1


def test_summarize_account_breakdown_skips_missing_prices():
    accounts = [
        AccountSummary(
            account_id="3",
            name="Brokerage",
            type="Taxable Brokerage",
            institution="Robinhood",
        )
    ]
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="BTC",
            quantity=Decimal("0.5"),
            cost_basis=Decimal("25000"),
            price=None,
            market_value=None,
            error="bad",
        )
    ]
    summary = summarize_account_breakdown(accounts, [], valuations)
    assert summary.accounts == []
    assert summary.net_worth_total == Decimal("0")


def test_summarize_account_breakdown():
    accounts = [
        AccountSummary(
            account_id="1",
            name="Checking",
            type="Checking Account",
            institution="Bank",
        ),
        AccountSummary(
            account_id="3",
            name="Brokerage",
            type="Taxable Brokerage",
            institution="Robinhood",
        ),
    ]
    balances = [
        BalanceSummary(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-02-01",
            balance=Decimal("2000"),
        )
    ]
    valuations = [
        HoldingValuation(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("10"),
            cost_basis=Decimal("4000"),
            price=Decimal("100"),
            market_value=Decimal("1000"),
        )
    ]
    summary = summarize_account_breakdown(accounts, balances, valuations)
    assert summary.net_worth_total == Decimal("3000")
    assert len(summary.accounts) == 2
    assert summary.accounts[0].account_id == "1"
