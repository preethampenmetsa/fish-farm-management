from django import forms
from django.core.exceptions import ValidationError
from stock.models import PondFishStock
from sampling.models import FishSampling


class SamplingForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["fish_stock"].queryset = PondFishStock.objects.filter(
                user=self.user,
                status=PondFishStock.ACTIVE
            )
        else:
            self.fields["fish_stock"].queryset = PondFishStock.objects.none()

    fish_stock = forms.ModelChoiceField(
        queryset=PondFishStock.objects.none(),
        help_text="Select active fish stock"
    )

    sampled_on = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    batch_size = forms.IntegerField(
        min_value=1,
        help_text="Number of fish per batch (e.g. 5)"
    )

    batch_weights = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter one batch weight per line"
    )

    def clean_batch_weights(self):
        raw = self.cleaned_data["batch_weights"]
        lines = raw.strip().splitlines()

        if not lines:
            raise forms.ValidationError("Enter at least one batch weight.")

        weights = []
        for idx, line in enumerate(lines, start=1):
            try:
                weight = float(line.strip())
            except ValueError:
                raise forms.ValidationError(
                    f"Line {idx}: weight must be a number."
                )

            if weight <= 0:
                raise forms.ValidationError(
                    f"Line {idx}: weight must be > 0."
                )

            weights.append(weight)

        return weights

    def clean(self):
        cleaned_data = super().clean()

        fish_stock = cleaned_data.get("fish_stock")
        sampled_on = cleaned_data.get("sampled_on")

        if not fish_stock or not sampled_on:
            return cleaned_data

        exists = FishSampling.objects.filter(
            fish_stock=fish_stock,
            sampled_on=sampled_on
        ).exists()

        if exists:
            raise ValidationError(
                "A sampling already exists on this date."
            )

        if sampled_on < fish_stock.stocked_on:
            raise ValidationError(
                f"Sampling date cannot be before stocking date ({fish_stock.stocked_on})."
            )

        return cleaned_data
