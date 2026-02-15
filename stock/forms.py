from django import forms
from django.db.models import Q
from core.models import FishSpecies, Pond
from stock.models import PondFishStock


class PondStockForm(forms.ModelForm):
    class Meta:
        model = PondFishStock
        fields = [
            "pond",
            "species",
            "quantity",
            "initial_avg_weight",
            "stocked_on",
        ]
        widgets = {
            "stocked_on": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["pond"].queryset = Pond.objects.filter(user=self.user)

        self.fields["species"].queryset = FishSpecies.objects.filter(
            Q(user__isnull=True) | Q(user=self.user)
        ).order_by("name")
