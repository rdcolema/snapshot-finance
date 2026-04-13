import json
import logging
from decimal import Decimal

from positions.models import Account, Position
from positions.services.quotes import get_quotes

logger = logging.getLogger(__name__)


def _d(val, default="0"):
    """Safely convert to Decimal."""
    if val is None:
        return Decimal(default)
    return Decimal(str(val))


def get_enriched_positions(account_ids=None, sector_ids=None):
    """Get all positions enriched with live quote data."""
    qs = Position.objects.select_related("account", "sector").prefetch_related("themes", "lots")
    if account_ids:
        qs = qs.filter(account_id__in=account_ids)
    if sector_ids:
        qs = qs.filter(sector_id__in=sector_ids)

    positions = list(qs)
    if not positions:
        return []

    symbols = list({p.symbol for p in positions})
    quotes = get_quotes(symbols)

    enriched = []
    for pos in positions:
        quote = quotes.get(pos.symbol, {})
        price = _d(quote.get("price"))
        prev_close = _d(quote.get("previous_close"))
        shares = pos.shares
        cost_basis = pos.cost_basis
        avg_cost = pos.avg_cost
        mkt_value = shares * price if price else Decimal("0")
        day_change = price - prev_close if price and prev_close else Decimal("0")
        day_change_pct = (day_change / prev_close * 100) if prev_close and prev_close != 0 else Decimal("0")
        day_gain = shares * day_change
        total_gain = mkt_value - cost_basis if mkt_value and cost_basis else Decimal("0")
        total_return_pct = (total_gain / cost_basis * 100) if cost_basis and cost_basis != 0 else Decimal("0")

        enriched.append(
            {
                "id": pos.id,
                "symbol": pos.symbol,
                "name": pos.name,
                "sector": pos.sector.name if pos.sector else "-",
                "sector_id": pos.sector_id,
                "account": pos.account.name,
                "account_id": pos.account_id,
                "themes": [t.name for t in pos.themes.all()],
                "shares": shares,
                "avg_cost": avg_cost.quantize(Decimal("0.01")),
                "price": price.quantize(Decimal("0.01")) if price else None,
                "day_change": day_change.quantize(Decimal("0.01")),
                "day_change_pct": day_change_pct.quantize(Decimal("0.01")),
                "day_gain": day_gain.quantize(Decimal("0.01")),
                "mkt_value": mkt_value.quantize(Decimal("0.01")),
                "cost_basis": cost_basis.quantize(Decimal("0.01")),
                "total_gain": total_gain.quantize(Decimal("0.01")),
                "total_return_pct": total_return_pct.quantize(Decimal("0.01")),
                "target_weight_pct": pos.target_weight_pct,
                "thesis": pos.thesis,
                "thesis_updated_at": pos.thesis_updated_at,
                "has_quote": bool(quote),
            }
        )

    # Compute portfolio weight for each position
    total_value = sum(p["mkt_value"] for p in enriched)
    if total_value:
        for p in enriched:
            p["weight_pct"] = (p["mkt_value"] / total_value * 100).quantize(Decimal("0.01"))
    else:
        for p in enriched:
            p["weight_pct"] = Decimal("0")

    return enriched


def get_portfolio_summary():
    """Build the summary data for the dashboard."""
    positions = get_enriched_positions()
    accounts = Account.objects.all()
    total_cash = sum((a.cash_balance for a in accounts), Decimal("0"))

    if not positions:
        return {
            "total_value": "0.00",
            "day_change_dollar": "$0.00",
            "day_change_pct": Decimal("0"),
            "total_return_dollar": "$0.00",
            "total_return_pct": Decimal("0"),
            "total_cash": f"{total_cash:,.2f}",
            "num_positions": 0,
            "num_accounts": accounts.count(),
            "top_movers": [],
            "top_winners": [],
            "top_positions": [],
            "sector_chart_data": "",
            "theme_chart_data": "",
            "account_chart_data": "",
        }

    total_mkt = sum((p["mkt_value"] for p in positions), Decimal("0"))
    total_cost = sum((p["cost_basis"] for p in positions), Decimal("0"))
    total_day_gain = sum((p["day_gain"] for p in positions), Decimal("0"))
    total_value = total_mkt + total_cash
    total_return = total_mkt - total_cost
    total_return_pct = (total_return / total_cost * 100) if total_cost else Decimal("0")
    day_pct = (total_day_gain / (total_mkt - total_day_gain) * 100) if (total_mkt - total_day_gain) else Decimal("0")

    # Add pct_of_portfolio to each position
    for p in positions:
        p["pct_of_portfolio"] = (
            (p["mkt_value"] / total_value * 100).quantize(Decimal("0.01")) if total_value else Decimal("0")
        )

    # Top movers (by absolute day %)
    sorted_movers = sorted(
        [p for p in positions if p["has_quote"]],
        key=lambda p: abs(p["day_change_pct"]),
        reverse=True,
    )[:5]

    # Top winners (by total return %)
    sorted_winners = sorted(positions, key=lambda p: p["total_return_pct"], reverse=True)[:5]

    # Largest positions
    sorted_largest = sorted(positions, key=lambda p: p["mkt_value"], reverse=True)[:5]

    # Chart data
    sector_totals = {}
    for p in positions:
        s = p["sector"]
        sector_totals[s] = sector_totals.get(s, Decimal("0")) + p["mkt_value"]
    sorted_sectors = sorted(sector_totals.items(), key=lambda x: x[1], reverse=True)
    sector_chart = {"labels": [s[0] for s in sorted_sectors], "values": [float(s[1]) for s in sorted_sectors]}

    theme_totals = {}
    for p in positions:
        for t in p["themes"]:
            theme_totals[t] = theme_totals.get(t, Decimal("0")) + p["mkt_value"]
    sorted_themes = sorted(theme_totals.items(), key=lambda x: x[1], reverse=True)
    theme_chart = {"labels": [t[0] for t in sorted_themes], "values": [float(t[1]) for t in sorted_themes]}

    account_totals = {}
    for p in positions:
        a = p["account"]
        account_totals[a] = account_totals.get(a, Decimal("0")) + p["mkt_value"]
    for a in accounts:
        account_totals[a.name] = account_totals.get(a.name, Decimal("0")) + a.cash_balance
    account_chart = {"labels": list(account_totals.keys()), "values": [float(v) for v in account_totals.values()]}

    sign = "+" if total_day_gain >= 0 else ""
    return_sign = "+" if total_return >= 0 else ""

    return {
        "total_value": f"{total_value:,.2f}",
        "day_change_dollar": f"{sign}${total_day_gain:,.2f}",
        "day_change_pct": day_pct.quantize(Decimal("0.01")),
        "total_return_dollar": f"{return_sign}${total_return:,.2f}",
        "total_return_pct": total_return_pct.quantize(Decimal("0.01")),
        "total_cash": f"{total_cash:,.2f}",
        "num_positions": len(positions),
        "num_accounts": accounts.count(),
        "top_movers": [{"symbol": p["symbol"], "day_change_pct": p["day_change_pct"]} for p in sorted_movers],
        "top_winners": [{"symbol": p["symbol"], "total_return_pct": p["total_return_pct"]} for p in sorted_winners],
        "top_positions": [{"symbol": p["symbol"], "pct_of_portfolio": p["pct_of_portfolio"]} for p in sorted_largest],
        "sector_chart_data": json.dumps(sector_chart),
        "theme_chart_data": json.dumps(theme_chart),
        "account_chart_data": json.dumps(account_chart),
    }
