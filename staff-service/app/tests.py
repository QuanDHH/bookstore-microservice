import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


class DummyUpstreamResponse:
    def __init__(self, status_code=200, body=None, headers=None):
        self.status = status_code
        self._body = body or b"{}"
        self.headers = headers or {"Content-Type": "application/json"}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@override_settings(
    DB_ENGINE="django.db.backends.sqlite3",
    DB_NAME=":memory:",
    LAPTOP_SERVICE_URL="http://laptop-service:8004",
    CLOTHES_SERVICE_URL="http://clothes-service:8005",
)
class StaffServiceTests(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password="StrongPass123!",
        )

    def authenticate(self):
        response = self.client.post(
            "/api/staff/login/",
            {"username": "admin", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_staff_can_log_in(self):
        response = self.client.post(
            "/api/staff/login/",
            {"username": "admin", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["staff"]["username"], "admin")
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    @patch("app.views.urllib_request.urlopen")
    def test_authenticated_staff_can_proxy_laptop_creation(self, mock_urlopen):
        mock_urlopen.return_value = DummyUpstreamResponse(
            status_code=201,
            body=json.dumps({"id": 1, "name": "ThinkPad X1"}).encode("utf-8"),
        )
        self.authenticate()

        response = self.client.post(
            "/api/staff/laptops/",
            {
                "name": "ThinkPad X1",
                "brand": "Lenovo",
                "cpu": "Intel Core Ultra 7",
                "ram": 32,
                "price": "1999.99",
                "stock": 12,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "ThinkPad X1")

        upstream_request = mock_urlopen.call_args.args[0]
        self.assertEqual(upstream_request.full_url, "http://laptop-service:8004/api/laptops/")
        self.assertEqual(upstream_request.get_method(), "POST")
