from django.urls import path,include
from sampling.views import add_sampling, sampling_dashboard, sampling_success, add_pond_stock

urlpatterns = [
    path("add/", add_sampling, name="add-sampling"),
    path("success/", sampling_success, name="sampling-success"),
    path("stock/add/", add_pond_stock, name="add-pond-stock"),
    path("dashboard/", sampling_dashboard, name="sampling-dashboard"),
]
