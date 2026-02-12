from calculator.utils import calculate_sampling_from_batches
from sampling.models import FishSampling, PondFishStock
from collections import defaultdict


def create_sampling_from_batches(
    user,
    fish_stock,
    sampled_on,
    batch_size,
    batches
):
    result = calculate_sampling_from_batches(batch_size, batches)

    sampling = FishSampling.objects.create(
        user=user,
        fish_stock=fish_stock,
        sampled_on=sampled_on,
        sample_fish_count=result["sample_fish_count"],
        sample_total_weight=result["sample_total_weight"],
    )

    return sampling

from sampling.models import FishSampling

def calculate_growth(current_sampling):
    previous_sampling = (
        FishSampling.objects
        .filter(
            user=current_sampling.user,
            fish_stock=current_sampling.fish_stock,
            sampled_on__lt=current_sampling.sampled_on
        )
        .exclude(average_weight__isnull=True)
        .order_by("-sampled_on")
        .first()
    )

    if not previous_sampling or previous_sampling.average_weight == 0:
        return {
            "growth_from_previous": None,
            "growth_percentage": None,
            "growth_status": "NO DATA",
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
        "growth_status": status,
    }


def get_single_pond_biomass(pond):
    """
    Calculate biomass summary for a single pond.

    Returns:
        {
            "total_alive_fish": int,
            "total_biomass": float (grams),
            "species_data": {
                "Rohu": {
                    "alive_fish": int,
                    "total_weight": float (grams),
                },
                ...
            }
        }
    """

    # Get all ACTIVE stocks for this pond
    stocks = (
        pond.pondfishstock_set
        .filter(status="ACTIVE")
        .select_related("species")
    )

    total_alive = 0
    total_biomass = 0
    species_data = defaultdict(lambda: {
        "alive_fish": 0,
        "total_weight": 0,
    })

    for stock in stocks:

        # 1️⃣ Alive fish count (after mortality deduction)
        alive = stock.alive_fish_count or 0

        # 2️⃣ Latest average weight (fallback to initial weight)
        avg_weight = stock.latest_average_weight or 0

        # 3️⃣ Biomass = count × avg_weight (grams)
        biomass = alive * avg_weight

        # Aggregate pond totals
        total_alive += alive
        total_biomass += biomass

        # Aggregate species totals
        species = species_data[stock.species.name]
        species["alive_fish"] += alive
        species["total_weight"] += biomass

    return {
    "total_alive_fish": total_alive,
    "total_biomass": total_biomass,
    "total_biomass_tons": total_biomass / 1_000_000,
    "species_data": dict(species_data),
}






