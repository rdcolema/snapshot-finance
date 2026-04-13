"""
Valuation dashboard with per-sector thresholds.

Thresholds are subjective and represent rough benchmarks for where multiples
start to look stretched vs. cheap. Users should tune these to match their own
investing philosophy -- a value investor's "stretched" is a growth investor's
"fair."

ETFs are excluded from valuation verdicts since fund-level multiples are
not directly comparable.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from positions.models import Position
from positions.services.fundamentals import get_fundamentals

# Per-sector forward P/E thresholds: (cheap_below, fair_below, stretched_above)
PE_THRESHOLDS = {
    "Information Technology": (18, 30, 30),
    "Communication Services": (15, 28, 28),
    "Consumer Discretionary": (15, 25, 25),
    "Health Care": (15, 25, 25),
    "Industrials": (12, 22, 22),
    "Financials": (10, 16, 16),
    "Consumer Staples": (14, 22, 22),
    "Energy": (8, 14, 14),
    "Utilities": (12, 18, 18),
    "Real Estate": (15, 25, 25),
    "Materials": (10, 18, 18),
    "Other": (12, 22, 22),
}

DEFAULT_THRESHOLD = (12, 22, 22)


def _get_verdict(value, sector):
    """Return 'cheap', 'fair', or 'stretched' for a given P/E and sector."""
    if value is None:
        return None
    cheap, fair, _ = PE_THRESHOLDS.get(sector, DEFAULT_THRESHOLD)
    if value < cheap:
        return "cheap"
    elif value <= fair:
        return "fair"
    else:
        return "stretched"


def get_valuation_data():
    """Build valuation table data for all positions."""
    positions = list(Position.objects.select_related("sector").values_list("symbol", "name", "sector__name"))
    if not positions:
        return []

    # Fetch fundamentals in parallel
    symbols = [p[0] for p in positions]
    fundamentals_map = {}
    with ThreadPoolExecutor(max_workers=min(10, len(symbols))) as executor:
        futures = {executor.submit(get_fundamentals, sym): sym for sym in symbols}
        for future in as_completed(futures):
            sym = futures[future]
            try:
                fundamentals_map[sym] = future.result() or {}
            except Exception:
                fundamentals_map[sym] = {}

    rows = []
    for symbol, name, sector in positions:
        fundamentals = fundamentals_map.get(symbol, {})

        # Skip ETF-like sectors for valuation verdict
        is_etf = sector.startswith("ETF") if sector else False

        forward_pe = fundamentals.get("forward_pe")
        trailing_pe = fundamentals.get("trailing_pe")
        price_to_sales = fundamentals.get("price_to_sales")
        ev_to_ebitda = fundamentals.get("ev_to_ebitda")

        verdict = None
        if not is_etf and forward_pe is not None:
            verdict = _get_verdict(forward_pe, sector)

        rows.append(
            {
                "symbol": symbol,
                "name": name,
                "sector": sector,
                "forward_pe": round(forward_pe, 1) if forward_pe else None,
                "trailing_pe": round(trailing_pe, 1) if trailing_pe else None,
                "price_to_sales": round(price_to_sales, 1) if price_to_sales else None,
                "ev_to_ebitda": round(ev_to_ebitda, 1) if ev_to_ebitda else None,
                "verdict": verdict,
                "is_etf": is_etf,
            }
        )

    return rows
