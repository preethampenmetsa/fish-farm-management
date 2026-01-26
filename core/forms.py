from django import forms
from core.models import Pond, FishSpecies

class PondForm(forms.ModelForm):
    class Meta:
        model = Pond
        fields = ["name", "area_acres"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")   # 👈 CRITICAL
        super().__init__(*args, **kwargs)

class FishSpeciesForm(forms.ModelForm):
    class Meta:
        model = FishSpecies
        fields = ["name"]
