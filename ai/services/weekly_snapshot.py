import json
import logging
from datetime import date

from ai.models import WeeklySnapshot
from ai.services.client import get_client
from positions.services.portfolio import get_enriched_positions

logger = logging.getLogger(__name__)

MODEL = "claude-opus-4-6"
MAX_TOKENS = 4096


def _iso_week_start(d=None):
    """Get the Monday of the current ISO week."""
    d = d or date.today()
    return d - __import__("datetime").timedelta(days=d.weekday())


def get_or_create_weekly_snapshot(force=False):
    """Get the weekly snapshot for the current week, or generate one."""
    week_start = _iso_week_start()

    if not force:
        existing = WeeklySnapshot.objects.filter(week_of=week_start).first()
        if existing:
            return existing

    client = get_client()
    if not client:
        return None

    positions = get_enriched_positions()
    if not positions:
        return None

    # Build compact portfolio digest
    digest = []
    for p in positions:
        digest.append(
            {
                "symbol": p["symbol"],
                "sector": p["sector"],
                "shares": str(p["shares"]),
                "mkt_value": str(p["mkt_value"]),
                "day_change_pct": str(p["day_change_pct"]),
                "total_return_pct": str(p["total_return_pct"]),
                "pct_of_portfolio": str(p.get("pct_of_portfolio", "0")),
            }
        )

    # Sector rollups
    from decimal import Decimal

    sector_totals = {}
    for p in positions:
        s = p["sector"]
        sector_totals[s] = sector_totals.get(s, Decimal("0")) + p["mkt_value"]
    total = sum(sector_totals.values(), Decimal("0"))
    sector_summary = {k: f"{float(v / total * 100):.1f}%" for k, v in sector_totals.items()} if total else {}

    portfolio_data = json.dumps({"positions": digest, "sectors": sector_summary}, default=str)

    system = (
        "You are writing a concise weekly portfolio review for an experienced self-directed retail investor. "
        "Cover: what moved this week, any theses that look shaky based on price action, "
        "concentration concerns, and one thing worth looking at next week. Keep it under 600 words. "
        "Be direct and specific. No disclaimers."
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": f"Portfolio data:\n{portfolio_data}"}],
        )
        text = response.content[0].text

        snapshot = WeeklySnapshot.objects.create(
            week_of=week_start,
            portfolio_snapshot=json.loads(portfolio_data),
            response=text,
            model=MODEL,
        )
        return snapshot
    except Exception:
        logger.exception("Weekly snapshot generation failed")
        return None
