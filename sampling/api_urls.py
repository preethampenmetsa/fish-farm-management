from django.urls import path
from sampling.api_views import FishSamplingCreateAPI, FishSamplingListAPI, FishSamplingDetailAPI, PondStockListCreateAPI, PondStockCloseAPI

urlpatterns = [
    path("samplings/", FishSamplingListAPI.as_view(), name="api-samplings"),
    path(
        "samplings/<int:pk>/",
        FishSamplingDetailAPI.as_view(),
        name="api-sampling-detail",
    ),
    path(
        "samplings/create/",
        FishSamplingCreateAPI.as_view(),
        name="api-sampling-create",
    ),
    path("stocks/", PondStockListCreateAPI.as_view(), name="api-stock-list-create"),
    path("stocks/<int:pk>/close/", PondStockCloseAPI.as_view(), name="api-stock-close"),
]
