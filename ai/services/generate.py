import logging

from ai.services.client import get_client
from positions.services.fundamentals import get_fundamentals
from positions.services.quotes import get_quote

logger = logging.getLogger(__name__)

MODEL = "claude-opus-4-6"
MAX_TOKENS = 1024

THESIS_SYSTEM_PROMPT = (
    "You are helping an experienced self-directed retail investor write a concise investment thesis. "
    "Based on the position data provided, write a clear 2-4 sentence thesis covering: why to own this stock, "
    "what the key growth/value drivers are, and what makes it a compelling hold at the current price. "
    "Be specific to this company -- avoid generic statements. No disclaimers. No bullet points."
)

BEAR_CASE_SYSTEM_PROMPT = (
    "You are helping an experienced self-directed retail investor articulate the bear case "
    "for a stock they own. Based on the position data provided, write a concise 2-4 sentence bear case covering: "
    "the biggest risks to the thesis, what could go wrong, and at what point the investor should reconsider the "
    "position. Be specific and concrete -- name actual competitive threats, regulatory risks, or valuation concerns. "
    "No disclaimers. No bullet points."
)


def _build_position_context(position):
    """Build the context string for a position."""
    quote = get_quote(position.symbol) or {}
    fundamentals = get_fundamentals(position.symbol) or {}

    price = quote.get("price")
    parts = [
        f"Symbol: {position.symbol}",
        f"Name: {position.name}",
        f"Sector: {position.sector.name if position.sector else 'Unknown'}",
    ]

    themes = list(position.themes.values_list("name", flat=True))
    if themes:
        parts.append(f"Themes: {', '.join(themes)}")

    if price:
        parts.append(f"Current Price: ${price}")

    if quote.get("fifty_two_week_low") and quote.get("fifty_two_week_high"):
        parts.append(f"52-Week Range: ${quote['fifty_two_week_low']} - ${quote['fifty_two_week_high']}")

    for key, label in [
        ("forward_pe", "Forward P/E"),
        ("trailing_pe", "Trailing P/E"),
        ("price_to_sales", "P/S"),
        ("ev_to_ebitda", "EV/EBITDA"),
        ("market_cap", "Market Cap"),
        ("dividend_yield", "Dividend Yield"),
    ]:
        val = fundamentals.get(key)
        if val is not None:
            parts.append(f"{label}: {val}")

    shares = position.shares
    cost_basis = position.cost_basis
    if shares and price:
        mkt_value = shares * price
        total_return = mkt_value - cost_basis
        return_pct = (total_return / cost_basis * 100) if cost_basis else 0
        parts.append(f"Cost Basis: ${cost_basis:.2f}")
        parts.append(f"Current Return: {return_pct:.1f}%")

    return "\n".join(parts)


def generate_thesis(position):
    """Generate a thesis for a position using Claude. Returns the text or None."""
    client = get_client()
    if not client:
        return None

    context = _build_position_context(position)
    user_message = f"{context}\n\nWrite an investment thesis for this position."

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=THESIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except Exception:
        logger.exception("Thesis generation failed for %s", position.symbol)
        return None


def generate_bear_case(position):
    """Generate a bear case for a position using Claude. Returns the text or None."""
    client = get_client()
    if not client:
        return None

    context = _build_position_context(position)

    if position.thesis:
        context += f"\n\nCurrent Thesis:\n{position.thesis}"

    user_message = f"{context}\n\nWrite the bear case for this position."

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=BEAR_CASE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except Exception:
        logger.exception("Bear case generation failed for %s", position.symbol)
        return None
