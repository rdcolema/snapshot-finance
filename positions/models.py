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

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        if not self.pk:
            if self.thesis:
                self.thesis_updated_at = timezone.now()
            if self.bear_case:
                self.bear_case_updated_at = timezone.now()
        else:
            update_fields = kwargs.get("update_fields")
            if update_fields is None or "thesis" in update_fields:
                if self.thesis and not self.thesis_updated_at:
                    self.thesis_updated_at = timezone.now()
            if update_fields is None or "bear_case" in update_fields:
                if self.bear_case and not self.bear_case_updated_at:
                    self.bear_case_updated_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def shares(self):
        total = self.lots.aggregate(total=models.Sum("shares"))["total"]
        return total or Decimal("0")

    @property
    def cost_basis(self):
        from django.db.models import F, Sum

        total = self.lots.aggregate(total=Sum(F("shares") * F("purchase_price")))["total"]
        return total or Decimal("0")

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
