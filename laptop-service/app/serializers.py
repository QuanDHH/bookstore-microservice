from rest_framework import serializers
from .models import Laptop


class LaptopSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model  = Laptop
        fields = [
            "id", "name", "brand", "cpu", "ram",
            "price", "stock", "image",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LaptopListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view — omits heavy fields."""
    class Meta:
        model  = Laptop
        fields = ["id", "name", "brand", "cpu", "ram", "price", "stock", "image"]