from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Pond(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ponds"
    )
    name = models.CharField(max_length=50)
    area_acres = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.area_acres} acres)"

class FishSpecies(models.Model):
    name = models.CharField(max_length=100)

    # NULL = global species, set = user-specific
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custom_species"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"],
                name="unique_species_per_user"
            )
        ]

    def __str__(self):
        if self.user:
            return f"{self.name} (custom)"
        return f"{self.name} (default)"
