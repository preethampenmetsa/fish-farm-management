from django.db import models

class Farmer(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name

class Pond(models.Model):
    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        related_name="ponds"
    )
    name = models.CharField(max_length=50)
    area_acres = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.area_acres} acres)"


class FishSpecies(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
