from decimal import Decimal
from unittest.mock import patch

import pytest

from positions.services.portfolio import get_enriched_positions, get_portfolio_summary


@pytest.mark.django_db
class TestPortfolio:
    def test_enriched_positions_empty(self):
        result = get_enriched_positions()
        assert result == []

    @patch("positions.services.portfolio.get_quotes")
    def test_enriched_positions_with_data(self, mock_get_quotes, sample_portfolio, mock_quotes):
        mock_get_quotes.return_value = mock_quotes
        result = get_enriched_positions()
        assert len(result) == 15
        # Check that VTI is in the results
        vti = [p for p in result if p["symbol"] == "VTI"][0]
        assert vti["shares"] == Decimal("50")
        assert vti["account"] == "IRA"

    @patch("positions.services.portfolio.get_quotes")
    def test_portfolio_summary_totals(self, mock_get_quotes, sample_portfolio, mock_quotes):
        mock_get_quotes.return_value = mock_quotes
        summary = get_portfolio_summary()
        assert summary["num_positions"] == 15
        assert summary["num_accounts"] == 3
        assert int(summary["total_cash"].replace(",", "").split(".")[0]) > 0

    @patch("positions.services.portfolio.get_quotes")
    def test_day_change_aggregation(self, mock_get_quotes, sample_portfolio, mock_quotes):
        mock_get_quotes.return_value = mock_quotes
        summary = get_portfolio_summary()
        # Day change should be non-zero since we have price != previous_close
        assert summary["day_change_pct"] != Decimal("0")

    def test_portfolio_summary_empty(self):
        summary = get_portfolio_summary()
        assert summary["num_positions"] == 0
        assert summary["total_value"] == "0.00"
