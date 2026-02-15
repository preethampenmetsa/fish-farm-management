from django import forms
from core.models import Pond
from feed.models import FeedType, FeedUsageLog, PondFeedStock


class FeedUsageForm(forms.ModelForm):
    class Meta:
        model = FeedUsageLog
        fields = [
            "pond_feed_stock",
            "quantity_kg",
            "given_on",
        ]
        widgets = {
            "given_on": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields["pond_feed_stock"].queryset = (
                PondFeedStock.objects.filter(user=user)
            )

class PondFeedStockForm(forms.ModelForm):
    class Meta:
        model = PondFeedStock
        fields = ["pond", "feed_type", "purchased_quantity_kg", "purchased_on"]
        widgets = {
            "purchased_on": forms.DateInput(attrs={"type": "date"})
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields["pond"].queryset = Pond.objects.filter(user=user)
            self.fields["feed_type"].queryset = FeedType.objects.filter(user=user)

class FeedTypeForm(forms.ModelForm):
    class Meta:
        model = FeedType
        fields = ["name", "brand"]
