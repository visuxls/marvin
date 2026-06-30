from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from models.summaries import TickerPrice
from services import market_data
from services.market_data import fetch_ticker_prices


async def test_fetch_ticker_prices_empty():
    assert await fetch_ticker_prices([]) == []


async def test_fetch_ticker_prices_uses_cache():
    market_data._price_cache["VOO"] = (
        datetime.now(UTC),
        TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
    )
    prices = await fetch_ticker_prices(["VOO"])
    assert prices[0].price == Decimal("100")


async def test_fetch_ticker_prices_expired_cache(monkeypatch):
    market_data._price_cache["VOO"] = (
        datetime.now(UTC) - timedelta(minutes=10),
        TickerPrice(symbol="VOO", market_symbol="VOO", price=Decimal("100")),
    )

    mock_ticker = MagicMock()
    mock_ticker.fast_info = {"lastPrice": 200.0, "currency": "USD"}
    mock_ticker.info = {}

    mock_tickers = MagicMock()
    mock_tickers.tickers = {"VOO": mock_ticker}

    with patch("services.market_data.yf.Tickers", return_value=mock_tickers):
        prices = await fetch_ticker_prices(["VOO"])
    assert prices[0].price == Decimal("200")


async def test_fetch_ticker_prices_falls_back_to_regular_market_price():
    mock_ticker = MagicMock()
    mock_ticker.fast_info = {}
    mock_ticker.info = {"regularMarketPrice": 150.0}

    mock_tickers = MagicMock()
    mock_tickers.tickers = {"VOO": mock_ticker}

    with patch("services.market_data.yf.Tickers", return_value=mock_tickers):
        prices = await fetch_ticker_prices(["VOO"])
    assert prices[0].price == Decimal("150")


async def test_fetch_ticker_prices_no_price_available():
    mock_ticker = MagicMock()
    mock_ticker.fast_info = {}
    mock_ticker.info = {}

    mock_tickers = MagicMock()
    mock_tickers.tickers = {"VOO": mock_ticker}

    with patch("services.market_data.yf.Tickers", return_value=mock_tickers):
        prices = await fetch_ticker_prices(["VOO"])
    assert prices[0].price is None
    assert prices[0].error == "No market price available for symbol"


async def test_fetch_ticker_prices_handles_exception():
    mock_tickers = MagicMock()
    mock_tickers.tickers = {"VOO": MagicMock()}
    mock_tickers.tickers["VOO"].fast_info.get.side_effect = RuntimeError("boom")

    with patch("services.market_data.yf.Tickers", return_value=mock_tickers):
        prices = await fetch_ticker_prices(["VOO"])
    assert prices[0].error == "boom"


def test_store_cached_price_skips_none():
    market_data._store_cached_price(TickerPrice(symbol="VOO", market_symbol="VOO", price=None))
    assert "VOO" not in market_data._price_cache
