from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from stock.forms import PondStockForm
from stock.models import PondFishStock
from stock.services import get_single_pond_biomass
from core.models import Pond


@login_required
def add_pond_stock(request):
    if request.method == "POST":
        form = PondStockForm(request.POST, user=request.user)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            return redirect("stock:pond-stock-list")
    else:
        form = PondStockForm(user=request.user)

    return render(request, "stock/add_pond_stock.html", {"form": form})


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

    return redirect("stock:pond-stock-list")


@login_required
def pond_stock_list(request):
    pond_id = request.GET.get("pond_id")
    ponds = Pond.objects.filter(user=request.user)
    stocks = PondFishStock.objects.filter(user=request.user)
    selected_pond = None

    if pond_id:
        selected_pond = ponds.filter(id=pond_id).first()
        stocks = stocks.filter(pond_id=pond_id)

    context = {
        "stocks": stocks,
        "ponds": ponds,
        "selected_pond": selected_pond,
    }

    return render(request, "stock/pond_stock_list.html", context)


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

    return render(
        request,
        "stock/pond_biomass.html",
        {
            "ponds": ponds,
            "selected_pond": selected_pond,
            "biomass": biomass_data,
        }
    )

@login_required
def stock_dashboard(request):
    stocks = PondFishStock.objects.filter(user=request.user)

    active_stocks = stocks.filter(status=PondFishStock.ACTIVE)
    closed_stocks = stocks.filter(status=PondFishStock.CLOSED)

    total_alive_fish = sum(
        stock.alive_fish_count for stock in active_stocks
    )

    total_biomass = sum(
        stock.total_live_weight for stock in active_stocks
    )

    context = {
        "active_stocks": active_stocks,
        "total_active_stocks": active_stocks.count(),
        "total_closed_stocks": closed_stocks.count(),
        "total_alive_fish": total_alive_fish,
        "total_biomass": total_biomass,
    }

    return render(request, "stock/stock_dashboard.html", context)
