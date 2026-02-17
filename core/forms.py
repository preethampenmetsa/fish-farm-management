from django import forms
from core.models import Pond, FishSpecies
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

