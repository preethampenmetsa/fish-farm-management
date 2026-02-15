from django.urls import path
from . import views

app_name = "stock"

urlpatterns = [
    path("", views.stock_dashboard, name="stock-dashboard"),
    path("list/", views.pond_stock_list, name="pond-stock-list"),
    path("add/", views.add_pond_stock, name="add-pond-stock"),
    path("<int:stock_id>/close/", views.close_pond_stock, name="close-pond-stock"),
    path("pond-biomass/", views.pond_biomass_view, name="pond-biomass"),
]
