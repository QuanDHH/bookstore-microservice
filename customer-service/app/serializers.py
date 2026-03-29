from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Customer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = Customer
        fields = [
            "username", "email", "password", "password2",
            "full_name", "phone_number", "address", "date_of_birth",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id", "username", "email", "full_name",
            "phone_number", "address", "date_of_birth",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "username", "email", "created_at", "updated_at"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)