from decimal import Decimal

from positions.services.portfolio import get_enriched_positions


def get_concentration_data():
    """Calculate concentration by position, sector, theme, and account."""
    positions = get_enriched_positions()
    if not positions:
        return {"by_position": [], "by_sector": {}, "by_theme": {}, "by_account": {}}

    total_value = sum((p["mkt_value"] for p in positions), Decimal("0"))
    if total_value == 0:
        return {"by_position": [], "by_sector": {}, "by_theme": {}, "by_account": {}}

    # By position
    by_position = sorted(
        [
            {"symbol": p["symbol"], "value": float(p["mkt_value"]), "pct": float(p["mkt_value"] / total_value * 100)}
            for p in positions
        ],
        key=lambda x: x["pct"],
        reverse=True,
    )

    # By sector
    sector_totals = {}
    for p in positions:
        s = p["sector"]
        sector_totals[s] = sector_totals.get(s, Decimal("0")) + p["mkt_value"]
    by_sector = {k: {"value": float(v), "pct": float(v / total_value * 100)} for k, v in sector_totals.items()}

    # By theme
    theme_totals = {}
    for p in positions:
        for t in p["themes"]:
            theme_totals[t] = theme_totals.get(t, Decimal("0")) + p["mkt_value"]
    by_theme = {k: {"value": float(v), "pct": float(v / total_value * 100)} for k, v in theme_totals.items()}

    # By account
    account_totals = {}
    for p in positions:
        a = p["account"]
        account_totals[a] = account_totals.get(a, Decimal("0")) + p["mkt_value"]
    by_account = {k: {"value": float(v), "pct": float(v / total_value * 100)} for k, v in account_totals.items()}

    return {
        "by_position": by_position,
        "by_sector": by_sector,
        "by_theme": by_theme,
        "by_account": by_account,
    }
