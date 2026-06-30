import sqlite3
from datetime import date, timedelta
from decimal import Decimal

from models.summaries import (
    BalanceSummary,
    CategorySpending,
    MonthlyBurnPoint,
    MonthlyBurnSummary,
    RunwaySummary,
    SpendingBreakdownSummary,
)
from services.analysis import account_type_category
from storage import queries


def summarize_spending_breakdown(
    categories: list[CategorySpending],
    *,
    period_start: str,
    period_end: str,
    total_income: Decimal,
    has_data: bool,
) -> SpendingBreakdownSummary:
    """
    Build a category spending breakdown with percentage weights.

    Args:
        categories: Category totals for the period.
        period_start: Inclusive start date (YYYY-MM-DD).
        period_end: Inclusive end date (YYYY-MM-DD).
        total_income: Total inflows in the period.
        has_data: Whether any transactions exist in the database.

    Returns:
        Spending breakdown with weighted categories.
    """
    total_spending = sum((category.amount for category in categories), Decimal("0"))
    weighted_categories: list[CategorySpending] = []
    for category in categories:
        weight_pct = (
            (category.amount / total_spending * Decimal("100")).quantize(Decimal("0.01"))
            if total_spending > 0
            else Decimal("0")
        )
        weighted_categories.append(
            CategorySpending(
                category=category.category,
                amount=category.amount,
                transaction_count=category.transaction_count,
                weight_pct=weight_pct,
            )
        )

    return SpendingBreakdownSummary(
        period_start=period_start,
        period_end=period_end,
        total_spending=total_spending,
        total_income=total_income,
        categories=weighted_categories,
        has_data=has_data,
    )


def summarize_monthly_burn(points: list[MonthlyBurnPoint], *, has_data: bool) -> MonthlyBurnSummary:
    """
    Summarize monthly burn from cash-flow points.

    Args:
        points: Monthly income, spending, and net burn points.
        has_data: Whether any transactions exist in the database.

    Returns:
        Monthly burn summary with average net outflow.
    """
    if not points:
        return MonthlyBurnSummary(
            points=[],
            average_monthly_burn=Decimal("0"),
            has_data=has_data,
        )

    average_monthly_burn = (
        sum((point.net_burn for point in points), Decimal("0")) / Decimal(len(points))
    ).quantize(Decimal("0.01"))
    return MonthlyBurnSummary(
        points=points,
        average_monthly_burn=average_monthly_burn,
        has_data=has_data,
    )


def calculate_runway(liquid_cash: Decimal, average_monthly_burn: Decimal) -> Decimal | None:
    """
    Estimate runway months from liquid cash and average monthly burn.

    Args:
        liquid_cash: Cash available in checking and savings accounts.
        average_monthly_burn: Average monthly net outflow (positive = spending).

    Returns:
        Months of runway, or None when burn is zero or negative.
    """
    if average_monthly_burn <= 0:
        return None
    return (liquid_cash / average_monthly_burn).quantize(Decimal("0.1"))


def sum_liquid_cash(
    balances: list[BalanceSummary],
    account_types: dict[str, str],
) -> Decimal:
    """
    Sum balances in checking and savings accounts.

    Args:
        balances: Latest balance snapshots.
        account_types: Account ID to account type mapping.

    Returns:
        Total liquid cash balance.
    """
    total = Decimal("0")
    for balance in balances:
        account_type = account_types.get(balance.account_id, balance.account_type)
        if account_type_category(account_type) == "cash":
            total += balance.balance
    return total


def build_spending_breakdown(
    connection: sqlite3.Connection,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    account_id: str | None = None,
) -> SpendingBreakdownSummary:
    """
    Load and summarize spending by category for a date range.

    Args:
        connection: Open SQLite connection.
        start_date: Optional inclusive start date (YYYY-MM-DD). Defaults to 90 days ago.
        end_date: Optional inclusive end date (YYYY-MM-DD). Defaults to today.
        account_id: Optional account ID filter.

    Returns:
        Category spending breakdown with income and outflow totals.
    """
    resolved_end = end_date or date.today().isoformat()
    resolved_start = start_date or (date.today() - timedelta(days=90)).isoformat()
    has_data = queries.count_transactions(connection) > 0
    categories = queries.get_spending_by_category(
        connection,
        resolved_start,
        resolved_end,
        account_id=account_id,
    )
    total_income = queries.get_period_income(
        connection,
        resolved_start,
        resolved_end,
        account_id=account_id,
    )
    return summarize_spending_breakdown(
        categories,
        period_start=resolved_start,
        period_end=resolved_end,
        total_income=total_income,
        has_data=has_data,
    )


def build_runway_summary(
    connection: sqlite3.Connection,
    *,
    months: int = 6,
) -> RunwaySummary:
    """
    Estimate runway months from liquid cash and average monthly burn.

    Args:
        connection: Open SQLite connection.
        months: Number of recent months used to calculate average burn.

    Returns:
        Runway estimate using checking and savings balances.
    """
    has_data = queries.count_transactions(connection) > 0
    if not has_data:
        return RunwaySummary(
            liquid_cash=Decimal("0"),
            average_monthly_burn=Decimal("0"),
            runway_months=None,
            has_data=False,
            note=(
                "No transaction data loaded. Add transactions.csv to data/imports/ and re-import."
            ),
        )

    balances = queries.get_latest_balances(connection)
    accounts = queries.list_accounts(connection)
    points = queries.get_monthly_cashflow(connection, months)
    account_types = {account.account_id: account.type for account in accounts}
    liquid_cash = sum_liquid_cash(balances, account_types)

    burn_summary = summarize_monthly_burn(points, has_data=True)
    runway_months = calculate_runway(liquid_cash, burn_summary.average_monthly_burn)
    note = None
    if runway_months is None:
        note = (
            "Average monthly burn is zero or negative, "
            "so runway cannot be estimated from transactions."
        )

    return RunwaySummary(
        liquid_cash=liquid_cash,
        average_monthly_burn=burn_summary.average_monthly_burn,
        runway_months=runway_months,
        has_data=True,
        note=note,
    )
