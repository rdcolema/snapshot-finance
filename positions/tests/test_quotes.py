from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.cache import cache as django_cache

from positions.services.quotes import _fetch_with_retry, get_quote, get_quotes


@pytest.fixture(autouse=True)
def clear_cache():
    django_cache.clear()
    yield
    django_cache.clear()


@pytest.mark.django_db
class TestQuotes:
    @patch("positions.services.quotes._fetch_quote")
    def test_get_quote_returns_data(self, mock_fetch):
        mock_fetch.return_value = {"symbol": "AAPL", "price": Decimal("175.00"), "previous_close": Decimal("173.00")}
        result = get_quote("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["price"] == Decimal("175.00")

    @patch("positions.services.quotes._fetch_quote")
    def test_get_quote_caches(self, mock_fetch):
        mock_fetch.return_value = {"symbol": "GOOG", "price": Decimal("140.00"), "previous_close": Decimal("138.00")}
        result1 = get_quote("GOOG")
        result2 = get_quote("GOOG")
        assert mock_fetch.call_count == 1
        assert result1 == result2

    @patch("positions.services.quotes.time.sleep")
    @patch("positions.services.quotes._fetch_quote")
    def test_retry_on_failure(self, mock_fetch, mock_sleep):
        mock_fetch.side_effect = [
            ConnectionError("timeout"),
            ConnectionError("timeout"),
            {"symbol": "AAPL", "price": Decimal("175.00")},
        ]
        result = _fetch_with_retry("AAPL", max_retries=3)
        assert result is not None
        assert mock_fetch.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("positions.services.quotes.time.sleep")
    @patch("positions.services.quotes._fetch_quote")
    def test_all_retries_exhausted(self, mock_fetch, mock_sleep):
        mock_fetch.side_effect = ConnectionError("timeout")
        result = _fetch_with_retry("BAD", max_retries=3)
        assert result is None
        assert mock_fetch.call_count == 3

    @patch("positions.services.quotes._fetch_with_retry")
    def test_get_quotes_concurrent(self, mock_retry):
        mock_retry.side_effect = lambda sym: {"symbol": sym, "price": Decimal("100.00")}
        results = get_quotes(["AAPL", "MSFT", "GOOGL"])
        assert len(results) == 3
        assert "AAPL" in results
        assert "MSFT" in results

    @patch("positions.services.quotes._fetch_with_retry")
    def test_graceful_degradation(self, mock_retry):
        mock_retry.return_value = None
        result = get_quote("BAD")
        assert result is None
