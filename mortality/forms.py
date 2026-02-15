from django import forms
from stock.models import PondFishStock
from mortality.models import FishMortality


class FishMortalityForm(forms.ModelForm):
    class Meta:
        model = FishMortality
        fields = [
            "fish_stock",
            "date",
            "dead_count",
            "note",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea,
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields["fish_stock"].queryset = PondFishStock.objects.filter(
                user=user,
                status=PondFishStock.ACTIVE
            )
