"""
tests.py - Recommendation Service Tests

Run with: python manage.py test
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json

from .models import UserPurchaseHistory, RecommendationCache
from .recommendation_engine import CollaborativeFilteringEngine


class UserPurchaseHistoryModelTest(TestCase):
    """Test UserPurchaseHistory model"""

    def setUp(self):
        self.purchase = UserPurchaseHistory.objects.create(
            user_id=1,
            product_id=100,
            product_type="laptop",
            purchase_price=999.99,
            rating=5
        )

    def test_create_purchase(self):
        """Test creating a purchase record"""
        self.assertEqual(self.purchase.user_id, 1)
        self.assertEqual(self.purchase.product_id, 100)
        self.assertEqual(self.purchase.product_type, "laptop")
        self.assertEqual(self.purchase.rating, 5)

    def test_unique_constraint(self):
        """Test unique constraint (user_id, product_id, product_type)"""
        with self.assertRaises(Exception):
            UserPurchaseHistory.objects.create(
                user_id=1,
                product_id=100,
                product_type="laptop",
                purchase_price=1000.00,
                rating=4
            )

    def test_string_representation(self):
        """Test __str__ method"""
        self.assertIn("User 1", str(self.purchase))
        self.assertIn("laptop", str(self.purchase))


class RecordPurchaseAPITest(TestCase):
    """Test record purchase endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = "/api/recommendations/purchase/"

    def test_record_purchase_success(self):
        """Test successful purchase recording"""
        data = {
            "user_id": 1,
            "product_id": 100,
            "product_type": "laptop",
            "purchase_price": 999.99
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify data was saved
        purchase = UserPurchaseHistory.objects.get(user_id=1, product_id=100)
        self.assertEqual(purchase.product_type, "laptop")
        self.assertEqual(float(purchase.purchase_price), 999.99)

    def test_record_purchase_missing_fields(self):
        """Test with missing required fields"""
        data = {
            "user_id": 1,
            "product_id": 100
            # Missing product_type and purchase_price
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_record_purchase_invalid_type(self):
        """Test with invalid product type"""
        data = {
            "user_id": 1,
            "product_id": 100,
            "product_type": "invalid_type",
            "purchase_price": 999.99
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_record_purchase_update(self):
        """Test updating existing purchase"""
        # Create initial purchase
        UserPurchaseHistory.objects.create(
            user_id=1,
            product_id=100,
            product_type="laptop",
            purchase_price=999.99,
            rating=0
        )
        
        # Record same purchase with different price
        data = {
            "user_id": 1,
            "product_id": 100,
            "product_type": "laptop",
            "purchase_price": 899.99
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify price was updated
        purchase = UserPurchaseHistory.objects.get(user_id=1, product_id=100)
        self.assertEqual(float(purchase.purchase_price), 899.99)


class RateProductAPITest(TestCase):
    """Test product rating endpoint"""

    def setUp(self):
        self.client = Client()
        self.url = "/api/recommendations/rate/"
        
        # Create a purchase first
        self.purchase = UserPurchaseHistory.objects.create(
            user_id=1,
            product_id=100,
            product_type="laptop",
            purchase_price=999.99,
            rating=0
        )

    def test_rate_product_success(self):
        """Test successful product rating"""
        data = {
            "user_id": 1,
            "product_id": 100,
            "product_type": "laptop",
            "rating": 5
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify rating was saved
        purchase = UserPurchaseHistory.objects.get(user_id=1, product_id=100)
        self.assertEqual(purchase.rating, 5)

    def test_rate_product_invalid_rating(self):
        """Test with invalid rating value"""
        data = {
            "user_id": 1,
            "product_id": 100,
            "product_type": "laptop",
            "rating": 10  # Invalid: only 1-5 allowed
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_nonexistent_purchase(self):
        """Test rating a product that wasn't purchased"""
        data = {
            "user_id": 1,
            "product_id": 999,  # Doesn't exist
            "product_type": "laptop",
            "rating": 5
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetRecommendationsAPITest(TestCase):
    """Test recommendations endpoint"""

    def setUp(self):
        self.client = Client()
        
        # Create sample purchase history
        UserPurchaseHistory.objects.create(
            user_id=1, product_id=100, product_type="laptop",
            purchase_price=999.99, rating=5
        )
        UserPurchaseHistory.objects.create(
            user_id=1, product_id=101, product_type="laptop",
            purchase_price=899.99, rating=4
        )
        UserPurchaseHistory.objects.create(
            user_id=2, product_id=100, product_type="laptop",
            purchase_price=999.99, rating=5
        )
        UserPurchaseHistory.objects.create(
            user_id=2, product_id=102, product_type="laptop",
            purchase_price=1199.99, rating=5
        )

    def test_get_recommendations_success(self):
        """Test getting recommendations"""
        url = "/api/recommendations/recommendations/1/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data["user_id"], 1)
        self.assertIn("recommendations", data)
        self.assertIn("count", data)
        self.assertIn("generated_at", data)

    def test_get_recommendations_with_count(self):
        """Test recommendations with custom count"""
        url = "/api/recommendations/recommendations/1/?count=10"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertLessEqual(data["count"], 10)

    def test_get_recommendations_with_type_filter(self):
        """Test recommendations filtered by product type"""
        url = "/api/recommendations/recommendations/1/?type=laptop"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        for rec in data["recommendations"]:
            self.assertEqual(rec["product_type"], "laptop")

    def test_get_recommendations_invalid_user_id(self):
        """Test with invalid user ID format"""
        url = "/api/recommendations/recommendations/invalid/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_recommendations_new_user(self):
        """Test getting recommendations for new user"""
        url = "/api/recommendations/recommendations/999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # New users should get trending products (empty list is ok too)
        data = response.json()
        self.assertEqual(data["user_id"], 999)
        self.assertIsInstance(data["recommendations"], list)


class PurchaseHistoryAPITest(TestCase):
    """Test purchase history endpoint"""

    def setUp(self):
        self.client = Client()
        
        UserPurchaseHistory.objects.create(
            user_id=1, product_id=100, product_type="laptop",
            purchase_price=999.99, rating=5
        )
        UserPurchaseHistory.objects.create(
            user_id=1, product_id=200, product_type="clothes",
            purchase_price=99.99, rating=4
        )

    def test_get_purchase_history_success(self):
        """Test retrieving purchase history"""
        url = "/api/recommendations/history/1/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data["user_id"], 1)
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["purchases"]), 2)

    def test_get_purchase_history_nonexistent_user(self):
        """Test retrieving history for user with no purchases"""
        url = "/api/recommendations/history/999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_purchase_history_invalid_user_id(self):
        """Test with invalid user ID format"""
        url = "/api/recommendations/history/invalid/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CollaborativeFilteringEngineTest(TestCase):
    """Test the collaborative filtering engine"""

    def setUp(self):
        # Create sample data
        UserPurchaseHistory.objects.create(
            user_id=1, product_id=1, product_type="laptop",
            purchase_price=1000, rating=5
        )
        UserPurchaseHistory.objects.create(
            user_id=1, product_id=2, product_type="laptop",
            purchase_price=800, rating=3
        )
        UserPurchaseHistory.objects.create(
            user_id=2, product_id=1, product_type="laptop",
            purchase_price=1000, rating=5
        )
        UserPurchaseHistory.objects.create(
            user_id=2, product_id=3, product_type="laptop",
            purchase_price=1200, rating=5
        )

    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = CollaborativeFilteringEngine()
        self.assertIsNotNone(engine)

    def test_build_matrix(self):
        """Test building user-product matrix"""
        engine = CollaborativeFilteringEngine()
        matrix, user_map, product_map = engine.build_user_product_matrix()
        
        self.assertIsNotNone(matrix)
        self.assertGreater(len(user_map), 0)
        self.assertGreater(len(product_map), 0)

    def test_compute_similarity(self):
        """Test product similarity computation"""
        engine = CollaborativeFilteringEngine()
        engine.build_user_product_matrix()
        similarity = engine.compute_product_similarity()
        
        self.assertIsNotNone(similarity)

    def test_get_recommendations(self):
        """Test recommendation generation"""
        engine = CollaborativeFilteringEngine()
        engine.build_user_product_matrix()
        engine.compute_product_similarity()
        
        recommendations = engine.get_recommendations(user_id=1, n_recommendations=5)
        self.assertIsInstance(recommendations, list)


class HealthCheckTest(TestCase):
    """Test health check endpoint"""

    def setUp(self):
        self.client = Client()

    def test_health_check(self):
        """Test service health check"""
        url = "/api/recommendations/health/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "recommendation-service")
