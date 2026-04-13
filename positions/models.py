from decimal import Decimal

from django.db import models
from django.utils import timezone


class Account(models.Model):
    name = models.CharField(max_length=100)
    cash_balance = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))

    def __str__(self):
        return self.name


class Position(models.Model):
    symbol = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=200, blank=True, default="")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="positions")
    sector = models.ForeignKey(
        "core.Sector", on_delete=models.SET_NULL, null=True, blank=True, related_name="positions"
    )
    themes = models.ManyToManyField("core.Theme", blank=True, related_name="positions")
    thesis = models.TextField(blank=True, default="")
    thesis_updated_at = models.DateTimeField(null=True, blank=True)
    bear_case = models.TextField(blank=True, default="")
    bear_case_updated_at = models.DateTimeField(null=True, blank=True)
    target_weight_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("symbol", "account")]
        ordering = ["symbol"]

    def __str__(self):
        return f"{self.symbol} ({self.account.name})"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_thesis = self.thesis
        self._original_bear_case = self.bear_case

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        is_new = self.pk is None
        if is_new:
            if self.thesis:
                self.thesis_updated_at = timezone.now()
            if self.bear_case:
                self.bear_case_updated_at = timezone.now()
        else:
            if self.thesis != self._original_thesis and self.thesis:
                self.thesis_updated_at = timezone.now()
            if self.bear_case != self._original_bear_case and self.bear_case:
                self.bear_case_updated_at = timezone.now()
        super().save(*args, **kwargs)
        self._original_thesis = self.thesis
        self._original_bear_case = self.bear_case

    @property
    def shares(self):
        return sum((lot.shares for lot in self.lots.all()), Decimal("0"))

    @property
    def cost_basis(self):
        return sum((lot.shares * lot.purchase_price for lot in self.lots.all()), Decimal("0"))

    @property
    def avg_cost(self):
        s = self.shares
        if s == 0:
            return Decimal("0")
        return self.cost_basis / s


class Lot(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="lots")
    shares = models.DecimalField(max_digits=14, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=14, decimal_places=4)
    purchase_date = models.DateField()
    notes = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-purchase_date"]

    def __str__(self):
        return f"{self.position.symbol} - {self.shares} @ ${self.purchase_price} ({self.purchase_date})"

    @property
    def cost_basis(self):
        return self.shares * self.purchase_price
