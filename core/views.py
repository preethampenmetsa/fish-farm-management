from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import FishSpeciesForm, PondForm
from core.models import FishSpecies, Pond
from django.db.models import Q


@login_required
def home(request):
    return render(request, "core/home.html")

@login_required
def pond_list(request):
    ponds = Pond.objects.filter(user=request.user)
    return render(request, "core/pond_list.html", {"ponds": ponds})


@login_required
def create_pond(request):
    if request.method == "POST":
        form = PondForm(request.POST, user=request.user)
        if form.is_valid():
            pond = form.save(commit=False)
            pond.user = request.user  # 🔒 ownership enforced here
            pond.save()
            return redirect("pond-list")
    else:
        form = PondForm(user=request.user)

    return render(request, "core/create_pond.html", {"form": form})

@login_required
def species_list(request):
    species = FishSpecies.objects.filter(
        Q(user__isnull=True) | Q(user=request.user)
    ).order_by("name")

    return render(
        request,
        "core/species_list.html",
        {"species": species}
    )


@login_required
def add_species(request):
    if request.method == "POST":
        form = FishSpeciesForm(request.POST)
        if form.is_valid():
            species = form.save(commit=False)
            species.user = request.user   # 🔑 ownership applied here
            species.save()
            return redirect("species-list")
    else:
        form = FishSpeciesForm()

    return render(
        request,
        "core/add_species.html",
        {"form": form}
    )


