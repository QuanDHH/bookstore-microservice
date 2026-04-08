from rest_framework import serializers
from .models import Mobile


class MobileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model  = Mobile
        fields = [
            "id", "name", "brand", "ram", "storage",
            "battery", "price", "stock", "image",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MobileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    class Meta:
        model  = Mobile
        fields = ["id", "name", "brand", "ram", "storage", "battery", "price", "stock", "image"]