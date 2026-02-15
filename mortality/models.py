from django.db import models
from django.contrib.auth.models import User
from stock.models import PondFishStock
from django.core.exceptions import ValidationError



class FishMortality(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    fish_stock = models.ForeignKey(
        PondFishStock,
        on_delete=models.CASCADE,
        related_name="mortalities"
    )

    date = models.DateField()
    dead_count = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.fish_stock.status != PondFishStock.ACTIVE:
            raise ValidationError("Cannot log mortality for closed stock.")

    def __str__(self):
        return f"{self.fish_stock} - {self.dead_count} dead"
