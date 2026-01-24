from calculator.utils import calculate_sampling_from_batches
from sampling.models import FishSampling


def create_sampling_from_batches(
    fish_stock,
    sampled_on,
    batch_size,
    batches
):
    result = calculate_sampling_from_batches(batch_size, batches)

    sampling = FishSampling.objects.create(
        fish_stock=fish_stock,
        sampled_on=sampled_on,
        sample_fish_count=result["sample_fish_count"],
        sample_total_weight=result["sample_total_weight"],
    )

    return sampling

def calculate_growth(current_sampling):
    previous_sampling = (
        FishSampling.objects
        .filter(
            fish_stock=current_sampling.fish_stock,
            sampled_on__lt=current_sampling.sampled_on
        )
        .order_by("-sampled_on")
        .first()
    )

    if not previous_sampling:
        return {
            "growth_from_previous": None,
            "growth_percentage": None,
            "growth_status": "NO DATA"
        }

    diff = current_sampling.average_weight - previous_sampling.average_weight
    percentage = (diff / previous_sampling.average_weight) * 100

    if percentage >= 10:
        status = "GOOD"
    elif percentage >= 5:
        status = "AVERAGE"
    else:
        status = "POOR"

    return {
        "growth_from_previous": round(diff, 2),
        "growth_percentage": round(percentage, 2),
        "growth_status": status
    }



