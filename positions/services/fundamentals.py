import logging
import warnings

from django.core.cache import cache

from positions.services.quotes import _to_yf_symbol

logger = logging.getLogger(__name__)

FUNDAMENTALS_CACHE_TTL = 60 * 60 * 24  # 24 hours


def _fetch_fundamentals(symbol):
    """Fetch fundamental data for a symbol from yfinance .info (slow call)."""
    import yfinance as yf

    yf_symbol = _to_yf_symbol(symbol)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Timestamp.utcnow")
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info or {}
        return {
            "symbol": symbol,
            "long_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "forward_pe": info.get("forwardPE"),
            "trailing_pe": info.get("trailingPE"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),
            "dividend_yield": info.get("dividendYield"),
            "market_cap": info.get("marketCap"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        }
    except Exception:
        logger.exception("Failed to fetch fundamentals for %s", symbol)
        return None


def get_fundamentals(symbol):
    """Get fundamentals for a symbol, with 24h cache."""
    cache_key = f"fundamentals:{symbol.upper()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = _fetch_fundamentals(symbol)
    if result:
        cache.set(cache_key, result, FUNDAMENTALS_CACHE_TTL)
    return result
