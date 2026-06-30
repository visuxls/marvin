import sqlite3
from dataclasses import dataclass

from pydantic_ai import RunContext

from agent.deps import CFODeps, with_db
from models.summaries import (
    AccountBreakdownSummary,
    AccountSummary,
    BalanceHistoryEntry,
    BalanceSummary,
    HoldingSummary,
    HoldingValuation,
    LiquiditySummary,
    MonthlyBurnSummary,
    NetWorthHistorySummary,
    NetWorthMarketSummary,
    NetWorthSummary,
    PortfolioAllocationSummary,
    RunwaySummary,
    SpendingBreakdownSummary,
    TickerPrice,
    TransactionsSummary,
    UnrealizedGainsSummary,
)
from services.analysis import (
    build_net_worth_history,
    summarize_account_breakdown,
    summarize_liquidity,
    summarize_portfolio_allocation,
    summarize_unrealized_gains,
)
from services.market_data import fetch_ticker_prices
from services.spending import (
    build_runway_summary,
    build_spending_breakdown,
    summarize_monthly_burn,
)
from services.valuation import summarize_net_worth_market, value_holdings
from storage import queries


@dataclass(frozen=True)
class _PortfolioSnapshot:
    """
    Accounts, balances, and holdings loaded in one DB pass.
    """

    accounts: list[AccountSummary]
    balances: list[BalanceSummary]
    holdings: list[HoldingSummary]


def _load_portfolio_snapshot(connection: sqlite3.Connection) -> _PortfolioSnapshot:
    """
    Load accounts, latest balances, and holdings from one connection.

    Args:
        connection: Open SQLite connection.

    Returns:
        Portfolio snapshot for liquidity and breakdown tools.
    """
    return _PortfolioSnapshot(
        accounts=queries.list_accounts(connection),
        balances=queries.get_latest_balances(connection),
        holdings=queries.get_holdings(connection),
    )


async def _value_holdings_at_market(
    holdings: list[HoldingSummary],
) -> list[HoldingValuation]:
    """
    Value holdings using latest market prices.

    Args:
        holdings: Holdings to value.

    Returns:
        Holdings with current price and market value when available.
    """
    if not holdings:
        return []

    prices = await fetch_ticker_prices([holding.symbol for holding in holdings])
    return value_holdings(holdings, prices)


def list_accounts(ctx: RunContext[CFODeps]) -> list[AccountSummary]:
    """
    List all financial accounts with their type and institution.

    Args:
        ctx: Agent run context with database dependencies.

    Returns:
        All accounts stored in Marvin.
    """
    with with_db(ctx.deps) as connection:
        return queries.list_accounts(connection)


def get_account_balances(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
) -> list[BalanceSummary]:
    """
    Get the latest balance snapshot for each account.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID to filter to a single account.

    Returns:
        Latest balances for one or all accounts.
    """
    with with_db(ctx.deps) as connection:
        return queries.get_latest_balances(connection, account_id=account_id)


def get_holdings(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
) -> list[HoldingSummary]:
    """
    Get investment holdings and their average cost per share.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID to filter to a single brokerage account.

    Returns:
        Holdings for one or all investment accounts.
    """
    with with_db(ctx.deps) as connection:
        return queries.get_holdings(connection, account_id=account_id)


async def get_ticker_prices(
    _ctx: RunContext[CFODeps],
    symbols: list[str],
) -> list[TickerPrice]:
    """
    Fetch latest market prices for ticker symbols.

    Args:
        _ctx: Agent run context with database dependencies.
        symbols: Ticker symbols to look up, such as VOO, MSFT, BTC, or ETH.

    Returns:
        Latest market prices from Yahoo Finance.
    """
    return await fetch_ticker_prices(symbols)


async def get_holdings_market_value(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
) -> list[HoldingValuation]:
    """
    Value holdings using latest market prices.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID to filter to a single brokerage account.

    Returns:
        Holdings with current price and market value when available.
    """
    with with_db(ctx.deps) as connection:
        holdings = queries.get_holdings(connection, account_id=account_id)

    return await _value_holdings_at_market(holdings)


async def get_net_worth_market_value(ctx: RunContext[CFODeps]) -> NetWorthMarketSummary:
    """
    Summarize net worth using cash balances and live holding market values.

    Args:
        ctx: Agent run context with database dependencies.

    Returns:
        Net worth totals using latest market prices for investments.
    """
    with with_db(ctx.deps) as connection:
        balances = queries.get_latest_balances(connection)
        holdings = queries.get_holdings(connection)

    return await summarize_net_worth_market(balances, holdings)


def get_net_worth_summary(ctx: RunContext[CFODeps]) -> NetWorthSummary:
    """
    Summarize net worth from latest balances and investment cost basis.

    Args:
        ctx: Agent run context with database dependencies.

    Returns:
        Aggregated net worth totals across cash, credit, and investments.
    """
    with with_db(ctx.deps) as connection:
        return queries.get_net_worth_summary(connection)


def get_user_profile(ctx: RunContext[CFODeps]) -> str:
    """
    Read the user's personal profile and life context.

    Args:
        ctx: Agent run context with profile path dependencies.

    Returns:
        Profile text including education, employment, and career goals.
    """
    from services.profile import format_profile_message

    return format_profile_message(ctx.deps.profile_path, context="tool")


def get_balance_history(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
) -> list[BalanceHistoryEntry]:
    """
    Get historical balance snapshots for one or all accounts.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID to filter to a single account.

    Returns:
        Balance snapshots ordered by date.
    """
    with with_db(ctx.deps) as connection:
        return queries.get_balance_history(connection, account_id=account_id)


