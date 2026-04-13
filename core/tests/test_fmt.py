from decimal import Decimal

from core.templatetags.fmt import human_cap, money, pct, pct_ratio, ratio, shares_fmt


class TestMoney:
    def test_formats_dollars(self):
        assert money(Decimal("1234.56")) == "$1,234.56"

    def test_none(self):
        assert money(None) == "-"

    def test_negative(self):
        assert money(Decimal("-500.10")) == "$-500.10"

    def test_large(self):
        assert money(Decimal("1000000")) == "$1,000,000.00"


class TestSharesFmt:
    def test_whole(self):
        assert shares_fmt(Decimal("100")) == "100"

    def test_fractional(self):
        assert shares_fmt(Decimal("10.50")) == "10.50"

    def test_none(self):
        assert shares_fmt(None) == "-"


class TestRatio:
    def test_formats(self):
        assert ratio(28.5) == "28.50"

    def test_none(self):
        assert ratio(None) == "-"


class TestPct:
    def test_normal_pct(self):
        assert pct(Decimal("12.34")) == "12.34%"

    def test_small_pct(self):
        # A 0.3% daily move should NOT be multiplied by 100
        assert pct(Decimal("0.30")) == "0.30%"

    def test_none(self):
        assert pct(None) == "-"

    def test_zero(self):
        assert pct(0) == "0.00%"


class TestPctRatio:
    def test_decimal_ratio(self):
        # yfinance yields like 0.0194 should be multiplied by 100
        assert pct_ratio(0.0194) == "1.94%"

    def test_none(self):
        assert pct_ratio(None) == "-"

    def test_zero(self):
        assert pct_ratio(0) == "0.00%"


class TestHumanCap:
    def test_trillions(self):
        assert human_cap(2.8e12) == "$2.8T"

    def test_billions(self):
        assert human_cap(835e9) == "$835.0B"

    def test_millions(self):
        assert human_cap(450e6) == "$450M"

    def test_none(self):
        assert human_cap(None) == "-"
