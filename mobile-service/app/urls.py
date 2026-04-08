from django.urls import path
from .views import MobileListCreateView, MobileDetailView

urlpatterns = [
    path("",           MobileListCreateView.as_view(), name="mobile-list-create"),
    path("<int:pk>/",  MobileDetailView.as_view(),     name="mobile-detail"),
]