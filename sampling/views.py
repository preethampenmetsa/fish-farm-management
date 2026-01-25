from django.shortcuts import render, redirect
from calculator.utils import calculate_sampling_from_batches
from sampling.forms import SamplingForm
from sampling.models import FishSampling
from sampling.services import create_sampling_from_batches
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required



def add_sampling(request):
    if request.method == "POST":
        form = SamplingForm(request.POST)

        if form.is_valid():
            # 👈 If user clicks "Go back and edit"
            if "edit" in request.POST:
                return render(
                    request,
                    "sampling/add_sampling.html",
                    {"form": form},
                )

            fish_stock = form.cleaned_data["fish_stock"]
            sampled_on = form.cleaned_data["sampled_on"]
            batches = form.cleaned_data["fish_batches"]

            # 👈 Preview step
            if "confirm" not in request.POST:
                preview = calculate_sampling_from_batches(batches)

                return render(
                    request,
                    "sampling/preview_sampling.html",
                    {
                        "form": form,
                        "preview": preview,
                    },
                )

            # 👈 Final save
            create_sampling_from_batches(
                fish_stock=fish_stock,
                sampled_on=sampled_on,
                batches=batches,
            )

            return redirect("sampling-success")

    else:
        form = SamplingForm()

    return render(request, "sampling/add_sampling.html", {"form": form})


def sampling_success(request):
    return render(request, "sampling/success.html")

@login_required
def sampling_dashboard(request):
    samplings = (
        FishSampling.objects
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
