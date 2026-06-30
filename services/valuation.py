from decimal import Decimal

from models.summaries import (
    BalanceSummary,
    HoldingSummary,
    HoldingValuation,
    NetWorthMarketSummary,
    TickerPrice,
)
from services.market_data import fetch_ticker_prices


def _price_lookup(prices: list[TickerPrice]) -> dict[str, TickerPrice]:
    """
    Index ticker prices by normalized symbol.

    Args:
        prices: Quote rows returned from the market data service.

    Returns:
        Mapping of uppercase symbol to ticker price.
    """
    return {price.symbol.upper(): price for price in prices}


def value_holdings(
    holdings: list[HoldingSummary],
    prices: list[TickerPrice],
) -> list[HoldingValuation]:
    """
    Attach market prices and values to holdings.

    Args:
        holdings: Portfolio positions from the database.
        prices: Latest market prices for the holding symbols.

    Returns:
        Holdings enriched with price, market value, and quote errors.
    """
    quotes = _price_lookup(prices)
    valuations: list[HoldingValuation] = []

    for holding in holdings:
        quote = quotes.get(holding.symbol.upper())
        if quote is None:
            valuations.append(
                HoldingValuation(
                    account_id=holding.account_id,
                    account_name=holding.account_name,
                    symbol=holding.symbol,
                    quantity=holding.quantity,
                    cost_basis=holding.cost_basis,
                    price=None,
                    market_value=None,
                    error="No quote returned for symbol",
                )
            )
            continue

        market_value = holding.quantity * quote.price if quote.price is not None else None
        valuations.append(
            HoldingValuation(
                account_id=holding.account_id,
                account_name=holding.account_name,
                symbol=holding.symbol,
                quantity=holding.quantity,
                cost_basis=holding.cost_basis,
                price=quote.price,
                market_value=market_value,
                currency=quote.currency,
                error=quote.error,
            )
        )

    return valuations


async def summarize_net_worth_market(
    balances: list[BalanceSummary],
    holdings: list[HoldingSummary],
) -> NetWorthMarketSummary:
    """
    Calculate net worth using cash balances and live holding prices.

    Args:
        balances: Latest balance snapshots.
        holdings: Portfolio positions from the database.

    Returns:
        Net worth totals using market prices, falling back to cost basis when
        a quote is unavailable.
    """
    cash_total = sum((balance.balance for balance in balances), Decimal("0"))
    prices = await fetch_ticker_prices([holding.symbol for holding in holdings])
    quotes = _price_lookup(prices)

    investment_total = Decimal("0")
    missing_prices = 0
    for holding in holdings:
        quote = quotes.get(holding.symbol.upper())
        if quote is None or quote.price is None:
            missing_prices += 1
            investment_total += holding.quantity * holding.cost_basis
            continue
        investment_total += holding.quantity * quote.price

    return NetWorthMarketSummary(
        cash_and_credit_balance_total=cash_total,
        investment_market_value_total=investment_total,
        net_worth_total=cash_total + investment_total,
        accounts_with_balances=len(balances),
        accounts_with_holdings=len({holding.account_id for holding in holdings}),
        holdings_missing_prices=missing_prices,
    )
