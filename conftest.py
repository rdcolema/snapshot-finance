import datetime
from decimal import Decimal

import pytest

from core.models import Sector, Theme
from positions.models import Account, Lot, Position


@pytest.fixture
def sectors(db):
    """Create a set of sectors for testing."""
    names = [
        "Information Technology",
        "Financials",
        "Health Care",
        "Consumer Discretionary",
        "ETF — Broad Market",
        "Other",
    ]
    return {name: Sector.objects.get_or_create(name=name)[0] for name in names}


@pytest.fixture
def themes(db):
    """Create a set of themes for testing."""
    names = ["Dividend Growth", "AI Buildout", "Core Holdings"]
    return {name: Theme.objects.create(name=name) for name in names}


@pytest.fixture
def accounts(db):
    """Create test accounts."""
    return {
        "ira": Account.objects.create(name="IRA", cash_balance=Decimal("5000.0000")),
        "taxable": Account.objects.create(name="Taxable", cash_balance=Decimal("10000.0000")),
        "hsa": Account.objects.create(name="HSA", cash_balance=Decimal("2000.0000")),
    }


@pytest.fixture
def sample_portfolio(db, sectors, themes, accounts):
    """
    A realistic ~15 position portfolio spanning 5 sectors and 3 themes.
    Philosophy-neutral: broad ETFs, blue chips, a couple growth names.
    """
    positions_data = [
        # (symbol, name, account_key, sector_key, shares, price, date, theme_keys)
        (
            "VTI",
            "Vanguard Total Stock Market ETF",
            "ira",
            "ETF — Broad Market",
            50,
            "220.00",
            "2022-01-15",
            ["Core Holdings"],
        ),
        (
            "VXUS",
            "Vanguard Total International Stock ETF",
            "ira",
            "ETF — Broad Market",
            40,
            "55.00",
            "2022-01-15",
            ["Core Holdings"],
        ),
        ("AAPL", "Apple Inc.", "taxable", "Information Technology", 30, "145.00", "2021-06-10", ["AI Buildout"]),
        (
            "MSFT",
            "Microsoft Corporation",
            "taxable",
            "Information Technology",
            15,
            "280.00",
            "2021-03-20",
            ["AI Buildout"],
        ),
        ("GOOGL", "Alphabet Inc.", "taxable", "Information Technology", 10, "2200.00", "2021-08-05", ["AI Buildout"]),
        ("JPM", "JPMorgan Chase & Co.", "ira", "Financials", 20, "150.00", "2022-03-10", ["Dividend Growth"]),
        ("JNJ", "Johnson & Johnson", "ira", "Health Care", 25, "165.00", "2021-11-20", ["Dividend Growth"]),
        ("UNH", "UnitedHealth Group", "taxable", "Health Care", 8, "450.00", "2022-06-15", []),
        ("HD", "The Home Depot", "taxable", "Consumer Discretionary", 12, "310.00", "2022-02-01", ["Dividend Growth"]),
        ("AMZN", "Amazon.com Inc.", "taxable", "Consumer Discretionary", 20, "130.00", "2022-09-20", []),
        ("BRK.B", "Berkshire Hathaway Inc.", "ira", "Financials", 10, "300.00", "2021-05-15", []),
        ("PG", "Procter & Gamble", "hsa", "Other", 15, "140.00", "2022-04-10", ["Dividend Growth"]),
        ("KO", "Coca-Cola Company", "hsa", "Other", 30, "58.00", "2022-07-22", ["Dividend Growth"]),
        (
            "NVDA",
            "NVIDIA Corporation",
            "taxable",
            "Information Technology",
            25,
            "180.00",
            "2022-10-01",
            ["AI Buildout"],
        ),
        ("V", "Visa Inc.", "ira", "Financials", 18, "210.00", "2021-12-01", []),
    ]

    created = []
    for symbol, name, acct_key, sector_key, shares, price, date_str, theme_keys in positions_data:
        pos = Position.objects.create(
            symbol=symbol,
            name=name,
            account=accounts[acct_key],
            sector=sectors[sector_key],
        )
        for tk in theme_keys:
            pos.themes.add(themes[tk])
        Lot.objects.create(
            position=pos,
            shares=Decimal(str(shares)),
            purchase_price=Decimal(price),
            purchase_date=datetime.date.fromisoformat(date_str),
        )
        created.append(pos)

    return created


