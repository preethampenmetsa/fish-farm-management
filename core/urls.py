from django.urls import path
from core.views import home,pond_list,create_pond,species_list,add_species

urlpatterns = [
    path("", home, name="home"),
    path("ponds/", pond_list, name="pond-list"),
    path("ponds/create/", create_pond, name="create-pond"),
    path("species/", species_list, name="species-list"),
    path("species/add/", add_species, name="add-species"),    
]
