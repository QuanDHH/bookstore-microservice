from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(),  name="customer-register"),
    path("login/",    LoginView.as_view(),     name="customer-login"),
    path("logout/",   LogoutView.as_view(),    name="customer-logout"),
    path("profile/",  ProfileView.as_view(),   name="customer-profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]