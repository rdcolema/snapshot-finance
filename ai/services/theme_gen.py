import json
import logging

from ai.services.client import get_client

logger = logging.getLogger(__name__)

MODEL = "claude-opus-4-6"
MAX_TOKENS = 2048

SYSTEM_PROMPT = """\
You are analyzing a stock portfolio to identify investment themes. A theme is a cross-cutting \
idea that ties multiple positions together (e.g. "AI infrastructure", "defense modernization", \
"clean energy transition", "dividend compounders").

Given the list of positions, return a JSON array where each element has:
- "name": short theme name (2-4 words, title case)
- "description": one sentence explaining the theme
- "symbols": array of ticker symbols that belong to this theme

Rules:
- Each position can belong to multiple themes or none.
- Aim for 5-12 themes depending on portfolio diversity.
- Be specific. "Technology" is too broad. "Semiconductor capex cycle" is good.
- Only return valid JSON. No markdown, no explanation, no preamble."""


def generate_themes(positions):
    """Ask Claude to identify themes across a list of positions.

    Returns a list of dicts: [{"name": ..., "description": ..., "symbols": [...]}, ...]
    or None on failure.
    """
    client = get_client()
    if not client:
        return None

    lines = []
    for p in positions:
        sector = p.sector.name if p.sector else "Unknown"
        lines.append(f"{p.symbol} - {p.name} ({sector})")

    user_message = "Portfolio positions:\n" + "\n".join(lines)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        # Strip markdown fences if Claude wraps the JSON
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        themes = json.loads(text)
        if not isinstance(themes, list):
            logger.error("Expected list from Claude, got %s", type(themes))
            return None
        return themes
    except (json.JSONDecodeError, KeyError, IndexError):
        logger.exception("Failed to parse theme generation response")
        return None
    except Exception:
        logger.exception("Theme generation failed")
        return None
