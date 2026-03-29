from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Staff
from .serializers import (
    RegisterSerializer, StaffSerializer, LoginSerializer,
    ChangePasswordSerializer, LaptopSerializer, ClothesSerializer,
)
from .permissions import IsAdminStaff
from . import services


# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


# ── Auth views ────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        staff = serializer.save()
        return Response(
            {
                "message": "Registration successful.",
                "staff": StaffSerializer(staff).data,
                "tokens": get_tokens_for_user(staff),
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
        return Response(
            {
                "message": "Login successful.",
                "staff": StaffSerializer(user).data,
                "tokens": get_tokens_for_user(user),
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response({"message": "Logged out successfully."})
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(StaffSerializer(request.user).data)

    def patch(self, request):
        serializer = StaffSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"message": "Password changed successfully."})


# ── Laptop management (proxy to laptop-service) ───────────────────────────────

class LaptopCreateView(APIView):
    """
    POST /api/staff/products/laptops/
    Any authenticated staff can add a laptop.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = LaptopSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Separate image from other fields for multipart forwarding
        data  = {k: v for k, v in serializer.validated_data.items() if k != "image"}
        files = None
        if "image" in request.FILES:
            img = request.FILES["image"]
            files = {"image": (img.name, img.read(), img.content_type)}

        result, status_code = services.create_laptop(data, files)
        return Response(result, status=status_code)


class LaptopUpdateView(APIView):
    """
    PUT   /api/staff/products/laptops/<id>/  — full update (admin only)
    PATCH /api/staff/products/laptops/<id>/  — partial update (any staff)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == "PUT":
            return [IsAdminStaff()]
        return [IsAuthenticated()]

    def _forward_update(self, request, laptop_id, partial):
        serializer = LaptopSerializer(data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data  = {k: v for k, v in serializer.validated_data.items() if k != "image"}
        files = None
        if "image" in request.FILES:
            img = request.FILES["image"]
            files = {"image": (img.name, img.read(), img.content_type)}

        result, status_code = services.update_laptop(laptop_id, data, files, partial=partial)
        return Response(result, status=status_code)

    def put(self, request, laptop_id):
        return self._forward_update(request, laptop_id, partial=False)

    def patch(self, request, laptop_id):
        return self._forward_update(request, laptop_id, partial=True)


# ── Clothes management (proxy to clothes-service) ─────────────────────────────

class ClothesCreateView(APIView):
    """
    POST /api/staff/products/clothes/
    Any authenticated staff can add a clothes item.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ClothesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data  = {k: v for k, v in serializer.validated_data.items() if k != "image"}
        files = None
        if "image" in request.FILES:
            img = request.FILES["image"]
            files = {"image": (img.name, img.read(), img.content_type)}

        result, status_code = services.create_clothes(data, files)
        return Response(result, status=status_code)


class ClothesUpdateView(APIView):
    """
    PUT   /api/staff/products/clothes/<id>/  — full update (admin only)
    PATCH /api/staff/products/clothes/<id>/  — partial update (any staff)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == "PUT":
            return [IsAdminStaff()]
        return [IsAuthenticated()]

    def _forward_update(self, request, clothes_id, partial):
        serializer = ClothesSerializer(data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data  = {k: v for k, v in serializer.validated_data.items() if k != "image"}
        files = None
        if "image" in request.FILES:
            img = request.FILES["image"]
            files = {"image": (img.name, img.read(), img.content_type)}

        result, status_code = services.update_clothes(clothes_id, data, files, partial=partial)
        return Response(result, status=status_code)

    def put(self, request, clothes_id):
        return self._forward_update(request, clothes_id, partial=False)

    def patch(self, request, clothes_id):
        return self._forward_update(request, clothes_id, partial=True)