def get_net_worth_over_time(ctx: RunContext[CFODeps]) -> NetWorthHistorySummary:
    """
    Track net worth over time using balance history and current holdings cost basis.

    Investment totals are held constant across dates because historical holding
    snapshots are not tracked yet.

    Args:
        ctx: Agent run context with database dependencies.

    Returns:
        Net worth points for each balance snapshot date.
    """
    with with_db(ctx.deps) as connection:
        balance_history = queries.get_balance_history(connection)
        net_worth = queries.get_net_worth_summary(connection)

    return build_net_worth_history(
        balance_history,
        net_worth.investment_cost_basis_total,
    )


async def get_portfolio_allocation(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
) -> PortfolioAllocationSummary:
    """
    Show portfolio allocation by symbol using current market values.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID to filter to a single brokerage account.

    Returns:
        Symbol weights as a percentage of total market value.
    """
    with with_db(ctx.deps) as connection:
        holdings = queries.get_holdings(connection, account_id=account_id)

    valuations = await _value_holdings_at_market(holdings)
    return summarize_portfolio_allocation(valuations)


async def get_unrealized_gains(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
) -> UnrealizedGainsSummary:
    """
    Calculate unrealized gain or loss for each holding at market prices.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID to filter to a single brokerage account.

    Returns:
        Per-holding and total unrealized gains or losses.
    """
    with with_db(ctx.deps) as connection:
        holdings = queries.get_holdings(connection, account_id=account_id)

    valuations = await _value_holdings_at_market(holdings)
    return summarize_unrealized_gains(valuations)


async def get_liquidity_summary(ctx: RunContext[CFODeps]) -> LiquiditySummary:
    """
    Summarize cash versus invested assets by liquidity category.

    Args:
        ctx: Agent run context with database dependencies.

    Returns:
        Liquidity breakdown across cash, taxable investments, retirement, and crypto.
    """
    with with_db(ctx.deps) as connection:
        snapshot = _load_portfolio_snapshot(connection)

    account_types = {account.account_id: account.type for account in snapshot.accounts}

    if not snapshot.holdings:
        return summarize_liquidity(snapshot.balances, [], account_types)

    valuations = await _value_holdings_at_market(snapshot.holdings)
    return summarize_liquidity(snapshot.balances, valuations, account_types)


async def get_account_breakdown(ctx: RunContext[CFODeps]) -> AccountBreakdownSummary:
    """
    Break down net worth by account using cash balances and market-valued holdings.

    Args:
        ctx: Agent run context with database dependencies.

    Returns:
        Per-account cash, investment value, and total net worth.
    """
    with with_db(ctx.deps) as connection:
        snapshot = _load_portfolio_snapshot(connection)

    if not snapshot.holdings:
        return summarize_account_breakdown(snapshot.accounts, snapshot.balances, [])

    valuations = await _value_holdings_at_market(snapshot.holdings)
    return summarize_account_breakdown(snapshot.accounts, snapshot.balances, valuations)


def get_transactions(
    ctx: RunContext[CFODeps],
    account_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
) -> TransactionsSummary:
    """
    List transactions with optional account and date filters.

    Args:
        ctx: Agent run context with database dependencies.
        account_id: Optional account ID filter.
        start_date: Optional inclusive start date (YYYY-MM-DD).
        end_date: Optional inclusive end date (YYYY-MM-DD).
        limit: Maximum number of transactions to return.

    Returns:
        Matching transactions ordered by date descending.
    """
    with with_db(ctx.deps) as connection:
        return queries.get_transactions(
            connection,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )


def get_spending_breakdown(
    ctx: RunContext[CFODeps],
    start_date: str | None = None,
    end_date: str | None = None,
    account_id: str | None = None,
) -> SpendingBreakdownSummary:
    """
    Summarize spending by category for a date range.

    Args:
        ctx: Agent run context with database dependencies.
        start_date: Optional inclusive start date (YYYY-MM-DD). Defaults to 90 days ago.
        end_date: Optional inclusive end date (YYYY-MM-DD). Defaults to today.
        account_id: Optional account ID filter.

    Returns:
        Category spending breakdown with income and outflow totals.
    """
    with with_db(ctx.deps) as connection:
        return build_spending_breakdown(
            connection,
            start_date=start_date,
            end_date=end_date,
            account_id=account_id,
        )


def get_monthly_burn(
    ctx: RunContext[CFODeps],
    months: int = 6,
    account_id: str | None = None,
) -> MonthlyBurnSummary:
    """
    Show monthly income, spending, and net burn over recent months.

    Args:
        ctx: Agent run context with database dependencies.
        months: Number of recent calendar months to include.
        account_id: Optional account ID filter.

    Returns:
        Monthly cash-flow trend with average monthly burn.
    """
    with with_db(ctx.deps) as connection:
        has_data = queries.count_transactions(connection) > 0
        points = queries.get_monthly_cashflow(connection, months, account_id=account_id)

    return summarize_monthly_burn(points, has_data=has_data)


def get_runway_months(ctx: RunContext[CFODeps], months: int = 6) -> RunwaySummary:
    """
    Estimate runway months from liquid cash and average monthly burn.

    Args:
        ctx: Agent run context with database dependencies.
        months: Number of recent months used to calculate average burn.

    Returns:
        Runway estimate using checking and savings balances.
    """
    with with_db(ctx.deps) as connection:
        return build_runway_summary(connection, months=months)
