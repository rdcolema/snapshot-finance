import datetime
from decimal import Decimal

import pytest

from positions.models import Lot, Position


@pytest.mark.django_db
class TestLotAggregation:
    def test_single_lot_shares(self, accounts, sectors):
        pos = Position.objects.create(
            symbol="AAPL", account=accounts["taxable"], sector=sectors["Information Technology"]
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("10"),
            purchase_price=Decimal("150.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )
        assert pos.shares == Decimal("10")

    def test_single_lot_cost_basis(self, accounts, sectors):
        pos = Position.objects.create(
            symbol="AAPL", account=accounts["taxable"], sector=sectors["Information Technology"]
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("10"),
            purchase_price=Decimal("150.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )
        assert pos.cost_basis == Decimal("1500.0000")

    def test_multi_lot_shares(self, accounts, sectors):
        pos = Position.objects.create(
            symbol="MSFT", account=accounts["taxable"], sector=sectors["Information Technology"]
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("10"),
            purchase_price=Decimal("200.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("5"),
            purchase_price=Decimal("250.0000"),
            purchase_date=datetime.date(2023, 6, 1),
        )
        assert pos.shares == Decimal("15")

    def test_multi_lot_cost_basis(self, accounts, sectors):
        pos = Position.objects.create(
            symbol="MSFT", account=accounts["taxable"], sector=sectors["Information Technology"]
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("10"),
            purchase_price=Decimal("200.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("5"),
            purchase_price=Decimal("250.0000"),
            purchase_date=datetime.date(2023, 6, 1),
        )
        # 10*200 + 5*250 = 2000 + 1250 = 3250
        assert pos.cost_basis == Decimal("3250.0000")

    def test_multi_lot_avg_cost(self, accounts, sectors):
        pos = Position.objects.create(
            symbol="MSFT", account=accounts["taxable"], sector=sectors["Information Technology"]
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("10"),
            purchase_price=Decimal("200.0000"),
            purchase_date=datetime.date(2023, 1, 1),
        )
        Lot.objects.create(
            position=pos,
            shares=Decimal("5"),
            purchase_price=Decimal("250.0000"),
            purchase_date=datetime.date(2023, 6, 1),
        )
        # 3250 / 15 = 216.6666...
        expected = Decimal("3250.0000") / Decimal("15")
        assert pos.avg_cost == expected

    def test_no_lots_returns_zero(self, accounts, sectors):
        pos = Position.objects.create(
            symbol="TSLA", account=accounts["taxable"], sector=sectors["Information Technology"]
        )
        assert pos.shares == Decimal("0")
        assert pos.cost_basis == Decimal("0")
        assert pos.avg_cost == Decimal("0")

    def test_symbol_uppercased_on_save(self, accounts, sectors):
        pos = Position.objects.create(symbol="aapl", account=accounts["taxable"])
        assert pos.symbol == "AAPL"

    def test_lot_cost_basis_property(self, accounts, sectors):
        pos = Position.objects.create(symbol="VTI", account=accounts["ira"], sector=sectors["ETF — Broad Market"])
        lot = Lot.objects.create(
            position=pos,
            shares=Decimal("50"),
            purchase_price=Decimal("220.0000"),
            purchase_date=datetime.date(2022, 1, 15),
        )
        assert lot.cost_basis == Decimal("11000.0000")


@pytest.mark.django_db
class TestThesisTimestamp:
    def test_thesis_timestamp_set_on_create(self, accounts):
        pos = Position.objects.create(symbol="AAPL", account=accounts["taxable"], thesis="Strong ecosystem.")
        assert pos.thesis_updated_at is not None

    def test_no_timestamp_without_thesis(self, accounts):
        pos = Position.objects.create(symbol="AAPL", account=accounts["taxable"])
        assert pos.thesis_updated_at is None

    def test_timestamp_updates_on_edit(self, accounts):
        pos = Position.objects.create(symbol="AAPL", account=accounts["taxable"], thesis="Original thesis.")
        first_ts = pos.thesis_updated_at
        assert first_ts is not None

        pos.thesis = "Updated thesis with new reasoning."
        pos.save()
        pos.refresh_from_db()
        assert pos.thesis_updated_at > first_ts

    def test_timestamp_unchanged_on_unrelated_save(self, accounts):
        pos = Position.objects.create(symbol="AAPL", account=accounts["taxable"], thesis="Some thesis.")
        first_ts = pos.thesis_updated_at

        pos.name = "Apple Inc."
        pos.save()
        pos.refresh_from_db()
        assert pos.thesis_updated_at == first_ts

    def test_bear_case_timestamp_updates_on_edit(self, accounts):
        pos = Position.objects.create(symbol="AAPL", account=accounts["taxable"], bear_case="Valuation risk.")
        first_ts = pos.bear_case_updated_at
        assert first_ts is not None

        pos.bear_case = "Valuation risk plus regulatory."
        pos.save()
        pos.refresh_from_db()
        assert pos.bear_case_updated_at > first_ts
