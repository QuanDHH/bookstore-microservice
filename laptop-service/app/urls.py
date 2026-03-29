from django.urls import path
from .views import LaptopListCreateView, LaptopDetailView

urlpatterns = [
    path("",        LaptopListCreateView.as_view(), name="laptop-list-create"),
    path("<int:pk>/", LaptopDetailView.as_view(),   name="laptop-detail"),
]