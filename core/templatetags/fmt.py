from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def money(value):
    """Format as $1,234.56"""
    if value is None:
        return "-"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
    return f"${val:,.2f}"


@register.filter
def shares_fmt(value):
    """Format shares: whole numbers show no decimals, fractional show 2."""
    if value is None:
        return "-"
    try:
        val = Decimal(str(value))
    except Exception:
        return str(value)
    if val == val.to_integral_value():
        return f"{int(val):,}"
    return f"{float(val):,.2f}"


@register.filter
def ratio(value):
    """Format a ratio like P/E to 2 decimal places."""
    if value is None:
        return "-"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
    return f"{val:.2f}"


@register.filter
def pct(value, decimals=2):
    """Format as percentage: 0.0194 -> 1.94% or 1.94 -> 1.94%."""
    if value is None:
        return "-"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
    # yfinance returns dividend yield as a decimal ratio (e.g. 0.0194 for 1.94%)
    if 0 < abs(val) < 0.5:
        val *= 100
    return f"{val:.{int(decimals)}f}%"


@register.filter
def human_cap(value):
    """Format large numbers: $835B, $12.4T, $450M."""
    if value is None:
        return "-"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
    if val >= 1e12:
        return f"${val / 1e12:.1f}T"
    if val >= 1e9:
        return f"${val / 1e9:.1f}B"
    if val >= 1e6:
        return f"${val / 1e6:.0f}M"
    return f"${val:,.0f}"
