from django.urls import path
from . import views

app_name = "mortality"

urlpatterns = [
    path("add/", views.add_mortality, name="add-mortality"),
    path("logs/", views.mortality_logs, name="mortality-logs"),
]