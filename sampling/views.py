from django.shortcuts import get_object_or_404, render, redirect
from calculator.utils import calculate_sampling_from_batches
from core.models import Pond
from sampling.forms import FishMortalityForm, SamplingForm, PondStockForm
from sampling.models import FishSampling, PondFishStock
from sampling.services import create_sampling_from_batches, get_single_pond_biomass
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from collections import defaultdict
import json

def add_sampling(request):
    if request.method == "POST":
        form = SamplingForm(request.POST, user=request.user)

        if form.is_valid():
            # If user clicks "Go back and edit"
            if "edit" in request.POST:
                return render(
                    request,
                    "sampling/add_sampling.html",
                    {"form": form},
                )

            fish_stock = form.cleaned_data["fish_stock"]
            sampled_on = form.cleaned_data["sampled_on"]
            batch_size = form.cleaned_data["batch_size"]
            batch_weights = form.cleaned_data["batch_weights"]


            # Preview step
            if "confirm" not in request.POST:
                preview = calculate_sampling_from_batches(
                            batch_size=batch_size,
                            batches=batch_weights,
                        )

                return render(
                    request,
                    "sampling/preview_sampling.html",
                    {
                        "form": form,
                        "preview": preview,
                    },
                )

            # Final save
            create_sampling_from_batches(
                user=request.user,
                fish_stock=fish_stock,
                sampled_on=sampled_on,
                batch_size=batch_size,
                batches=batch_weights,
            )

            return redirect("sampling-success")

    else:
        form = SamplingForm(user=request.user)

    return render(request, "sampling/add_sampling.html", {"form": form})


def sampling_success(request):
    return render(request, "sampling/success.html")

@login_required
def add_pond_stock(request):
    if request.method == "POST":
        form = PondStockForm(request.POST, user=request.user)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            return redirect("pond-stock-list")
    else:
        form = PondStockForm(user=request.user)

    return render(
        request,
        "sampling/add_pond_stock.html",
        {"form": form},
    )

@login_required
def close_pond_stock(request, stock_id):
    stock = get_object_or_404(
        PondFishStock,
        id=stock_id,
        user=request.user,
        status=PondFishStock.ACTIVE
    )

    stock.status = PondFishStock.CLOSED
    stock.closed_on = timezone.now().date()
    stock.save()

    return redirect("pond-stock-list")

# -------------------------
# Sampling Dashboard (FILTERED)
# -------------------------
@login_required
def sampling_dashboard(request):
    pond_id = request.GET.get("pond")
    stock_id = request.GET.get("stock")

    samplings = (
        FishSampling.objects
        .filter(user=request.user)
        .select_related(
            "fish_stock",
            "fish_stock__pond",
            "fish_stock__species"
        )
        .order_by("-sampled_on")
    )

    # Apply filters in correct priority
    if pond_id:
        samplings = samplings.filter(fish_stock__pond_id=pond_id)

    if stock_id:
        samplings = samplings.filter(fish_stock_id=stock_id)

    paginator = Paginator(samplings, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    # ✅ Ponds for dropdown
    ponds = Pond.objects.filter(user=request.user)

    # ✅ Stocks filtered by selected pond
    stocks = PondFishStock.objects.filter(
        user=request.user,
        status=PondFishStock.ACTIVE
    )

    if pond_id:
        stocks = stocks.filter(pond_id=pond_id)

    all_samplings = (
        samplings
        .select_related("fish_stock")
        .order_by("sampled_on")
    )
    graph_data = defaultdict(list)
    seen_stocks = set()

    for s in all_samplings:
        stock = s.fish_stock

        if not stock.stocked_on:
            continue

        species_name = stock.species.name
        stock_key = stock.id  # important to avoid duplicates

        # ✅ Add stocking-day average ONCE per stock
        if stock_key not in seen_stocks:
            graph_data[species_name].append({
                "day": 0,
                "avg_weight": float(stock.initial_avg_weight),
            })
            seen_stocks.add(stock_key)

        days_since_stocked = (s.sampled_on - stock.stocked_on).days

        graph_data[species_name].append({
            "day": days_since_stocked,
            "avg_weight": float(s.average_weight),
        })
    is_single_pond = bool(pond_id)
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
            "graph_data_json": graph_data_json,
            "is_single_pond": is_single_pond,
        }
    )

@login_required
def pond_stock_list(request):
    stocks = PondFishStock.objects.filter(user=request.user)

    return render(
        request,
        "sampling/pond_stock_list.html",
        {"stocks": stocks}
    )

@login_required
def add_mortality(request):
    if request.method == "POST":
        form = FishMortalityForm(request.POST, user=request.user)
        if form.is_valid():
            mortality = form.save(commit=False)
            mortality.user = request.user
            mortality.save()
            return redirect("sampling-dashboard")
    else:
        form = FishMortalityForm(user=request.user)

    return render(
        request,
        "sampling/add_mortality.html",
        {"form": form}
    )

@login_required
def pond_biomass_view(request):
    ponds = Pond.objects.filter(user=request.user)
    selected_pond = None
    biomass_data = None

    pond_id = request.GET.get("pond_id")

    if pond_id:
        selected_pond = ponds.filter(id=pond_id).first()
        if selected_pond:
            biomass_data = get_single_pond_biomass(selected_pond)
        if biomass_data:
            # Convert total pond biomass to tonnes
            biomass_data["total_biomass_tons"] = round(
                biomass_data["total_biomass"] / 1_000_000, 2
            )

            # Convert species biomass to tonnes
            for species in biomass_data["species_data"].values():
                species["total_weight_tons"] = round(
                    species["total_weight"] / 1_000_000, 2
                )
    context = {
        "ponds": ponds,
        "selected_pond": selected_pond,
        "biomass": biomass_data,
    }

    return render(request, "sampling/pond_biomass.html", context)

