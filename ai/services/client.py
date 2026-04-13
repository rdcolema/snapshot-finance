from anthropic import Anthropic
from django.conf import settings


def get_client():
    key = settings.ANTHROPIC_API_KEY
    if not key:
        return None
    return Anthropic(api_key=key)


def is_available():
    return bool(settings.ANTHROPIC_API_KEY)
