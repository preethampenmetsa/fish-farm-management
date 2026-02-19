from django.urls import path
from . import views

app_name = "feed"

urlpatterns = [
    path("<int:pond_id>/", views.feed_dashboard, name="feed-dashboard"),
    path("stock/add/", views.add_feed_stock, name="add-feed-stock"),
    path("stock/", views.feed_stock_list, name="feed-stock-list"),
    path("usage/add/", views.add_feed_usage, name="add-feed-usage"),
    path("usage/", views.feed_usage_list, name="feed-usage-list"),
    path("feed-types/", views.feed_type_list, name="feed-type-list"),
    path("feed-types/add/", views.add_feed_type, name="add-feed-type"),
]
