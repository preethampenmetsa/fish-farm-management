from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from mortality.forms import FishMortalityForm
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import FishMortality
from stock.models import PondFishStock
from core.models import Pond


@login_required
def add_mortality(request):
    if request.method == "POST":
        form = FishMortalityForm(request.POST, user=request.user)
        if form.is_valid():
            mortality = form.save(commit=False)
            mortality.user = request.user
            mortality.save()
            return redirect("sampling:sampling-dashboard")
    else:
        form = FishMortalityForm(user=request.user)

    return render(request, "mortality/add_mortality.html", {"form": form})

@login_required
def mortality_logs(request):
    pond_id = request.GET.get("pond")
    stock_id = request.GET.get("stock")

    logs = FishMortality.objects.select_related(
        "fish_stock",
        "fish_stock__pond",
        "fish_stock__species"
    ).order_by("-date")

    ponds = Pond.objects.filter(user=request.user)
    stocks = PondFishStock.objects.filter(user=request.user)

    if pond_id:
        logs = logs.filter(fish_stock__pond_id=pond_id)
        stocks = stocks.filter(pond_id=pond_id)

    if stock_id:
        logs = logs.filter(fish_stock_id=stock_id)

    paginator = Paginator(logs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "mortality/mortality_logs.html", {
        "page_obj": page_obj,
        "ponds": ponds,
        "stocks": stocks,
        "selected_pond": pond_id,
        "selected_stock": stock_id,
    })