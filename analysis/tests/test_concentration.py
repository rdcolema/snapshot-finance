from decimal import Decimal
from unittest.mock import patch

import pytest

from analysis.services.concentration import get_concentration_data


@pytest.mark.django_db
class TestConcentration:
    @patch("analysis.services.concentration.get_enriched_positions")
    def test_empty_portfolio(self, mock_positions):
        mock_positions.return_value = []
        data = get_concentration_data()
        assert data["by_position"] == []

    @patch("analysis.services.concentration.get_enriched_positions")
    def test_sector_rollup(self, mock_positions):
        mock_positions.return_value = [
            {
                "symbol": "AAPL",
                "sector": "Information Technology",
                "themes": [],
                "account": "Taxable",
                "mkt_value": Decimal("5000"),
            },
            {
                "symbol": "MSFT",
                "sector": "Information Technology",
                "themes": [],
                "account": "Taxable",
                "mkt_value": Decimal("3000"),
            },
            {"symbol": "JPM", "sector": "Financials", "themes": [], "account": "IRA", "mkt_value": Decimal("2000")},
        ]
        data = get_concentration_data()
        assert "Information Technology" in data["by_sector"]
        assert data["by_sector"]["Information Technology"]["pct"] == 80.0
        assert data["by_sector"]["Financials"]["pct"] == 20.0

    @patch("analysis.services.concentration.get_enriched_positions")
    def test_theme_rollup(self, mock_positions):
        mock_positions.return_value = [
            {
                "symbol": "AAPL",
                "sector": "IT",
                "themes": ["AI Buildout", "Core Holdings"],
                "account": "Taxable",
                "mkt_value": Decimal("5000"),
            },
            {
                "symbol": "VTI",
                "sector": "ETF",
                "themes": ["Core Holdings"],
                "account": "IRA",
                "mkt_value": Decimal("5000"),
            },
        ]
        data = get_concentration_data()
        assert "Core Holdings" in data["by_theme"]
        assert data["by_theme"]["Core Holdings"]["pct"] == 100.0
        assert data["by_theme"]["AI Buildout"]["pct"] == 50.0

    @patch("analysis.services.concentration.get_enriched_positions")
    def test_account_rollup(self, mock_positions):
        mock_positions.return_value = [
            {"symbol": "AAPL", "sector": "IT", "themes": [], "account": "Taxable", "mkt_value": Decimal("7000")},
            {"symbol": "VTI", "sector": "ETF", "themes": [], "account": "IRA", "mkt_value": Decimal("3000")},
        ]
        data = get_concentration_data()
        assert data["by_account"]["Taxable"]["pct"] == 70.0
        assert data["by_account"]["IRA"]["pct"] == 30.0
