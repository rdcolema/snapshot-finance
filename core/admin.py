from django.contrib import admin

from .models import Sector, Theme


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]
