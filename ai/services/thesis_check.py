import logging

from ai.models import ThesisCheck
from ai.services.client import get_client
from ai.services.generate import _build_position_context

logger = logging.getLogger(__name__)

MODEL = "claude-opus-4-6"
MAX_TOKENS = 2048

SYSTEM_PROMPT = """You are reviewing an investment thesis for an experienced self-directed retail investor. \
Be concise. Push back if the thesis is weak or outdated. Note specific data points that support or \
undermine the thesis. Review the thesis on its own terms -- a growth thesis, a value thesis, and an \
indexing thesis are all legitimate approaches. Stress-test the stated reasoning rather than recommending \
a different philosophy. Keep your response under 300 words. Do not flatter. No disclaimers."""


def check_thesis(position):
    """Run a thesis check for a position using Claude. Returns a ThesisCheck instance or None."""
    client = get_client()
    if not client:
        return None

    from positions.services.quotes import get_quote

    price = (get_quote(position.symbol) or {}).get("price")

    context = _build_position_context(position)
    user_message = f"{context}\n\nThesis:\n{position.thesis}"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text

        check = ThesisCheck.objects.create(
            position=position,
            thesis_snapshot=position.thesis,
            price_snapshot=price,
            response=text,
            model=MODEL,
        )
        return check
    except Exception:
        logger.exception("Thesis check failed for %s", position.symbol)
        return None
