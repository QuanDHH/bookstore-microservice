from django.urls import path
from .views import CreateCartView, CartView, AddItemView, RemoveItemView

urlpatterns = [
    path("create/",                    CreateCartView.as_view(), name="cart-create"),
    path("<int:customer_id>/",         CartView.as_view(),       name="cart-detail"),
    path("<int:customer_id>/add/",     AddItemView.as_view(),    name="cart-add-item"),
    path("<int:customer_id>/remove/",  RemoveItemView.as_view(), name="cart-remove-item"),
]