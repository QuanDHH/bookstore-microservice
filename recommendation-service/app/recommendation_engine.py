import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from django.db import models
from .models import UserPurchaseHistory


class CollaborativeFilteringEngine:
    """
    Item-based Collaborative Filtering using scikit-learn.
    
    Finds similar products based on user ratings and purchase patterns.
    Uses cosine similarity to measure product similarity.
    """

    def __init__(self, min_common_users=1):
        """
        Args:
            min_common_users: Minimum number of users who rated both products
        """
        self.min_common_users = min_common_users
        self.user_product_matrix = None
        self.product_similarity = None
        self.user_id_map = None
        self.product_id_map = None

    def build_user_product_matrix(self):
        """
        Build user-product rating matrix from purchase history.
        
        Returns:
            tuple: (user_product_matrix, user_id_map, product_id_map)
        """
        # Fetch all purchase history with ratings
        purchases = UserPurchaseHistory.objects.filter(rating__gt=0).values(
            "user_id", "product_id", "rating", "product_type"
        )

        if not purchases.exists():
            return None, {}, {}

        # Create unique mappings for users and products
        unique_users = sorted(set(p["user_id"] for p in purchases))
        unique_products = sorted(set(
            f"{p['product_type']}_{p['product_id']}" for p in purchases
        ))

        user_id_map = {uid: idx for idx, uid in enumerate(unique_users)}
        product_id_map = {pid: idx for idx, pid in enumerate(unique_products)}

        # Build sparse matrix
        rows = []
        cols = []
        data = []

        for purchase in purchases:
            user_idx = user_id_map[purchase["user_id"]]
            product_key = f"{purchase['product_type']}_{purchase['product_id']}"
            product_idx = product_id_map[product_key]
            rows.append(user_idx)
            cols.append(product_idx)
            data.append(purchase["rating"])

        matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(len(unique_users), len(unique_products)),
            dtype=np.float32
        )

        self.user_product_matrix = matrix
        self.user_id_map = user_id_map
        self.product_id_map = {v: k for k, v in product_id_map.items()}
        
        return matrix, user_id_map, product_id_map

    def compute_product_similarity(self):
        """
        Compute product-to-product similarity using cosine similarity.
        
        Returns:
            Product similarity matrix
        """
        if self.user_product_matrix is None:
            return None

        # Compute cosine similarity between products
        # Transpose to get product-to-product similarity
        similarity = cosine_similarity(self.user_product_matrix.T)
        self.product_similarity = similarity

        return similarity

    def get_recommendations(self, user_id, n_recommendations=5, product_type=None):
        """
        Get top N product recommendations for a user.
        
        Args:
            user_id: Customer ID
            n_recommendations: Number of recommendations to return
            product_type: Filter recommendations by product type (optional)
        
        Returns:
            list: List of dicts with product_id, product_type, and score
        """
        # Rebuild matrices if needed
        if self.user_product_matrix is None:
            self.build_user_product_matrix()

        if self.user_product_matrix is None:
            return []  # No data available

        if self.product_similarity is None:
            self.compute_product_similarity()

        # Check if user exists
        if user_id not in self.user_id_map:
            return self._get_trending_products(n_recommendations, product_type)

        user_idx = self.user_id_map[user_id]
        user_ratings = self.user_product_matrix[user_idx].toarray().flatten()

        # Get products user has already rated
        rated_products = np.where(user_ratings > 0)[0]

        if len(rated_products) == 0:
            # User hasn't rated anything, return trending products
            return self._get_trending_products(n_recommendations, product_type)

        # Compute scores for unrated products based on similar products
        recommendation_scores = np.zeros(len(self.product_similarity))

        for rated_idx in rated_products:
            # Get similarity of all products to this rated product
            similarities = self.product_similarity[rated_idx]
            user_rating = user_ratings[rated_idx]

            # Weight the similarity by the user's rating
            recommendation_scores += similarities * user_rating

        # Zero out products already rated
        recommendation_scores[rated_products] = 0

        # Get top recommendations
        top_indices = np.argsort(recommendation_scores)[::-1][:n_recommendations]

        recommendations = []
        for idx in top_indices:
            if recommendation_scores[idx] > 0:
                product_key = self.product_id_map[idx]
                product_type_str, product_id_str = product_key.split("_")
                
                # Filter by product_type if specified
                if product_type and product_type_str != product_type:
                    continue

                recommendations.append({
                    "product_id": int(product_id_str),
                    "product_type": product_type_str,
                    "score": float(recommendation_scores[idx]),
                    "reason": f"Similar to products you liked"
                })

        # If we need more recommendations and have a type filter, remove it
        if len(recommendations) < n_recommendations and product_type:
            recommendations = []
            for idx in top_indices:
                if recommendation_scores[idx] > 0:
                    product_key = self.product_id_map[idx]
                    product_type_str, product_id_str = product_key.split("_")
                    
                    recommendations.append({
                        "product_id": int(product_id_str),
                        "product_type": product_type_str,
                        "score": float(recommendation_scores[idx]),
                        "reason": f"Similar to products you liked"
                    })

        return recommendations[:n_recommendations]

    def _get_trending_products(self, n_recommendations=5, product_type=None):
        """
        Fallback: return highest-rated products (trending).
        Used for new users or when insufficient data.
        """
        trending = UserPurchaseHistory.objects.values(
            "product_id", "product_type"
        ).annotate(
            avg_rating=models.Avg("rating")
        ).filter(
            avg_rating__gt=0
        ).order_by("-avg_rating")

        if product_type:
            trending = trending.filter(product_type=product_type)

        recommendations = []
        for item in trending[:n_recommendations]:
            recommendations.append({
                "product_id": item["product_id"],
                "product_type": item["product_type"],
                "score": float(item["avg_rating"] / 5.0),  # Normalize to 0-1
                "reason": "Trending based on user ratings"
            })

        return recommendations


# Global engine instance
_engine = None


def get_recommendation_engine():
    """Get or create the recommendation engine."""
    global _engine
    if _engine is None:
        _engine = CollaborativeFilteringEngine()
    return _engine


def rebuild_engine():
    """Rebuild the recommendation engine (call after new purchases)."""
    global _engine
    _engine = CollaborativeFilteringEngine()
    _engine.build_user_product_matrix()
    _engine.compute_product_similarity()
    return _engine
