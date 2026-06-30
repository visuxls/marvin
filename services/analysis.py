from collections import defaultdict
from decimal import Decimal

from models.summaries import (
    AccountBreakdown,
    AccountBreakdownSummary,
    AccountSummary,
    AllocationSlice,
    BalanceHistoryEntry,
    BalanceSummary,
    HoldingValuation,
    LiquidityCategorySummary,
    LiquiditySummary,
    NetWorthHistoryPoint,
    NetWorthHistorySummary,
    PortfolioAllocationSummary,
    UnrealizedGain,
    UnrealizedGainsSummary,
)


def account_type_category(account_type: str) -> str:
    """
    Map an account type string to a liquidity category.

    Args:
        account_type: Account type label from account metadata.

    Returns:
        A normalized liquidity category name.
    """
    lowered = account_type.lower()
    if any(term in lowered for term in ("checking", "savings", "cash")):
        return "cash"
    if any(term in lowered for term in ("roth", "ira", "401", "retirement")):
        return "retirement"
    if "crypto" in lowered:
        return "crypto"
    if any(term in lowered for term in ("credit", "card", "loan")):
        return "credit"
    if any(term in lowered for term in ("brokerage", "investment")):
        return "taxable_investments"
    return "other"


def build_net_worth_history(
    balance_history: list[BalanceHistoryEntry],
    investment_cost_basis: Decimal,
) -> NetWorthHistorySummary:
    """
    Build a net worth time series from balance snapshots.

    Investment totals use the current holdings cost basis at every point because
    historical holding snapshots are not tracked yet.

    Args:
        balance_history: Historical balance snapshots across accounts.
        investment_cost_basis: Current total investment cost basis.

    Returns:
        Net worth points for each balance snapshot date.
    """
    if not balance_history:
        return NetWorthHistorySummary(points=[])

    dates = sorted({entry.date for entry in balance_history})
    snapshots_by_account: dict[str, list[BalanceHistoryEntry]] = defaultdict(list)
    for entry in balance_history:
        snapshots_by_account[entry.account_id].append(entry)

    for account_entries in snapshots_by_account.values():
        account_entries.sort(key=lambda entry: entry.date)

    points: list[NetWorthHistoryPoint] = []
    for snapshot_date in dates:
        cash_total = Decimal("0")
        for account_entries in snapshots_by_account.values():
            latest: BalanceHistoryEntry | None = None
            for entry in account_entries:
                if entry.date <= snapshot_date:
                    latest = entry
            if latest is not None:
                cash_total += latest.balance

        points.append(
            NetWorthHistoryPoint(
                date=snapshot_date,
                cash_and_credit_total=cash_total,
                investment_cost_basis_total=investment_cost_basis,
                net_worth_total=cash_total + investment_cost_basis,
            )
        )

    return NetWorthHistorySummary(points=points)


def summarize_portfolio_allocation(
    valuations: list[HoldingValuation],
) -> PortfolioAllocationSummary:
    """
    Aggregate holdings market values into symbol weights.

    Args:
        valuations: Holdings valued at current market prices.

    Returns:
        Portfolio allocation slices sorted by descending weight.
    """
    totals_by_symbol: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    missing_prices = 0

    for valuation in valuations:
        if valuation.market_value is None:
            missing_prices += 1
            continue
        totals_by_symbol[valuation.symbol] += valuation.market_value

    total_market_value = sum(totals_by_symbol.values(), Decimal("0"))
    if total_market_value == 0:
        return PortfolioAllocationSummary(
            total_market_value=Decimal("0"),
            slices=[],
            holdings_missing_prices=missing_prices,
        )

    slices = [
        AllocationSlice(
            symbol=symbol,
            market_value=market_value,
            weight_pct=(market_value / total_market_value * Decimal("100")).quantize(
                Decimal("0.01")
            ),
        )
        for symbol, market_value in totals_by_symbol.items()
    ]
    slices.sort(key=lambda slice_: slice_.weight_pct, reverse=True)

    return PortfolioAllocationSummary(
        total_market_value=total_market_value,
        slices=slices,
        holdings_missing_prices=missing_prices,
    )


