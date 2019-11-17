from django.shortcuts import render

from positions.models import Account, Position
from . import analysis_utils as au


def index(request):
    """Primary view for portfolio analysis"""

    positions_data = au.get_position_data(Position.objects.all())
    accounts = Account.objects.all()
    total_cash = sum((acct.cash_balance for acct in accounts))

    concentration_bar_chart = au.get_concentration_bar_chart(positions_data)
    concentration_area_chart = au.get_concentration_area_chart(positions_data)

    context = {
        "positions": positions_data.to_html(index=False, float_format=lambda x: '%10.2f' % x),
        "accounts": [acct.name for acct in accounts],
        "cash_balances": {acct: acct.cash_balance for acct in accounts},
        "total_cash": "{:,.2f}".format(total_cash),
        "total_value": "{:,.2f}".format(total_cash + positions_data["Market Value ($)"].sum()),
        "num_positions": positions_data.shape[0],
        "concentration_bar_chart": concentration_bar_chart,
        "concentration_area_chart": concentration_area_chart,
    }

    return render(request, "analysis/index.html", context)
