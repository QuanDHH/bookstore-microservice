"""
gateway/settings.py  –  API Gateway Django settings
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "proxy",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "api_gateway.urls"
WSGI_APPLICATION = "api_gateway.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    }
]

# No database needed for a pure proxy gateway
DATABASES = {}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "/static/"

# ── Service registry ──────────────────────────────────────────────────────────
# Each key matches the first path segment after /api/
SERVICE_URLS = {
    "staff": os.getenv("STAFF_SERVICE_URL", "http://staff-service:8001"),
    "customers": os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8002"),
    "cart": os.getenv("CART_SERVICE_URL", "http://cart-service:8003"),
    "laptop": os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8004"),
    "clothes": os.getenv("CLOTHES_SERVICE_URL", "http://clothes-service:8005"),
}

SERVICE_PATHS = {
    "staff": "api/staff",
    "customers": "api/customers",
    "cart": "api/carts",
    "laptop": "api/laptops",
    "clothes": "api/clothes",
}