def summarize_unrealized_gains(
    valuations: list[HoldingValuation],
) -> UnrealizedGainsSummary:
    """
    Calculate unrealized gain or loss for each holding.

    ``cost_basis`` on each holding is the average cost per share or unit; totals
    and gain/loss math use ``quantity * cost_basis``.

    Args:
        valuations: Holdings valued at current market prices.

    Returns:
        Per-holding and total unrealized gain or loss.
    """
    gains: list[UnrealizedGain] = []
    total_cost_basis = Decimal("0")
    total_market_value = Decimal("0")
    has_missing_market_value = False

    for valuation in valuations:
        holding_cost_basis = valuation.quantity * valuation.cost_basis
        total_cost_basis += holding_cost_basis
        gain_loss: Decimal | None = None
        gain_loss_pct: Decimal | None = None

        if valuation.market_value is None:
            has_missing_market_value = True
            gains.append(
                UnrealizedGain(
                    account_id=valuation.account_id,
                    account_name=valuation.account_name,
                    symbol=valuation.symbol,
                    cost_basis=valuation.cost_basis,
                    market_value=None,
                    gain_loss=None,
                    gain_loss_pct=None,
                    error=valuation.error,
                )
            )
            continue

        total_market_value += valuation.market_value
        gain_loss = valuation.market_value - holding_cost_basis
        if holding_cost_basis != 0:
            gain_loss_pct = (gain_loss / holding_cost_basis * Decimal("100")).quantize(
                Decimal("0.01")
            )

        gains.append(
            UnrealizedGain(
                account_id=valuation.account_id,
                account_name=valuation.account_name,
                symbol=valuation.symbol,
                cost_basis=valuation.cost_basis,
                market_value=valuation.market_value,
                gain_loss=gain_loss,
                gain_loss_pct=gain_loss_pct,
                error=valuation.error,
            )
        )

    return UnrealizedGainsSummary(
        holdings=gains,
        total_cost_basis=total_cost_basis,
        total_market_value=None if has_missing_market_value else total_market_value,
        total_gain_loss=None if has_missing_market_value else total_market_value - total_cost_basis,
    )


def summarize_liquidity(
    balances: list[BalanceSummary],
    valuations: list[HoldingValuation],
    account_types: dict[str, str],
) -> LiquiditySummary:
    """
    Group balances and holdings into liquidity categories.

    Args:
        balances: Latest balance snapshots.
        valuations: Holdings valued at current market prices.
        account_types: Mapping of account ID to account type label.

    Returns:
        Liquidity breakdown by category.
    """
    totals_by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for balance in balances:
        category = account_type_category(balance.account_type)
        totals_by_category[category] += balance.balance

    for valuation in valuations:
        if valuation.market_value is None:
            continue
        account_type = account_types.get(valuation.account_id, "brokerage")
        category = account_type_category(account_type)
        totals_by_category[category] += valuation.market_value

    total = sum(totals_by_category.values(), Decimal("0"))
    if total == 0:
        return LiquiditySummary(total=Decimal("0"), categories=[])

    categories = [
        LiquidityCategorySummary(
            category=category,
            amount=amount,
            weight_pct=(amount / total * Decimal("100")).quantize(Decimal("0.01")),
        )
        for category, amount in totals_by_category.items()
    ]
    categories.sort(key=lambda category: category.weight_pct, reverse=True)

    return LiquiditySummary(total=total, categories=categories)


def summarize_account_breakdown(
    accounts: list[AccountSummary],
    balances: list[BalanceSummary],
    valuations: list[HoldingValuation],
) -> AccountBreakdownSummary:
    """
    Attribute cash and investments to each account.

    Args:
        accounts: All account metadata rows.
        balances: Latest balance snapshots.
        valuations: Holdings valued at current market prices.

    Returns:
        Per-account net worth breakdown.
    """
    balance_by_account = {balance.account_id: balance.balance for balance in balances}
    investment_by_account: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for valuation in valuations:
        if valuation.market_value is None:
            continue
        investment_by_account[valuation.account_id] += valuation.market_value

    breakdowns: list[AccountBreakdown] = []
    for account in accounts:
        cash_balance = balance_by_account.get(account.account_id, Decimal("0"))
        investment_value = investment_by_account.get(account.account_id, Decimal("0"))
        total = cash_balance + investment_value
        if cash_balance == 0 and investment_value == 0:
            continue
        breakdowns.append(
            AccountBreakdown(
                account_id=account.account_id,
                account_name=account.name,
                account_type=account.type,
                cash_balance=cash_balance,
                investment_value=investment_value,
                total=total,
            )
        )

    breakdowns.sort(key=lambda breakdown: breakdown.total, reverse=True)
    net_worth_total = sum((breakdown.total for breakdown in breakdowns), Decimal("0"))

    return AccountBreakdownSummary(accounts=breakdowns, net_worth_total=net_worth_total)
