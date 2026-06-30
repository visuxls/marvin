from decimal import Decimal

from models.summaries import HoldingSummary, TickerPrice
from services.symbols import to_market_symbol
from services.valuation import _price_lookup, summarize_net_worth_market, value_holdings


def test_to_market_symbol():
    assert to_market_symbol("voo") == "VOO"
    assert to_market_symbol("btc") == "BTC-USD"
    assert to_market_symbol("ETH") == "ETH-USD"
    assert to_market_symbol("sol") == "SOL-USD"


def test_price_lookup():
    prices = [
        TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
    ]
    assert _price_lookup(prices)["VOO"].price == Decimal("100")


def test_value_holdings_with_and_without_quotes():
    holdings = [
        HoldingSummary(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("2"),
            cost_basis=Decimal("100"),
        )
    ]
    valuations = value_holdings(
        holdings,
        [TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("150"))],
    )
    assert valuations[0].market_value == Decimal("300")

    missing = value_holdings(holdings, [])
    assert missing[0].error == "No quote returned for symbol"

    with_error = value_holdings(
        holdings,
        [TickerPrice(symbol="VOO", market_symbol="VOO", price=None, error="bad")],
    )
    assert with_error[0].error == "bad"


async def test_summarize_net_worth_market(monkeypatch):
    from models.summaries import BalanceSummary

    balances = [
        BalanceSummary(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2025-01-01",
            balance=Decimal("1000"),
        )
    ]
    holdings = [
        HoldingSummary(
            account_id="3",
            account_name="Brokerage",
            symbol="VOO",
            quantity=Decimal("2"),
            cost_basis=Decimal("100"),
        )
    ]

    async def fake_fetch(symbols):
        return [TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("150"))]

    monkeypatch.setattr("services.valuation.fetch_ticker_prices", fake_fetch)
    summary = await summarize_net_worth_market(balances, holdings)
    assert summary.net_worth_total == Decimal("1300")
    assert summary.holdings_missing_prices == 0

    async def missing_price_fetch(symbols):
        return [TickerPrice(symbol="VOO", market_symbol="VOO", price=None)]

    monkeypatch.setattr("services.valuation.fetch_ticker_prices", missing_price_fetch)
    summary = await summarize_net_worth_market(balances, holdings)
    assert summary.holdings_missing_prices == 1
    assert summary.investment_market_value_total == Decimal("200")
