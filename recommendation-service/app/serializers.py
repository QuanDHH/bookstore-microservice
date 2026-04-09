from rest_framework import serializers
from .models import UserPurchaseHistory, RecommendationCache


class UserPurchaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPurchaseHistory
        fields = [
            "id",
            "user_id",
            "product_id",
            "product_type",
            "purchase_price",
            "rating",
            "purchased_at",
            "updated_at",
        ]
        read_only_fields = ["purchased_at", "updated_at"]


class RecommendationSerializer(serializers.Serializer):
    """
    Serializer for recommendation responses.
    Returns product recommendations with similarity scores.
    """
    product_id = serializers.IntegerField()
    product_type = serializers.CharField()
    score = serializers.FloatField(help_text="Similarity/confidence score (0-1)")
    reason = serializers.CharField(
        help_text="Why this product was recommended",
        required=False
    )


class RecommendationResponseSerializer(serializers.Serializer):
    """Response wrapper for recommendations."""
    user_id = serializers.IntegerField()
    recommendations = RecommendationSerializer(many=True)
    count = serializers.IntegerField()
    generated_at = serializers.DateTimeField()
