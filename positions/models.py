from django.db import models


class Account(models.Model):
    """A brokerage account"""

    ACCOUNT_TYPES = (
        ('TRADITIONAL', 'Traditional IRA or 401(k)'),
        ('ROTH', 'Roth IRA or 401(k)'),
        ('STANDARD', 'Standard Brokerage'),
    )

    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100, choices=ACCOUNT_TYPES)
    cash_balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Position(models.Model):
    """A Position, such as an equity holding"""

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    shares = models.FloatField()
    cost_basis = models.FloatField(default=0.0)
    account = models.ForeignKey("Account", on_delete=models.CASCADE)

    def __str__(self):
        return self.symbol
