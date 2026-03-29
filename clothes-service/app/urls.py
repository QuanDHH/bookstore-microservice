from django.urls import path
from .views import ClothesListCreateView, ClothesDetailView

urlpatterns = [
    path("",           ClothesListCreateView.as_view(), name="clothes-list-create"),
    path("<int:pk>/",  ClothesDetailView.as_view(),     name="clothes-detail"),
]