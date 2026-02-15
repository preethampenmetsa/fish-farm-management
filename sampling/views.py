from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from calculator.utils import calculate_sampling_from_batches
from sampling.forms import SamplingForm
from sampling.models import FishSampling
from sampling.services import create_sampling_from_batches
from core.models import Pond
from stock.models import PondFishStock
import json
from collections import defaultdict

@login_required
def add_sampling(request):
    if request.method == "POST":
        form = SamplingForm(request.POST, user=request.user)

        if form.is_valid():
            if "edit" in request.POST:
                return render(request, "sampling/add_sampling.html", {"form": form})

            fish_stock = form.cleaned_data["fish_stock"]
            sampled_on = form.cleaned_data["sampled_on"]
            batch_size = form.cleaned_data["batch_size"]
            batch_weights = form.cleaned_data["batch_weights"]

            if "confirm" not in request.POST:
                preview = calculate_sampling_from_batches(
                    batch_size=batch_size,
                    batches=batch_weights,
                )

                return render(
                    request,
                    "sampling/preview_sampling.html",
                    {"form": form, "preview": preview},
                )

            create_sampling_from_batches(
                user=request.user,
                fish_stock=fish_stock,
                sampled_on=sampled_on,
                batch_size=batch_size,
                batches=batch_weights,
            )

            return redirect("sampling:sampling-success")

    else:
        form = SamplingForm(user=request.user)

    return render(request, "sampling/add_sampling.html", {"form": form})


@login_required
def sampling_success(request):
    return render(request, "sampling/success.html")


def sampling_dashboard(request):
    pond_id = request.GET.get("pond")
    stock_id = request.GET.get("stock")

    samplings = FishSampling.objects.all().select_related(
        "fish_stock", "fish_stock__pond", "fish_stock__species"
    )

    if pond_id:
        samplings = samplings.filter(fish_stock__pond_id=pond_id)

    if stock_id:
        samplings = samplings.filter(fish_stock_id=stock_id)

    samplings = samplings.order_by("sampled_on")

    paginator = Paginator(samplings, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    ponds = Pond.objects.filter(user=request.user)

    stocks = PondFishStock.objects.filter(
        user=request.user,
        status=PondFishStock.ACTIVE
    )

    if pond_id:
        stocks = stocks.filter(pond_id=pond_id)

    # -------------------------
    # GRAPH DATA
    # -------------------------

    graph_data = defaultdict(list)

    if pond_id:
        pond_stocks = PondFishStock.objects.filter(
            pond_id=pond_id,
            status=PondFishStock.ACTIVE
        )

        for stock in pond_stocks:
            species_name = stock.species.name

            # DAY 0 -> Stocking data
            graph_data[species_name].append({
                "day": 0,
                "avg_weight": float(stock.initial_avg_weight)
            })

            stock_samplings = samplings.filter(fish_stock=stock)

            for sampling in stock_samplings:
                graph_data[species_name].append({
                    "day": sampling.days_since_stocking,
                    "avg_weight": float(sampling.average_weight)
                })

    graph_data_json = json.dumps(graph_data)

    return render(
        request,
        "sampling/dashboard.html",
        {
            "page_obj": page_obj,
            "ponds": ponds,
            "stocks": stocks,
            "selected_pond": pond_id,
            "selected_stock": stock_id,
            "is_single_pond": bool(pond_id),
            "graph_data_json": graph_data_json,
        },
    )
