from django.db import transaction
from django.core.exceptions import ValidationError
from feed.models import FeedUsageLog, PondFeedStock


@transaction.atomic
def record_feed_usage(user, pond_feed_stock, quantity_kg, given_on):

    if quantity_kg <= 0:
        raise ValidationError("Quantity must be greater than 0")

    if pond_feed_stock.purchased_quantity_kg < quantity_kg:
        raise ValidationError("Not enough feed stock available")

    pond_feed_stock.purchased_quantity_kg -= quantity_kg
    pond_feed_stock.save()

    FeedUsageLog.objects.create(
        user=user,
        pond_feed_stock=pond_feed_stock,
        quantity_kg=quantity_kg,
        given_on=given_on
    )


def get_feed_dashboard(user):
    return (
        PondFeedStock.objects
        .filter(user=user)
        .select_related("pond", "feed_type")
    )
