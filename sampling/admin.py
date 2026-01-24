from django.contrib import admin
from sampling.models import FishSampling


@admin.register(FishSampling)
class FishSamplingAdmin(admin.ModelAdmin):
    list_display = (
        "fish_stock",
        "sampled_on",
        "sample_fish_count",
        "sample_total_weight",
        "average_weight_display",
        "growth_from_previous_display",
        "growth_percentage_display",
        "growth_status",
    )

    readonly_fields = (
        "average_weight_display",
        "growth_from_previous_display",
        "growth_percentage_display",
        "growth_status",
    )

    def average_weight_display(self, obj):
        return obj.average_weight

    average_weight_display.short_description = "Avg Weight (g)"

    def growth_from_previous_display(self, obj):
        return obj.growth_from_previous

    growth_from_previous_display.short_description = "Growth (g)"

    def growth_percentage_display(self, obj):
        return obj.growth_percentage

    growth_percentage_display.short_description = "Growth (%)"
