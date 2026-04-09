from django.db import models


class UserPurchaseHistory(models.Model):
    """
    Tracks user purchases and interactions.
    This allows the recommendation engine to learn from user behavior.
    """
    user_id = models.IntegerField(
        help_text="Customer ID from customer-service"
    )
    product_id = models.IntegerField(
        help_text="Product ID (laptop, clothes, mobile, etc.)"
    )
    product_type = models.CharField(
        max_length=50,
        choices=[
            ("laptop", "Laptop"),
            ("clothes", "Clothes"),
            ("mobile", "Mobile"),
        ],
        help_text="Type of product purchased"
    )
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price at time of purchase"
    )
    rating = models.IntegerField(
        default=0,
        choices=[
            (1, "1 - Poor"),
            (2, "2 - Fair"),
            (3, "3 - Good"),
            (4, "4 - Very Good"),
            (5, "5 - Excellent"),
        ],
        help_text="User rating (1-5)"
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_purchase_history"
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["product_id"]),
            models.Index(fields=["product_type"]),
        ]
        ordering = ["-purchased_at"]
        unique_together = [["user_id", "product_id", "product_type"]]

    def __str__(self):
        return f"User {self.user_id} - {self.product_type} {self.product_id} (Rating: {self.rating})"


class RecommendationCache(models.Model):
    """
    Caches recommendations for scalability.
    Recommendations are expensive to compute, so we cache them.
    """
    user_id = models.IntegerField(unique=True)
    recommendations = models.JSONField(
        help_text="List of recommended products: [{'product_id': int, 'product_type': str, 'score': float}, ...]"
    )
    cached_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        help_text="Recommendation cache expiration time"
    )

    class Meta:
        db_table = "recommendation_cache"
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Recommendations Cache for User {self.user_id}"
