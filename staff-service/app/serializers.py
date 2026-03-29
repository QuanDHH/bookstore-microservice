from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Staff, Role


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model  = Staff
        fields = [
            "username", "email", "password", "password2",
            "full_name", "phone_number", "address", "date_of_birth", "role",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        staff = Staff(**validated_data)
        staff.set_password(password)
        staff.save()
        return staff


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Staff
        fields = [
            "id", "username", "email", "full_name",
            "phone_number", "address", "date_of_birth",
            "role", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "username", "email", "role", "created_at", "updated_at"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, label="Confirm new password")

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs


# ── Product proxy serializers (forwarded to laptop/clothes services) ──────────

class LaptopSerializer(serializers.Serializer):
    """Mirrors the laptop-service fields."""
    name  = serializers.CharField(max_length=255)
    brand = serializers.CharField(max_length=100)
    cpu   = serializers.CharField(max_length=100)
    ram   = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock = serializers.IntegerField(min_value=0)
    image = serializers.ImageField(required=False, allow_null=True)


class ClothesSerializer(serializers.Serializer):
    """Mirrors the clothes-service fields."""
    SIZE_CHOICES     = ["XS", "S", "M", "L", "XL", "XXL"]
    CATEGORY_CHOICES = ["shirt", "pants", "dress", "jacket", "shoes", "hat", "other"]

    name     = serializers.CharField(max_length=255)
    brand    = serializers.CharField(max_length=100)
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    size     = serializers.ChoiceField(choices=SIZE_CHOICES)
    price    = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock    = serializers.IntegerField(min_value=0)
    image    = serializers.ImageField(required=False, allow_null=True)