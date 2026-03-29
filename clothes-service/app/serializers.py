from rest_framework import serializers
from .models import Clothes, Category, Size


class ClothesSerializer(serializers.ModelSerializer):
    image    = serializers.ImageField(required=False, allow_null=True)
    category = serializers.ChoiceField(choices=Category.choices)
    size     = serializers.ChoiceField(choices=Size.choices)

    class Meta:
        model  = Clothes
        fields = [
            "id", "name", "brand", "category", "size",
            "price", "stock", "image",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClothesListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    class Meta:
        model  = Clothes
        fields = ["id", "name", "brand", "category", "size", "price", "stock", "image"]