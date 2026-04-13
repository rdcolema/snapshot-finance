from django.db import models


class ThesisCheck(models.Model):
    position = models.ForeignKey("positions.Position", on_delete=models.CASCADE, related_name="thesis_checks")
    thesis_snapshot = models.TextField()
    price_snapshot = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    response = models.TextField()
    model = models.CharField(max_length=100, default="claude-opus-4-6")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ThesisCheck: {self.position.symbol} ({self.created_at:%Y-%m-%d})"


class WeeklySnapshot(models.Model):
    week_of = models.DateField(unique=True)
    portfolio_snapshot = models.JSONField()
    response = models.TextField()
    model = models.CharField(max_length=100, default="claude-opus-4-6")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-week_of"]

    def __str__(self):
        return f"WeeklySnapshot: {self.week_of}"
