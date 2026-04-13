from django.contrib import admin

from .models import Account, Lot, Position


class LotInline(admin.TabularInline):
    model = Lot
    extra = 1
    fields = ["shares", "purchase_price", "purchase_date", "notes"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "cash_balance"]


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ["symbol", "name", "account", "sector"]
    list_filter = ["account", "sector"]
    search_fields = ["symbol", "name"]
    filter_horizontal = ["themes"]
    inlines = [LotInline]


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ["position", "shares", "purchase_price", "purchase_date"]
    list_filter = ["position__account"]
    search_fields = ["position__symbol"]
