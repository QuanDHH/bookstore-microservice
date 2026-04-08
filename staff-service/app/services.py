"""
app/services.py

Handles all outbound HTTP calls from staff-service to
laptop-service and clothes-service.
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT = 10  # seconds


def _forward(method, url, data=None, files=None):
    """
    Generic HTTP forwarder.
    Returns (response_data, status_code).
    """
    try:
        if files:
            resp = requests.request(method, url, data=data, files=files, timeout=TIMEOUT)
        else:
            resp = requests.request(method, url, json=data, timeout=TIMEOUT)
        return resp.json(), resp.status_code
    except requests.exceptions.ConnectionError:
        logger.error("Connection error calling %s", url)
        return {"detail": f"Service unreachable: {url}"}, 503
    except requests.exceptions.Timeout:
        logger.error("Timeout calling %s", url)
        return {"detail": f"Service timed out: {url}"}, 504
    except Exception as exc:
        logger.exception("Unexpected error calling %s: %s", url, exc)
        return {"detail": "Unexpected gateway error."}, 500


# ── Laptop ────────────────────────────────────────────────────────────────────

def create_laptop(data, files=None):
    url = f"{settings.LAPTOP_SERVICE_URL}/api/laptops/"
    return _forward("POST", url, data=data, files=files)


def update_laptop(laptop_id, data, files=None, partial=False):
    url = f"{settings.LAPTOP_SERVICE_URL}/api/laptops/{laptop_id}/"
    method = "PATCH" if partial else "PUT"
    return _forward(method, url, data=data, files=files)


# ── Clothes ───────────────────────────────────────────────────────────────────

def create_clothes(data, files=None):
    url = f"{settings.CLOTHES_SERVICE_URL}/api/clothes/"
    return _forward("POST", url, data=data, files=files)


def update_clothes(clothes_id, data, files=None, partial=False):
    url = f"{settings.CLOTHES_SERVICE_URL}/api/clothes/{clothes_id}/"
    method = "PATCH" if partial else "PUT"
    return _forward(method, url, data=data, files=files)

# ── Mobile ───────────────────────────────────────────────────────────────────

def create_mobile(data, files=None):
    url = f"{settings.MOBILE_SERVICE_URL}/api/mobiles/"
    return _forward("POST", url, data=data, files=files)

def update_mobile(mobile_id, data, files=None, partial=False):
    url = f"{settings.MOBILE_SERVICE_URL}/api/mobiles/{mobile_id}/"
    method = "PATCH" if partial else "PUT"
    return _forward(method, url, data=data, files=files)