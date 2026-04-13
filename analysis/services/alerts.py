from decimal import Decimal

from django.utils import timezone

from positions.models import Position
from positions.services.portfolio import get_enriched_positions


def get_alerts():
    """Generate portfolio alerts."""
    positions = get_enriched_positions()
    if not positions:
        return {"sizing": [], "stale_thesis": [], "concentration": []}

    alerts = {"sizing": [], "stale_thesis": [], "concentration": []}

    # Position sizing alerts
    for p in positions:
        weight = p["weight_pct"]
        if p["target_weight_pct"] is not None:
            if weight > p["target_weight_pct"]:
                alerts["sizing"].append(
                    {
                        "symbol": p["symbol"],
                        "message": f"Above target weight: {weight:.1f}% vs {p['target_weight_pct']}% target",
                    }
                )
        elif weight > 5:
            alerts["sizing"].append(
                {
                    "symbol": p["symbol"],
                    "message": f"No target set, currently {weight:.1f}% of portfolio",
                }
            )

    # Stale thesis alerts (>180 days)
    now = timezone.now()
    stale_positions = Position.objects.filter(thesis_updated_at__isnull=False).exclude(thesis="")
    for pos in stale_positions:
        days = (now - pos.thesis_updated_at).days
        if days > 180:
            alerts["stale_thesis"].append(
                {
                    "symbol": pos.symbol,
                    "message": f"Thesis last updated {days} days ago",
                }
            )

    # No thesis at all
    no_thesis = Position.objects.filter(thesis="")
    for pos in no_thesis:
        alerts["stale_thesis"].append(
            {
                "symbol": pos.symbol,
                "message": "No thesis written",
            }
        )

    # Sector concentration (>25%)
    total_value = sum((p["mkt_value"] for p in positions), Decimal("0"))
    sector_totals = {}
    for p in positions:
        s = p["sector"]
        sector_totals[s] = sector_totals.get(s, Decimal("0")) + p["mkt_value"]
    for sector, value in sector_totals.items():
        if total_value > 0:
            pct = value / total_value * 100
            if pct > 25:
                alerts["concentration"].append(
                    {
                        "sector": sector,
                        "message": f"{sector}: {pct:.1f}% of portfolio",
                    }
                )

    return alerts
