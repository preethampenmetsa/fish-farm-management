from django.contrib import admin
from .models import PondFishStock


@admin.register(PondFishStock)
class PondFishStockAdmin(admin.ModelAdmin):
    list_display = (
        "pond",
        "species",
        "status",
        "alive_fish_count",
        "total_live_weight",
        "overall_growth_status",
    )

    list_filter = ("status", "pond", "species")
