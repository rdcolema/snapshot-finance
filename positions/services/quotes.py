import logging
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

from django.core.cache import cache

logger = logging.getLogger(__name__)

QUOTE_CACHE_TTL = 60 * 15  # 15 minutes

# Fidelity → Yahoo Finance symbol translation
SYMBOL_MAP = {
    "BRKB": "BRK-B",
    "BRK.B": "BRK-B",
    "BRKA": "BRK-A",
    "BRK.A": "BRK-A",
}


def _to_yf_symbol(symbol):
    return SYMBOL_MAP.get(symbol.upper(), symbol)


def _fetch_quote(symbol):
    """Fetch quote data for a single symbol from yfinance. Raises on transient errors."""
    import yfinance as yf

    yf_symbol = _to_yf_symbol(symbol)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Timestamp.utcnow")
        ticker = yf.Ticker(yf_symbol)
        info = ticker.fast_info
    return {
        "symbol": symbol,
        "price": Decimal(str(round(info.last_price, 4))) if info.last_price else None,
        "previous_close": Decimal(str(round(info.previous_close, 4))) if info.previous_close else None,
        "market_cap": info.market_cap if hasattr(info, "market_cap") else None,
        "fifty_two_week_low": Decimal(str(round(info.year_low, 4)))
        if hasattr(info, "year_low") and info.year_low
        else None,
        "fifty_two_week_high": Decimal(str(round(info.year_high, 4)))
        if hasattr(info, "year_high") and info.year_high
        else None,
    }


def _fetch_with_retry(symbol, max_retries=3):
    """Fetch with exponential backoff on transient errors."""
    for attempt in range(max_retries):
        try:
            return _fetch_quote(symbol)
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
            else:
                logger.exception("All retries exhausted for %s", symbol)
    return None


def get_quote(symbol):
    """Get quote for a single symbol, with caching."""
    cache_key = f"quote:{symbol.upper()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = _fetch_with_retry(symbol)
    if result:
        cache.set(cache_key, result, QUOTE_CACHE_TTL)
    return result


def get_quotes(symbols):
    """Fetch quotes for multiple symbols concurrently. Returns dict keyed by symbol."""
    results = {}
    to_fetch = []

    # Check cache first
    for sym in symbols:
        cache_key = f"quote:{sym.upper()}"
        cached = cache.get(cache_key)
        if cached is not None:
            results[sym.upper()] = cached
        else:
            to_fetch.append(sym)

    if not to_fetch:
        return results

    # Fetch remaining in thread pool
    with ThreadPoolExecutor(max_workers=min(10, len(to_fetch))) as executor:
        futures = {executor.submit(_fetch_with_retry, sym): sym for sym in to_fetch}
        for future in as_completed(futures):
            sym = futures[future]
            try:
                result = future.result()
                if result:
                    cache.set(f"quote:{sym.upper()}", result, QUOTE_CACHE_TTL)
                    results[sym.upper()] = result
            except Exception:
                logger.exception("Error fetching quote for %s", sym)

    return results
