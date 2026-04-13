from analysis.services.valuation import _get_verdict


class TestValuation:
    def test_tech_cheap(self):
        assert _get_verdict(15, "Information Technology") == "cheap"

    def test_tech_fair(self):
        assert _get_verdict(25, "Information Technology") == "fair"

    def test_tech_stretched(self):
        assert _get_verdict(35, "Information Technology") == "stretched"

    def test_financials_cheap(self):
        assert _get_verdict(8, "Financials") == "cheap"

    def test_financials_stretched(self):
        assert _get_verdict(20, "Financials") == "stretched"

    def test_energy_cheap(self):
        assert _get_verdict(6, "Energy") == "cheap"

    def test_energy_stretched(self):
        assert _get_verdict(18, "Energy") == "stretched"

    def test_none_value(self):
        assert _get_verdict(None, "Information Technology") is None

    def test_unknown_sector_uses_default(self):
        assert _get_verdict(10, "Unknown Sector") == "cheap"
        assert _get_verdict(25, "Unknown Sector") == "stretched"
