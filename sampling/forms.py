from django import forms
from sampling.models import PondFishStock, FishSampling
from django.core.exceptions import ValidationError

class SamplingForm(forms.Form):
    fish_stock = forms.ModelChoiceField(
        queryset=PondFishStock.objects.all()
    )
    sampled_on = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    fish_batches = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter one batch per line as count:weight (e.g. 5:420)"
    )

    def clean_fish_batches(self):
        raw_batches = self.cleaned_data["fish_batches"]

        lines = raw_batches.strip().splitlines()

        if not lines:
            raise forms.ValidationError(
                "Please enter at least one batch."
            )

        batches = []

        for idx, line in enumerate(lines, start=1):
            if ":" not in line:
                raise forms.ValidationError(
                    f"Line {idx}: Use format count:weight (e.g. 5:420)"
                )

            count, weight = line.split(":", 1)

            try:
                count = int(count.strip())
            except ValueError:
                raise forms.ValidationError(
                    f"Line {idx}: Fish count must be a number."
                )

            try:
                weight = float(weight.strip())
            except ValueError:
                raise forms.ValidationError(
                    f"Line {idx}: Weight must be a number."
                )

            if count <= 0:
                raise forms.ValidationError(
                    f"Line {idx}: Fish count must be greater than zero."
                )

            if weight <= 0:
                raise forms.ValidationError(
                    f"Line {idx}: Weight must be greater than zero."
                )

            batches.append({
                "count": count,
                "weight": weight,
            })

        return batches
    
    def clean(self):
        cleaned_data = super().clean()

        fish_stock = cleaned_data.get("fish_stock")
        sampled_on = cleaned_data.get("sampled_on")

        # If basic fields are missing, stop here
        if not fish_stock or not sampled_on:
            return cleaned_data

        # Duplicate sampling check
        exists = FishSampling.objects.filter(
            fish_stock=fish_stock,
            sampled_on=sampled_on
        ).exists()

        if exists:
            raise ValidationError(
                "A sampling for this fish stock already exists on this date."
            )

        # Sampling date sanity check
        if sampled_on < fish_stock.stocked_on:
            raise ValidationError(
                f"Sampling date cannot be before stocking date ({fish_stock.stocked_on})."
            )

        return cleaned_data
