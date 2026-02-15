from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from stock.models import PondFishStock


class FishSampling(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="samplings"
    )

    fish_stock = models.ForeignKey(
        PondFishStock,
        on_delete=models.CASCADE,
        related_name="samplings"
    )

    sampled_on = models.DateField()

    sample_fish_count = models.PositiveIntegerField()
    sample_total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # -----------------------------
    # Validation
    # -----------------------------
    def clean(self):
        if self.fish_stock.status != PondFishStock.ACTIVE:
            raise ValidationError(
                "Cannot add sampling to a closed stock."
            )

        if self.sampled_on < self.fish_stock.stocked_on:
            raise ValidationError(
                "Sampling date cannot be before stock date."
            )

        if self.sample_fish_count <= 0:
            raise ValidationError(
                "Fish count must be greater than zero."
            )

        if self.sample_total_weight <= 0:
            raise ValidationError(
                "Total weight must be greater than zero."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # -----------------------------
    # Simple Derived Data (Model Logic)
    # -----------------------------
    @property
    def average_weight(self):
        return round(
            self.sample_total_weight / self.sample_fish_count,
            2
        )

    def __str__(self):
        return f"Sampling on {self.sampled_on}"

    # -----------------------------
    # Growth (Delegated to Service Layer)
    # -----------------------------
    @property
    def growth_data(self):
        from sampling.services import calculate_growth
        return calculate_growth(self)

    @property
    def growth_from_previous(self):
        return self.growth_data["growth_from_previous"]

    @property
    def growth_percentage(self):
        return self.growth_data["growth_percentage"]

    @property
    def growth_status(self):
        return self.growth_data["growth_status"]
    
    @property
    def days_since_stocking(self):
        return (self.sampled_on - self.fish_stock.stocked_on).days

