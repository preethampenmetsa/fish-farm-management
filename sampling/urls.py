from django.urls import path,include
from sampling.views import add_sampling, sampling_dashboard, sampling_success, add_pond_stock, pond_stock_list, close_pond_stock, add_mortality, pond_biomass_view

urlpatterns = [
    path("add/", add_sampling, name="add-sampling"),
    path("success/", sampling_success, name="sampling-success"),
    path("stock/add/", add_pond_stock, name="add-pond-stock"),
    path("stock/", pond_stock_list, name="pond-stock-list"),
    path("dashboard/", sampling_dashboard, name="sampling-dashboard"),
    path("stock/<int:stock_id>/close/",close_pond_stock,name="close-pond-stock"),
    path("mortality/add/", add_mortality, name="add-mortality"),
    path("pond-biomass/", pond_biomass_view, name="pond_biomass"),

]
