from core import views
from django.urls import path

urlpatterns = [
    path("", views.home, name="home"),
    path("ponds/", views.pond_list, name="pond-list"),
    path("ponds/create/", views.create_pond, name="create-pond"),
    path("species/", views.species_list, name="species-list"),
    path("species/add/", views.add_species, name="add-species"), 
    path("pond/<int:pond_id>/", views.pond_detail, name="pond-detail"),
    path("register/", views.register, name="register"),

]
