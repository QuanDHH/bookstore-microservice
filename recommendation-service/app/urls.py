from django.urls import path
from .views import (
    HealthCheckView,
    RecordPurchaseView,
    RateProductView,
    GetRecommendationsView,
    PurchaseHistoryView,
)

urlpatterns = [
    # Health check
    path("health/", HealthCheckView.as_view(), name="health-check"),

    # Purchase tracking
    path("purchase/", RecordPurchaseView.as_view(), name="record-purchase"),
    path("rate/", RateProductView.as_view(), name="rate-product"),

    # Recommendations
    path("recommendations/<int:user_id>/", GetRecommendationsView.as_view(), name="get-recommendations"),
    path("history/<int:user_id>/", PurchaseHistoryView.as_view(), name="purchase-history"),
]
