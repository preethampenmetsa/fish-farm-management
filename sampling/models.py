from decimal import Decimal
from django.db import models
from django.forms import ValidationError
from core.models import Pond, FishSpecies
from django.core.exceptions import ObjectDoesNotExist

class PondFishStock(models.Model):
    pond = models.ForeignKey(
        Pond,
        on_delete=models.CASCADE,
        related_name="fish_stocks"
    )
    species = models.ForeignKey(
        FishSpecies,
        on_delete=models.CASCADE,
        related_name="pond_stocks"
    )
    initial_avg_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Initial average weight per fish (grams)"
    )
    stocked_on = models.DateField()

    def latest_sampling(self):
        return self.samplings.order_by("-sampled_on").first()

    def previous_sampling(self):
        samplings = self.samplings.order_by("-sampled_on")
        if samplings.count() >= 2:
            return samplings[1]
        return None
    
    def latest_sampling(self):
        return self.samplings.order_by("-sampled_on").first()

    @property
    def total_growth(self):
        latest = self.latest_sampling()
        if not latest:
            return None

        return latest.average_weight - self.initial_avg_weight

    @property
    def days_since_stocking(self):
        latest = self.latest_sampling()
        if not latest:
            return None

        return (latest.sampled_on - self.stocked_on).days

    @property
    def total_growth_percentage(self):
        if self.initial_avg_weight == 0:
            return None

        growth = self.total_growth
        if growth is None:
            return None

        return round((growth / self.initial_avg_weight) * Decimal("100"), 2)
    
    @property
    def overall_growth_status(self):
        percentage = self.total_growth_percentage

        if percentage is None:
            return "NO DATA"

        if percentage >= 25:
            return "EXCELLENT"
        elif percentage >= 15:
            return "GOOD"
        elif percentage >= 8:
            return "AVERAGE"
        else:
            return "POOR"

    def __str__(self):
        return f"{self.species.name} in {self.pond.name}"


class FishSampling(models.Model):
    fish_stock = models.ForeignKey(
        PondFishStock,
        on_delete=models.CASCADE,
        related_name="samplings"
    )
    sampled_on = models.DateField()
    sample_fish_count = models.PositiveIntegerField()
    sample_total_weight = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Total weight of sampled fish (grams)"
    )
    def clean(self):
        if self.sample_fish_count <= 0:
            raise ValidationError("Fish count must be greater than zero")

    @property
    def average_weight(self):
        return round(
            self.sample_total_weight / self.sample_fish_count,
            2
        )
    @property
    def growth_from_previous(self):
        previous = (
            self.fish_stock.samplings
            .filter(sampled_on__lt=self.sampled_on)
            .order_by("-sampled_on")
            .first()
        )

        if not previous:
            return None

        return self.average_weight - previous.average_weight

    @property
    def days_since_previous(self):
        previous = (
            self.fish_stock.samplings
            .filter(sampled_on__lt=self.sampled_on)
            .order_by("-sampled_on")
            .first()
        )

        if not previous:
            return None

        return (self.sampled_on - previous.sampled_on).days 

    def __str__(self):
        return f"Sampling on {self.sampled_on}"
    
    @property
    def growth_percentage(self):
        previous = (
            self.fish_stock.samplings
            .filter(sampled_on__lt=self.sampled_on)
            .order_by("-sampled_on")
            .first()
        )

        if not previous:
            return None

        growth = self.average_weight - previous.average_weight
        return round((growth / previous.average_weight) * Decimal("100"), 2)
    
    @property
    def growth_status(self):
        percentage = self.growth_percentage

        if percentage is None:
            return "NO DATA"

        if percentage >= 8:
            return "GOOD"
        elif percentage >= 4:
            return "AVERAGE"
        else:
            return "POOR"

