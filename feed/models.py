from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from core.models import Pond

class FeedType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class PondFeedStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE)
    feed_type = models.ForeignKey(FeedType, on_delete=models.CASCADE)

    purchased_quantity_kg = models.FloatField()
    purchased_on = models.DateField()

    def total_used(self):
        return self.feedusagelog_set.aggregate(
            total=Sum("quantity_kg")
        )["total"] or 0

    def current_stock(self):
        return self.purchased_quantity_kg - self.total_used()

    def __str__(self):
        return f"{self.pond.name} - {self.feed_type.name}"

class FeedUsageLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pond_feed_stock = models.ForeignKey(
        PondFeedStock,
        on_delete=models.CASCADE
    )

    quantity_kg = models.FloatField()
    given_on = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pond_feed_stock} - {self.quantity_kg} kg"
