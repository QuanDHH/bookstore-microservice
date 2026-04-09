from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.utils import timezone
from datetime import timedelta

from .models import UserPurchaseHistory, RecommendationCache
from .serializers import (
    UserPurchaseHistorySerializer,
    RecommendationResponseSerializer,
)
from .recommendation_engine import get_recommendation_engine, rebuild_engine


class HealthCheckView(APIView):
    """
    GET /health/  - Service health check
    """
    permission_classes = []

    def get(self, request):
        return Response(
            {"status": "ok", "service": "recommendation-service"},
            status=status.HTTP_200_OK
        )


class RecordPurchaseView(APIView):
    """
    POST /api/purchase/  - Record a user purchase
    
    Request body:
    {
        "user_id": 123,
        "product_id": 456,
        "product_type": "laptop",  // "laptop", "clothes", or "mobile"
        "purchase_price": 999.99
    }
    """
    permission_classes = []
    parser_classes = [JSONParser]

    def post(self, request):
        # Create or update purchase history
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")
        product_type = request.data.get("product_type")
        purchase_price = request.data.get("purchase_price")

        if not all([user_id, product_id, product_type, purchase_price]):
            return Response(
                {"detail": "Missing required fields: user_id, product_id, product_type, purchase_price"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if product_type not in ["laptop", "clothes", "mobile"]:
            return Response(
                {"detail": "Invalid product_type. Must be: laptop, clothes, or mobile"},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase, created = UserPurchaseHistory.objects.get_or_create(
            user_id=user_id,
            product_id=product_id,
            product_type=product_type,
            defaults={"purchase_price": purchase_price, "rating": 0}
        )

        if not created:
            purchase.purchase_price = purchase_price
            purchase.save(update_fields=["purchase_price"])

        # Invalidate recommendation cache for this user
        RecommendationCache.objects.filter(user_id=user_id).delete()

        # Rebuild the recomm engine after new purchase
        rebuild_engine()

        serializer = UserPurchaseHistorySerializer(purchase)
        return Response(
            {
                "message": "Purchase recorded successfully",
                "purchase": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class RateProductView(APIView):
    """
    POST /api/rate/  - Rate a purchased product
    
    Request body:
    {
        "user_id": 123,
        "product_id": 456,
        "product_type": "laptop",
        "rating": 5  // 1-5
    }
    """
    permission_classes = []
    parser_classes = [JSONParser]

    def post(self, request):
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")
        product_type = request.data.get("product_type")
        rating = request.data.get("rating")

        if not all([user_id, product_id, product_type, rating]):
            return Response(
                {"detail": "Missing required fields: user_id, product_id, product_type, rating"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return Response(
                {"detail": "Rating must be an integer between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            purchase = UserPurchaseHistory.objects.get(
                user_id=user_id,
                product_id=product_id,
                product_type=product_type
            )
            purchase.rating = rating
            purchase.save(update_fields=["rating"])

            # Invalidate cache
            RecommendationCache.objects.filter(user_id=user_id).delete()

            # Rebuild engine
            rebuild_engine()

        except UserPurchaseHistory.DoesNotExist:
            return Response(
                {"detail": "Purchase history not found for this user and product"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserPurchaseHistorySerializer(purchase)
        return Response(
            {
                "message": "Rating submitted successfully",
                "purchase": serializer.data
            },
            status=status.HTTP_200_OK
        )


class GetRecommendationsView(APIView):
    """
    GET /api/recommendations/<user_id>/
    
    Query parameters:
      ?count=5        - Number of recommendations (default: 5)
      ?type=laptop    - Filter by product type (optional)
    
    Returns:
    {
        "user_id": 123,
        "recommendations": [
            {
                "product_id": 456,
                "product_type": "laptop",
                "score": 0.85,
                "reason": "Similar to products you liked"
            },
            ...
        ],
        "count": 5,
        "generated_at": "2024-04-09T10:30:00Z"
    }
    """
    permission_classes = []

    def get(self, request, user_id):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid user_id. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get query parameters
        count = request.query_params.get("count", 5)
        product_type = request.query_params.get("type")

        try:
            count = int(count)
            if count < 1 or count > 50:
                count = 5
        except (ValueError, TypeError):
            count = 5

        # Check cache first
        now = timezone.now()
        cache = RecommendationCache.objects.filter(
            user_id=user_id,
            expires_at__gt=now
        ).first()

        if cache:
            recommendations = cache.recommendations
        else:
            # Get fresh recommendations
            engine = get_recommendation_engine()
            recommendations = engine.get_recommendations(
                user_id, 
                n_recommendations=count,
                product_type=product_type
            )

            # Cache the recommendations (valid for 24 hours)
            RecommendationCache.objects.update_or_create(
                user_id=user_id,
                defaults={
                    "recommendations": recommendations,
                    "expires_at": now + timedelta(hours=24)
                }
            )

        response_data = {
            "user_id": user_id,
            "recommendations": recommendations[:count],
            "count": len(recommendations[:count]),
            "generated_at": now.isoformat()
        }

        serializer = RecommendationResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PurchaseHistoryView(APIView):
    """
    GET /api/history/<user_id>/  - Get user's purchase history
    """
    permission_classes = []

    def get(self, request, user_id):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid user_id. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchases = UserPurchaseHistory.objects.filter(user_id=user_id)

        if not purchases.exists():
            return Response(
                {"detail": "No purchase history found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserPurchaseHistorySerializer(purchases, many=True)
        return Response(
            {
                "user_id": user_id,
                "purchases": serializer.data,
                "count": purchases.count()
            },
            status=status.HTTP_200_OK
        )
