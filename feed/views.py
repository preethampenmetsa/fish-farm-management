from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from feed.forms import FeedTypeForm, FeedUsageForm, PondFeedStockForm
from feed.models import FeedType, FeedUsageLog, PondFeedStock
from feed.services import record_feed_usage

@login_required
def feed_type_list(request):
    feed_types = FeedType.objects.filter(user=request.user)
    return render(request, "feed/feed_type_list.html", {"feed_types": feed_types})


@login_required
def add_feed_type(request):
    if request.method == "POST":
        form = FeedTypeForm(request.POST)
        if form.is_valid():
            feed_type = form.save(commit=False)
            feed_type.user = request.user
            feed_type.save()
            return redirect("feed:feed-type-list")
    else:
        form = FeedTypeForm()

    return render(request, "feed/add_feed_type.html", {"form": form})

@login_required
def add_feed_stock(request):
    if request.method == "POST":
        form = PondFeedStockForm(request.POST, user=request.user)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            return redirect("feed:feed-stock-list")
    else:
        form = PondFeedStockForm(user=request.user)

    return render(request, "feed/add_feed_stock.html", {"form": form})



@login_required
def add_feed_usage(request):
    if request.method == "POST":
        form = FeedUsageForm(request.POST)

        if form.is_valid():
            try:
                record_feed_usage(
                    user=request.user,
                    pond_feed_stock=form.cleaned_data["pond_feed_stock"],
                    quantity_kg=form.cleaned_data["quantity_kg"],
                    given_on=form.cleaned_data["given_on"],
                )
                messages.success(request, "Feed usage recorded successfully.")
                return redirect("feed:feed-dashboard")

            except ValidationError as e:
                messages.error(request, e.message)

    else:
        form = FeedUsageForm()

    return render(request, "feed/add_feed_usage.html", {"form": form})


@login_required
def feed_stock_list(request):
    stocks = (
        PondFeedStock.objects
        .filter(user=request.user)
        .select_related("pond", "feed_type")
    )

    return render(
        request,
        "feed/feed_stock_list.html",
        {"stocks": stocks}
    )


@login_required
def feed_usage_list(request):
    logs = (
        FeedUsageLog.objects
        .filter(user=request.user)
        .select_related("pond_feed_stock", "pond_feed_stock__pond")
        .order_by("-given_on")
    )

    return render(
        request,
        "feed/feed_usage_list.html",
        {"logs": logs}
    )

@login_required
def feed_dashboard(request):
    stocks = (
        PondFeedStock.objects
        .filter(user=request.user)
        .select_related("pond", "feed_type")
    )

    total_purchased = sum(s.purchased_quantity_kg for s in stocks)
    total_used = sum(s.total_used() for s in stocks)
    total_remaining = sum(s.current_stock() for s in stocks)

    context = {
        "stocks": stocks,
        "total_purchased": total_purchased,
        "total_used": total_used,
        "total_remaining": total_remaining,
    }

    return render(request, "feed/feed_dashboard.html", context)



