"""
Map portfolio symbols to Yahoo Finance quote symbols.
"""

CRYPTO_SYMBOL_MAP = {
    "AAVE": "AAVE-USD",
    "ADA": "ADA-USD",
    "ALGO": "ALGO-USD",
    "ATOM": "ATOM-USD",
    "AVAX": "AVAX-USD",
    "BCH": "BCH-USD",
    "BNB": "BNB-USD",
    "BTC": "BTC-USD",
    "DOGE": "DOGE-USD",
    "DOT": "DOT-USD",
    "ETC": "ETC-USD",
    "ETH": "ETH-USD",
    "FIL": "FIL-USD",
    "HBAR": "HBAR-USD",
    "LINK": "LINK-USD",
    "LTC": "LTC-USD",
    "MATIC": "MATIC-USD",
    "NEAR": "NEAR-USD",
    "SHIB": "SHIB-USD",
    "SOL": "SOL-USD",
    "UNI": "UNI-USD",
    "USDC": "USDC-USD",
    "USDT": "USDT-USD",
    "XLM": "XLM-USD",
    "XRP": "XRP-USD",
}


def to_market_symbol(symbol: str) -> str:
    """
    Convert a portfolio symbol to a Yahoo Finance quote symbol.

    Args:
        symbol: Symbol from holdings data.

    Returns:
        Yahoo Finance-compatible quote symbol.
    """
    normalized = symbol.strip().upper()
    return CRYPTO_SYMBOL_MAP.get(normalized, normalized)
