from collections import defaultdict


def get_single_pond_biomass(pond):

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
        "current_avg_weight": 0,
    })

    for stock in stocks:

        alive = stock.alive_fish_count or 0
        avg_weight = stock.latest_average_weight or 0
        biomass = alive * avg_weight

        total_alive += alive
        total_biomass += biomass

        species = species_data[stock.species.name]
        species["alive_fish"] += alive
        species["total_weight"] += biomass
        species["current_avg_weight"] = avg_weight
        for data in species_data.values():
            data["total_weight_tons"] = data["total_weight"] / 1_000_000

    return {
        "total_alive_fish": total_alive,
        "total_biomass": total_biomass,
        "total_biomass_tons": total_biomass / 1_000_000,
        "species_data": dict(species_data),
    }
