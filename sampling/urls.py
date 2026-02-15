from django.urls import path
from sampling.views import add_sampling, sampling_dashboard, sampling_success

app_name = "sampling"
urlpatterns = [
    path("add/", add_sampling, name="add-sampling"),
    path("success/", sampling_success, name="sampling-success"),
    path("dashboard/", sampling_dashboard, name="sampling-dashboard"),
]
