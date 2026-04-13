# Snapshot Finance

Personal investing dashboard. Track positions across multiple brokerage accounts with live quotes, cost basis, sector/theme tagging, and optional AI-powered thesis review.

## Background

This is a rewrite of the [2020 original](https://medium.com/@rdcolema7/make-your-own-investing-web-portal-with-python-and-django-89feb5ce0ddd). IEX Cloud shut down, Bokeh dropped its `charts` module, and the rest of the stack had rotted. v2 swaps in yfinance for market data, adds lot-level cost basis tracking, a valuation/concentration dashboard, and optional LLM thesis review via Claude.

## Quickstart

```bash
cp .env.example .env
# edit .env -- set INITIAL_USERNAME, INITIAL_PASSWORD, optionally ANTHROPIC_API_KEY
docker compose up
```

http://localhost:8000

**Without Docker:**

```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py create_initial_user
uv run python manage.py runserver
```

`INITIAL_USERNAME` and `INITIAL_PASSWORD` must be set in `.env` (or as env vars) before running `create_initial_user`.

## Adding positions

Use the Django admin at `/admin/`:

1. Create **Accounts** (e.g. "IRA", "Brokerage")
2. Create **Positions** (symbol + account). Name and sector auto-populate from yfinance on save.
3. Add **Lots** as inlines on each position (shares, price, date)
4. Optionally assign **Themes** and write a **Thesis** for each position

## LLM features

Set `ANTHROPIC_API_KEY` in `.env` to enable:

- **Thesis check** -- per-position review that stress-tests your stated reasoning
- **Bear case generation** -- writes the bear case for positions you own
- **Theme generation** -- clusters your portfolio into investment themes
- **Weekly snapshot** -- portfolio-wide summary of movers, concentration, and what to watch

Everything works without an API key. These features just won't appear.

## Project layout

| Directory | What's in it |
|---|---|
| `config/` | Django settings, root URL conf |
| `core/` | Sector/Theme models, base templates, auth, dashboard |
| `positions/` | Account/Position/Lot models, yfinance quotes + fundamentals, portfolio rollups |
| `analysis/` | Concentration, valuation, movers, alerts tabs |
| `ai/` | Anthropic client, thesis checks, weekly snapshots, theme generation |

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (or pip, if you prefer)
- Docker (optional)

## Tests

```bash
uv run pytest
```

## Not included

- No broker integrations (Plaid, OAuth, etc.)
- No options, bonds, crypto, or FX
- No multi-user support
- No real-time streaming quotes
- Server-rendered Django + HTMX, no SPA

## Future work

- Historical performance tracking (daily snapshots of portfolio value)
- Dividend income tracking and projections
- Bulk position import from CSV
- Rebalancing targets vs. current weights