@pytest.fixture
def mock_quotes():
    """Mock quote data keyed by symbol."""
    return {
        "VTI": {
            "symbol": "VTI",
            "price": Decimal("230.00"),
            "previous_close": Decimal("228.50"),
            "market_cap": None,
            "fifty_two_week_low": Decimal("195.00"),
            "fifty_two_week_high": Decimal("240.00"),
        },
        "VXUS": {
            "symbol": "VXUS",
            "price": Decimal("58.00"),
            "previous_close": Decimal("57.50"),
            "market_cap": None,
            "fifty_two_week_low": Decimal("48.00"),
            "fifty_two_week_high": Decimal("60.00"),
        },
        "AAPL": {
            "symbol": "AAPL",
            "price": Decimal("175.00"),
            "previous_close": Decimal("173.00"),
            "market_cap": 2800000000000,
            "fifty_two_week_low": Decimal("130.00"),
            "fifty_two_week_high": Decimal("180.00"),
        },
        "MSFT": {
            "symbol": "MSFT",
            "price": Decimal("350.00"),
            "previous_close": Decimal("345.00"),
            "market_cap": 2600000000000,
            "fifty_two_week_low": Decimal("260.00"),
            "fifty_two_week_high": Decimal("360.00"),
        },
        "GOOGL": {
            "symbol": "GOOGL",
            "price": Decimal("140.00"),
            "previous_close": Decimal("138.00"),
            "market_cap": 1700000000000,
            "fifty_two_week_low": Decimal("100.00"),
            "fifty_two_week_high": Decimal("150.00"),
        },
        "JPM": {
            "symbol": "JPM",
            "price": Decimal("170.00"),
            "previous_close": Decimal("168.00"),
            "market_cap": 500000000000,
            "fifty_two_week_low": Decimal("130.00"),
            "fifty_two_week_high": Decimal("175.00"),
        },
        "JNJ": {
            "symbol": "JNJ",
            "price": Decimal("160.00"),
            "previous_close": Decimal("161.00"),
            "market_cap": 420000000000,
            "fifty_two_week_low": Decimal("150.00"),
            "fifty_two_week_high": Decimal("170.00"),
        },
        "UNH": {
            "symbol": "UNH",
            "price": Decimal("520.00"),
            "previous_close": Decimal("515.00"),
            "market_cap": 480000000000,
            "fifty_two_week_low": Decimal("420.00"),
            "fifty_two_week_high": Decimal("530.00"),
        },
        "HD": {
            "symbol": "HD",
            "price": Decimal("340.00"),
            "previous_close": Decimal("335.00"),
            "market_cap": 340000000000,
            "fifty_two_week_low": Decimal("280.00"),
            "fifty_two_week_high": Decimal("350.00"),
        },
        "AMZN": {
            "symbol": "AMZN",
            "price": Decimal("155.00"),
            "previous_close": Decimal("152.00"),
            "market_cap": 1600000000000,
            "fifty_two_week_low": Decimal("110.00"),
            "fifty_two_week_high": Decimal("160.00"),
        },
        "BRK.B": {
            "symbol": "BRK.B",
            "price": Decimal("360.00"),
            "previous_close": Decimal("355.00"),
            "market_cap": 780000000000,
            "fifty_two_week_low": Decimal("280.00"),
            "fifty_two_week_high": Decimal("370.00"),
        },
        "PG": {
            "symbol": "PG",
            "price": Decimal("155.00"),
            "previous_close": Decimal("154.00"),
            "market_cap": 360000000000,
            "fifty_two_week_low": Decimal("130.00"),
            "fifty_two_week_high": Decimal("160.00"),
        },
        "KO": {
            "symbol": "KO",
            "price": Decimal("62.00"),
            "previous_close": Decimal("61.50"),
            "market_cap": 270000000000,
            "fifty_two_week_low": Decimal("52.00"),
            "fifty_two_week_high": Decimal("64.00"),
        },
        "NVDA": {
            "symbol": "NVDA",
            "price": Decimal("480.00"),
            "previous_close": Decimal("470.00"),
            "market_cap": 1200000000000,
            "fifty_two_week_low": Decimal("150.00"),
            "fifty_two_week_high": Decimal("500.00"),
        },
        "V": {
            "symbol": "V",
            "price": Decimal("260.00"),
            "previous_close": Decimal("258.00"),
            "market_cap": 530000000000,
            "fifty_two_week_low": Decimal("200.00"),
            "fifty_two_week_high": Decimal("270.00"),
        },
    }
