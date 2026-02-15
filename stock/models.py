from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum
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
    quantity = models.PositiveIntegerField()
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

        if self.status == self.CLOSED and not self.closed_on:
            raise ValidationError(
                "closed_on must be set when closing a stock."
            )

    def save(self, *args, **kwargs):
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
        samplings = list(self.samplings.order_by("-sampled_on")[:2])
        return samplings[1] if len(samplings) == 2 else None


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

    @property
    def total_dead_fish(self):
        return (
            self.mortalities.aggregate(
                total=Sum("dead_count")
            )["total"] or 0
        )

    @property
    def alive_fish_count(self):
        return max(self.quantity - self.total_dead_fish, 0)

    @property
    def latest_average_weight(self):
        latest = self.latest_sampling()
        return latest.average_weight if latest else self.initial_avg_weight


    @property
    def total_live_weight(self):
        return self.alive_fish_count * self.latest_average_weight
    
    @property
    def total_mortality(self):
        return self.mortalities.aggregate(
            total=Sum("dead_count")
        )["total"] or 0

    def __str__(self):
        return f"{self.species.name} in {self.pond.name} ({self.status})"
