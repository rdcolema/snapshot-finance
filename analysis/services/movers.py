from positions.services.portfolio import get_enriched_positions


def get_movers_data():
    """Get today's biggest movers and all-time winners/losers."""
    positions = get_enriched_positions()
    if not positions:
        return {"day_movers": [], "winners": [], "losers": []}

    quoted = [p for p in positions if p["has_quote"]]

    day_movers = sorted(quoted, key=lambda p: abs(p["day_change_pct"]), reverse=True)[:20]
    winners = sorted(positions, key=lambda p: p["total_return_pct"], reverse=True)[:20]
    losers = sorted(positions, key=lambda p: p["total_return_pct"])[:20]

    return {
        "day_movers": day_movers,
        "winners": winners,
        "losers": losers,
    }
