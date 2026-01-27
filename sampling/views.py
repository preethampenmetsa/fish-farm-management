from django.shortcuts import get_object_or_404, render, redirect
from calculator.utils import calculate_sampling_from_batches
from sampling.forms import SamplingForm, PondStockForm
from sampling.models import FishSampling, PondFishStock
from sampling.services import create_sampling_from_batches
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone

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
        .select_related("fish_stock", "fish_stock__pond", "fish_stock__species")
        .order_by("-sampled_on")
    )

    if stock_id:
        samplings = samplings.filter(fish_stock_id=stock_id)
    elif pond_id:
        samplings = samplings.filter(fish_stock__pond_id=pond_id)

    paginator = Paginator(samplings, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    ponds = PondFishStock.objects.filter(
        user=request.user,
        status=PondFishStock.ACTIVE
    ).values("pond__id", "pond__name").distinct()

    stocks = PondFishStock.objects.filter(
        user=request.user,
        status=PondFishStock.ACTIVE
    )

    return render(
        request,
        "sampling/dashboard.html",
        {
            "page_obj": page_obj,
            "ponds": ponds,
            "stocks": stocks,
            "selected_pond": pond_id,
            "selected_stock": stock_id,
        },
    )

@login_required
def pond_stock_list(request):
    stocks = PondFishStock.objects.filter(user=request.user)

    return render(
        request,
        "sampling/pond_stock_list.html",
        {"stocks": stocks}
    )
