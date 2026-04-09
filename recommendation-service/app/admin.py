from django.contrib import admin
from .models import UserPurchaseHistory, RecommendationCache


@admin.register(UserPurchaseHistory)
class UserPurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id", "user_id", "product_id", "product_type", 
        "purchase_price", "rating", "purchased_at"
    ]
    list_filter = ["product_type", "rating", "purchased_at"]
    search_fields = ["user_id", "product_id"]
    readonly_fields = ["purchased_at", "updated_at"]
    ordering = ["-purchased_at"]


@admin.register(RecommendationCache)
class RecommendationCacheAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "cached_at", "expires_at"]
    list_filter = ["cached_at", "expires_at"]
    search_fields = ["user_id"]
    readonly_fields = ["cached_at"]
