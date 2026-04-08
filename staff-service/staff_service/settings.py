from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "staff_service.urls"
WSGI_APPLICATION = "staff_service.wsgi.application"

# ── Database (MySQL) ──────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   os.getenv("DB_ENGINE",   "django.db.backends.mysql"),
        "NAME":     os.getenv("DB_NAME",     "staff_db"),
        "USER":     os.getenv("DB_USER",     "staff_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "staff_pass"),
        "HOST":     os.getenv("DB_HOST",     "localhost"),
        "PORT":     os.getenv("DB_PORT",     "3306"),
    }
}

# ── Custom user model ─────────────────────────────────────────────────────────
AUTH_USER_MODEL = "app.Staff"

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ── JWT ───────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":    timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME":   timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":    True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES":        ("Bearer",),
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ── Inter-service URLs ────────────────────────────────────────────────────────
LAPTOP_SERVICE_URL  = os.getenv("LAPTOP_SERVICE_URL",  "http://laptop-service:8004")
CLOTHES_SERVICE_URL = os.getenv("CLOTHES_SERVICE_URL", "http://clothes-service:8005")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8006")

# ── Misc ──────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_TZ = True