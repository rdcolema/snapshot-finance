from django.db import migrations

SECTORS = [
    "Information Technology",
    "Financials",
    "Health Care",
    "Energy",
    "Utilities",
    "Industrials",
    "Consumer Discretionary",
    "Consumer Staples",
    "Communication Services",
    "Real Estate",
    "Materials",
    "ETF — Broad Market",
    "ETF — International",
    "ETF — Sector",
    "ETF — Bond",
    "ETF — Commodity",
    "Other",
]


def seed_sectors(apps, schema_editor):
    Sector = apps.get_model("core", "Sector")
    for name in SECTORS:
        Sector.objects.get_or_create(name=name)


def remove_sectors(apps, schema_editor):
    Sector = apps.get_model("core", "Sector")
    Sector.objects.filter(name__in=SECTORS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_sectors, remove_sectors),
    ]
