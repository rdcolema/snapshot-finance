from django.shortcuts import render

from .models import Account, Position
from . import portfolio_utils as pu


def index(request):
    """Primary view of positions held"""

    positions_summary = pu.get_position_summary(Position.objects.all())
    accounts = Account.objects.all()
    total_cash = sum((acct.cash_balance for acct in accounts))

    context = {
        "positions": positions_summary.to_html(index=False, float_format=lambda x: '%.2f' % x),
        "accounts": [acct.name for acct in accounts],
        "cash_balances": {acct: acct.cash_balance for acct in accounts},
        "total_cash": "{:,.2f}".format(total_cash),
        "total_value": "{:,.2f}".format(total_cash + positions_summary["Market Value ($)"].iloc[0]),
        "num_positions": positions_summary.shape[0] - 1,
    }

    return render(request, "positions/index.html", context)
