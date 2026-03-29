from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView,
    ProfileView, ChangePasswordView,
    LaptopCreateView, LaptopUpdateView,
    ClothesCreateView, ClothesUpdateView,
)

urlpatterns = [
    # -- Auth
    path("register/",         RegisterView.as_view(),      name="staff-register"),
    path("login/",            LoginView.as_view(),          name="staff-login"),
    path("logout/",           LogoutView.as_view(),         name="staff-logout"),
    path("profile/",          ProfileView.as_view(),        name="staff-profile"),
    path("change-password/",  ChangePasswordView.as_view(), name="staff-change-password"),
    path("token/refresh/",    TokenRefreshView.as_view(),   name="staff-token-refresh"),

    # -- Laptop management
    path("products/laptops/",              LaptopCreateView.as_view(), name="staff-laptop-create"),
    path("products/laptops/<int:laptop_id>/", LaptopUpdateView.as_view(), name="staff-laptop-update"),

    # -- Clothes management
    path("products/clothes/",                 ClothesCreateView.as_view(), name="staff-clothes-create"),
    path("products/clothes/<int:clothes_id>/", ClothesUpdateView.as_view(), name="staff-clothes-update"),
]