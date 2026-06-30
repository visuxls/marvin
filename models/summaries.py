from decimal import Decimal

from pydantic import BaseModel


class AccountSummary(BaseModel):
    """
    Account metadata returned to the agent.
    """

    account_id: str
    name: str
    type: str
    institution: str
    note: str | None = None


class BalanceSummary(BaseModel):
    """
    Latest balance snapshot for an account.
    """

    account_id: str
    account_name: str
    account_type: str
    date: str
    balance: Decimal


class HoldingSummary(BaseModel):
    """
    Investment position for an account.
    """

    account_id: str
    account_name: str
    symbol: str
    quantity: Decimal
    cost_basis: Decimal  # Average cost per share or unit.


class NetWorthSummary(BaseModel):
    """
    High-level net worth breakdown.
    """

    cash_and_credit_balance_total: Decimal
    investment_cost_basis_total: Decimal
    net_worth_total: Decimal
    accounts_with_balances: int
    accounts_with_holdings: int


class TickerPrice(BaseModel):
    """
    Latest market price for a ticker symbol.
    """

    symbol: str
    market_symbol: str
    price: Decimal | None
    currency: str = "USD"
    error: str | None = None


class HoldingValuation(BaseModel):
    """
    Holding valued with the latest market price when available.
    """

    account_id: str
    account_name: str
    symbol: str
    quantity: Decimal
    cost_basis: Decimal
    price: Decimal | None
    market_value: Decimal | None
    currency: str = "USD"
    error: str | None = None


class NetWorthMarketSummary(BaseModel):
    """
    Net worth using latest market prices for holdings.
    """

    cash_and_credit_balance_total: Decimal
    investment_market_value_total: Decimal
    net_worth_total: Decimal
    accounts_with_balances: int
    accounts_with_holdings: int
    holdings_missing_prices: int


class BalanceHistoryEntry(BaseModel):
    """
    A single balance snapshot in account history.
    """

    account_id: str
    account_name: str
    account_type: str
    date: str
    balance: Decimal


class NetWorthHistoryPoint(BaseModel):
    """
    Net worth totals at a historical balance snapshot date.
    """

    date: str
    cash_and_credit_total: Decimal
    investment_cost_basis_total: Decimal
    net_worth_total: Decimal


class NetWorthHistorySummary(BaseModel):
    """
    Net worth over time from balance history and current holdings cost basis.
    """

    points: list[NetWorthHistoryPoint]
    investment_values_are_current_snapshot: bool = True


class AllocationSlice(BaseModel):
    """
    Portfolio weight for a single symbol.
    """

    symbol: str
    market_value: Decimal
    weight_pct: Decimal


class PortfolioAllocationSummary(BaseModel):
    """
    Holdings allocation by symbol using market values.
    """

    total_market_value: Decimal
    slices: list[AllocationSlice]
    holdings_missing_prices: int


class UnrealizedGain(BaseModel):
    """
    Unrealized gain or loss for a single holding.
    """

    account_id: str
    account_name: str
    symbol: str
    cost_basis: Decimal  # Average cost per share or unit.
    market_value: Decimal | None
    gain_loss: Decimal | None
    gain_loss_pct: Decimal | None
    error: str | None = None


class UnrealizedGainsSummary(BaseModel):
    """
    Aggregate unrealized gains across all holdings.
    """

    holdings: list[UnrealizedGain]
    total_cost_basis: Decimal
    total_market_value: Decimal | None
    total_gain_loss: Decimal | None


class LiquidityCategorySummary(BaseModel):
    """
    Balance sheet slice grouped by liquidity category.
    """

    category: str
    amount: Decimal
    weight_pct: Decimal


class LiquiditySummary(BaseModel):
    """
    Cash vs invested assets grouped by liquidity category.
    """

    total: Decimal
    categories: list[LiquidityCategorySummary]


class AccountBreakdown(BaseModel):
    """
    Net worth attributed to a single account.
    """

    account_id: str
    account_name: str
    account_type: str
    cash_balance: Decimal
    investment_value: Decimal
    total: Decimal


class AccountBreakdownSummary(BaseModel):
    """
    Net worth split across accounts.
    """

    accounts: list[AccountBreakdown]
    net_worth_total: Decimal


class TransactionSummary(BaseModel):
    """
    A single transaction joined with account metadata.
    """

    transaction_id: str
    account_id: str
    account_name: str
    date: str
    amount: Decimal
    category: str | None = None
    merchant: str | None = None
    description: str | None = None


class TransactionsSummary(BaseModel):
    """
    Filtered transaction list with availability metadata.
    """

    transactions: list[TransactionSummary]
    total_count: int
    has_data: bool


class CategorySpending(BaseModel):
    """
    Spending total for a single category.
    """

    category: str
    amount: Decimal
    transaction_count: int
    weight_pct: Decimal


class SpendingBreakdownSummary(BaseModel):
    """
    Income and spending breakdown by category for a date range.
    """

    period_start: str
    period_end: str
    total_spending: Decimal
    total_income: Decimal
    categories: list[CategorySpending]
    has_data: bool


class MonthlyBurnPoint(BaseModel):
    """
    Monthly income, spending, and net burn.
    """

    month: str
    spending: Decimal
    income: Decimal
    net_burn: Decimal


class MonthlyBurnSummary(BaseModel):
    """
    Monthly cash-flow trend with average burn.
    """

    points: list[MonthlyBurnPoint]
    average_monthly_burn: Decimal
    has_data: bool


class RunwaySummary(BaseModel):
    """
    Runway estimate from liquid cash and average monthly burn.
    """

    liquid_cash: Decimal
    average_monthly_burn: Decimal
    runway_months: Decimal | None
    has_data: bool
    note: str | None = None
