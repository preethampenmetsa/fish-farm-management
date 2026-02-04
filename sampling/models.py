from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from core.models import Pond, FishSpecies

class PondFishStock(models.Model):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (CLOSED, "Closed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE)
    species = models.ForeignKey(FishSpecies, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(help_text="Total number of fish stocked initially")
    initial_avg_weight = models.DecimalField(max_digits=8, decimal_places=2)
    stocked_on = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ACTIVE,
    )
    closed_on = models.DateField(null=True, blank=True)

    # --------------------
    # Lifecycle enforcement
    # --------------------
    def clean(self):
        # Only one ACTIVE stock per pond + species
        if self.status == self.ACTIVE:
            qs = PondFishStock.objects.filter(
                pond=self.pond,
                species=self.species,
                status=self.ACTIVE,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError(
                    "An active stock for this species already exists in this pond."
                )

        # CLOSED must have closed_on
        if self.status == self.CLOSED and not self.closed_on:
            raise ValidationError(
                "closed_on must be set when closing a stock."
            )

    def save(self, *args, **kwargs):
        # Prevent reopening a closed stock
        if self.pk:
            old = PondFishStock.objects.get(pk=self.pk)
            if old.status == self.CLOSED and self.status == self.ACTIVE:
                raise ValidationError(
                    "A closed stock cannot be reopened."
                )

        self.full_clean()
        super().save(*args, **kwargs)

    # --------------------
    # Sampling helpers
    # --------------------
    def latest_sampling(self):
        return self.samplings.order_by("-sampled_on").first()

    def previous_sampling(self):
        samplings = self.samplings.order_by("-sampled_on")
        if samplings.count() >= 2:
            return samplings[1]
        return None

    # --------------------
    # Aggregated insights
    # --------------------
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
        if not self.initial_avg_weight:
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
        return f"{self.species.name} in {self.pond.name} ({self.status})"


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

    # User-input driven, but stored as derived values
    sample_fish_count = models.PositiveIntegerField()
    sample_total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total weight of sampled fish (grams)"
    )

    # --------------------
    # Validation
    # --------------------
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

    # --------------------
    # Derived properties
    # --------------------
    @property
    def average_weight(self):
        if not self.sample_total_weight or not self.sample_fish_count:
            return None
        return round(
            self.sample_total_weight / self.sample_fish_count,
            2
        )

    @property
    def previous_sampling(self):
        return (
            FishSampling.objects
            .filter(
                fish_stock=self.fish_stock,
                sampled_on__lt=self.sampled_on,
            )
            .order_by("-sampled_on")
            .first()
        )

    @property
    def growth_from_previous(self):
        previous = self.previous_sampling
        initial_avg = self.fish_stock.initial_avg_weight
        if previous and previous.average_weight is not None:
            return round(
            self.average_weight - previous.average_weight,
            2
        )
        # initial_avg = self.fish_stock.initial_avg_weight
        elif  initial_avg is not None:
            return round(
                    self.average_weight - initial_avg,
                    2
                )
        return None

    @property
    def days_since_previous(self):
        previous = self.previous_sampling
        if not previous:
            return None
        return (self.sampled_on - previous.sampled_on).days

    @property
    def growth_percentage(self):
        previous = self.previous_sampling

        # Case 1: Compare with previous sampling
        if previous and previous.average_weight is not None:
            base = previous.average_weight

        # Case 2: First sampling → compare with initial stock
        elif self.fish_stock.initial_avg_weight is not None:
            base = self.fish_stock.initial_avg_weight

        # Case 3: No baseline
        else:
            return None

        growth = self.average_weight - base

        return round(
            (growth / base) * Decimal("100"),
            2
        )

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

    def __str__(self):
        return f"Sampling on {self.sampled_on}"
