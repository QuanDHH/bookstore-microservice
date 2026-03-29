import requests
import logging
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Customer
from .serializers import RegisterSerializer, CustomerSerializer, LoginSerializer

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }


def create_cart_for_customer(customer_id):
    """
    Call cart-service to create an empty cart for the new customer.
    Fails silently — a cart error should never block registration.
    """
    try:
        url = f"{settings.CART_SERVICE_URL}/api/carts/create/"
        resp = requests.post(url, json={"customer_id": customer_id}, timeout=5)
        resp.raise_for_status()
        logger.info("Cart created for customer %s", customer_id)
    except requests.RequestException as exc:
        logger.warning("Could not create cart for customer %s: %s", customer_id, exc)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        customer = serializer.save()

        # Automatically create a cart in cart-service
        create_cart_for_customer(customer.id)

        tokens = get_tokens_for_user(customer)
        return Response(
            {
                "message": "Registration successful.",
                "customer": CustomerSerializer(customer).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = get_tokens_for_user(user)
        return Response(
            {
                "message": "Login successful.",
                "customer": CustomerSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomerSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = CustomerSerializer(
            request.user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."})
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)