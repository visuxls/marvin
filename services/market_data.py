import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import yfinance as yf

from models.summaries import TickerPrice
from services.symbols import to_market_symbol

CACHE_TTL = timedelta(minutes=5)

_price_cache: dict[str, tuple[datetime, TickerPrice]] = {}


def _get_cached_price(symbol: str) -> TickerPrice | None:
    """
    Return a cached price when it is still fresh.

    Args:
        symbol: Normalized portfolio symbol.

    Returns:
        Cached ticker price, or None when missing or expired.
    """
    cached = _price_cache.get(symbol)
    if cached is None:
        return None
    cached_at, price = cached
    if datetime.now(UTC) - cached_at > CACHE_TTL:
        return None
    return price


def _store_cached_price(price: TickerPrice) -> None:
    """
    Store a successful quote in the in-memory cache.

    Args:
        price: Ticker price to cache.
    """
    if price.price is None:
        return
    _price_cache[price.symbol.upper()] = (datetime.now(UTC), price)


def _fetch_ticker_prices_sync(symbols: list[str]) -> list[TickerPrice]:
    """
    Fetch ticker prices synchronously using yfinance.

    Args:
        symbols: Portfolio symbols to look up.

    Returns:
        Latest price data for each requested symbol.
    """
    market_symbols = [to_market_symbol(symbol) for symbol in symbols]
    market_to_requested = {to_market_symbol(symbol): symbol for symbol in symbols}
    tickers = yf.Tickers(" ".join(market_symbols))

    prices: list[TickerPrice] = []
    for market_symbol in market_symbols:
        requested_symbol = market_to_requested[market_symbol]
        try:
            ticker = tickers.tickers[market_symbol]
            raw_price = ticker.fast_info.get("lastPrice")
            if raw_price is None:
                raw_price = ticker.info.get("regularMarketPrice")

            if raw_price is None:
                prices.append(
                    TickerPrice(
                        symbol=requested_symbol,
                        market_symbol=market_symbol,
                        price=None,
                        currency="USD",
                        error="No market price available for symbol",
                    )
                )
                continue

            prices.append(
                TickerPrice(
                    symbol=requested_symbol,
                    market_symbol=market_symbol,
                    price=Decimal(str(raw_price)),
                    currency=ticker.fast_info.get("currency") or "USD",
                )
            )
        except Exception as exc:
            prices.append(
                TickerPrice(
                    symbol=requested_symbol,
                    market_symbol=market_symbol,
                    price=None,
                    error=str(exc),
                )
            )

    return prices


async def fetch_ticker_prices(symbols: list[str]) -> list[TickerPrice]:
    """
    Fetch latest market prices for one or more ticker symbols.

    Uses yfinance against Yahoo Finance market data. Crypto symbols such as BTC
    and ETH are normalized to Yahoo's `-USD` pairs automatically.

    Args:
        symbols: Portfolio symbols to look up.

    Returns:
        Latest price data for each requested symbol.
    """
    if not symbols:
        return []

    unique_symbols = list(
        dict.fromkeys(symbol.strip().upper() for symbol in symbols if symbol.strip())
    )
    prices: list[TickerPrice] = []
    symbols_to_fetch: list[str] = []

    for symbol in unique_symbols:
        cached = _get_cached_price(symbol)
        if cached is not None:
            prices.append(cached)
        else:
            symbols_to_fetch.append(symbol)

    if symbols_to_fetch:
        fetched = await asyncio.to_thread(_fetch_ticker_prices_sync, symbols_to_fetch)
        for price in fetched:
            _store_cached_price(price)
            prices.append(price)

    prices.sort(key=lambda price: price.symbol)
    return prices
