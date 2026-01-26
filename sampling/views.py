from django.shortcuts import render, redirect
from calculator.utils import calculate_sampling_from_batches
from sampling.forms import SamplingForm, PondStockForm
from sampling.models import FishSampling
from sampling.services import create_sampling_from_batches
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

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
def sampling_dashboard(request):
    samplings = (
        FishSampling.objects
        .filter(user=request.user)
        .select_related("fish_stock")
        .order_by("-sampled_on")
    )

    paginator = Paginator(samplings, 10)  # 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "sampling/dashboard.html",
        {"page_obj": page_obj}
    )
