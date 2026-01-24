from decimal import Decimal, InvalidOperation

def calculate_sampling_from_batches(batch_size, batches):
    if batch_size <= 0:
        raise ValueError("Batch size must be greater than zero")

    if not batches:
        raise ValueError("At least one batch must be provided")

    total_batches = len(batches)
    total_fish = batch_size * total_batches
    total_weight = Decimal("0")

    for weight in batches:
        try:
            weight = Decimal(str(weight))
        except (InvalidOperation, ValueError):
            raise ValueError(f"Invalid batch weight: {weight}")

        if weight <= 0:
            raise ValueError("Batch weight must be greater than zero")

        total_weight += weight

    average_weight = total_weight / Decimal(total_fish)

    return {
        "sample_fish_count": total_fish,
        "sample_total_weight": total_weight,
        "average_weight": round(average_weight, 2),
    }

