import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from ai.models import ThesisCheck
from ai.services.thesis_check import check_thesis


@pytest.mark.django_db
class TestThesisCheck:
    @patch("positions.services.fundamentals.get_fundamentals")
    @patch("positions.services.quotes.get_quote")
    @patch("ai.services.thesis_check.get_client")
    def test_thesis_check_creates_record(self, mock_client, mock_quote, mock_fundamentals, accounts, sectors):
        from positions.models import Lot, Position

        pos = Position.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            account=accounts["taxable"],
            sector=sectors["Information Technology"],
            thesis="Strong ecosystem, services growth, AI integration coming.",
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("30"),
            purchase_price=Decimal("145.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )

        mock_quote.return_value = {
            "price": Decimal("175.00"),
            "previous_close": Decimal("173.00"),
            "fifty_two_week_low": Decimal("130.00"),
            "fifty_two_week_high": Decimal("180.00"),
        }
        mock_fundamentals.return_value = {
            "forward_pe": 28.5,
            "trailing_pe": 30.1,
            "price_to_sales": 7.2,
            "ev_to_ebitda": 22.0,
            "market_cap": 2800000000000,
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="The thesis is reasonable but could be strengthened.")]
        mock_client_instance = MagicMock()
        mock_client_instance.messages.create.return_value = mock_response
        mock_client.return_value = mock_client_instance

        result = check_thesis(pos)
        assert result is not None
        assert isinstance(result, ThesisCheck)
        assert result.position == pos
        assert result.thesis_snapshot == pos.thesis
        assert result.price_snapshot == Decimal("175.00")
        assert "reasonable" in result.response

    @patch("ai.services.thesis_check.get_client")
    def test_thesis_check_no_api_key(self, mock_client, accounts, sectors):
        from positions.models import Position

        pos = Position.objects.create(symbol="AAPL", account=accounts["taxable"], thesis="Test thesis")
        mock_client.return_value = None
        result = check_thesis(pos)
        assert result is None

    @patch("positions.services.fundamentals.get_fundamentals")
    @patch("positions.services.quotes.get_quote")
    @patch("ai.services.thesis_check.get_client")
    def test_prompt_includes_thesis(self, mock_client, mock_quote, mock_fundamentals, accounts, sectors):
        from positions.models import Lot, Position

        pos = Position.objects.create(
            symbol="MSFT",
            account=accounts["taxable"],
            sector=sectors["Information Technology"],
            thesis="Cloud dominance, AI copilot monetization.",
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("10"),
            purchase_price=Decimal("280.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )

        mock_quote.return_value = {"price": Decimal("350.00"), "previous_close": Decimal("345.00")}
        mock_fundamentals.return_value = {}

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Thesis review.")]
        mock_client_instance = MagicMock()
        mock_client_instance.messages.create.return_value = mock_response
        mock_client.return_value = mock_client_instance

        check_thesis(pos)

        call_args = mock_client_instance.messages.create.call_args
        user_content = call_args.kwargs["messages"][0]["content"]
        assert "Cloud dominance" in user_content
        assert "MSFT" in user_content
