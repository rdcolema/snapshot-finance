from django.contrib import admin

from .models import ThesisCheck, WeeklySnapshot


@admin.register(ThesisCheck)
class ThesisCheckAdmin(admin.ModelAdmin):
    list_display = ["position", "model", "created_at"]
    list_filter = ["model"]
    readonly_fields = ["position", "thesis_snapshot", "price_snapshot", "response", "model", "created_at"]


@admin.register(WeeklySnapshot)
class WeeklySnapshotAdmin(admin.ModelAdmin):
    list_display = ["week_of", "model", "created_at"]
    readonly_fields = ["week_of", "portfolio_snapshot", "response", "model", "created_at"]
