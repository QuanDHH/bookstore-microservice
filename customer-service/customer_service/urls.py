from django.urls import path, include

urlpatterns = [
    path("api/customers/", include("app.urls")),
]