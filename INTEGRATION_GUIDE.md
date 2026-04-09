# Integration Guide: Recommendation Service

This guide explains how to integrate the Recommendation Service with your existing microservices.

## Overview

The Recommendation Service should be called at key points in your application:

1. **After Purchase**: Record the purchase and product type
2. **Product Rating**: Record user ratings after purchase
3. **Product Recommendation**: Display recommendations to users

## Integration Points

### 1. From Product Services (Laptop, Clothes, Mobile)

After a user successfully purchases a product, notify the recommendation service:

```python
# In laptop-service/app/views.py or similar
import requests
import os

def record_purchase_to_recommendation(user_id, product_id, product_info):
    """Record purchase in recommendation service"""
    recommendation_service_url = os.getenv(
        'RECOMMENDATION_SERVICE_URL',
        'http://recommendation-service:8007'
    )
    
    payload = {
        'user_id': user_id,
        'product_id': product_id,
        'product_type': 'laptop',  # Change per service
        'purchase_price': float(product_info.price)
    }
    
    try:
        response = requests.post(
            f'{recommendation_service_url}/api/recommendations/purchase/',
            json=payload,
            timeout=5
        )
        if response.status_code == 201:
            print(f"Purchase recorded: User {user_id}, Product {product_id}")
        else:
            print(f"Failed to record purchase: {response.status_code}")
    except Exception as e:
        # Don't fail the purchase if recommendation service is down
        print(f"Warning: Could not record purchase: {e}")

# Call this after successful purchase
# record_purchase_to_recommendation(user_id, laptop_id, laptop_object)
```

### 2. From Cart Service

When order is confirmed:

```python
# In cart-service/app/views.py
def checkout(request):
    """Checkout process"""
    cart = get_user_cart(request.user.id)
    
    for item in cart.items:
        # Process payment, create order, etc.
        
        # Then record in recommendation service
        record_purchase_to_recommendation(
            user_id=request.user.id,
            product_id=item.product.id,
            product_info=item.product
        )
    
    # Clear cart
    cart.clear()
    return Response({"status": "Order placed successfully"})
```

### 3. Frontend: Display Recommendations

In your React/Vue components:

```javascript
// src/api/recommendations.js
const API_BASE = "http://api-gateway:8000";

export async function getProductRecommendations(userId, count = 5, type = null) {
    let url = `${API_BASE}/api/recommendations/recommendations/${userId}/?count=${count}`;
    if (type) {
        url += `&type=${type}`;
    }
    
    const response = await fetch(url);
    return response.json();
}

export async function recordPurchase(userId, productId, productType, price) {
    const response = await fetch(
        `${API_BASE}/api/recommendations/purchase/`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                product_type: productType,
                purchase_price: price
            })
        }
    );
    return response.json();
}

export async function rateProduct(userId, productId, productType, rating) {
    const response = await fetch(
        `${API_BASE}/api/recommendations/rate/`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                product_type: productType,
                rating: rating
            })
        }
    );
    return response.json();
}
```

```jsx
// src/pages/ProductDetail.jsx
import { getProductRecommendations } from '../api/recommendations';

export default function ProductDetail() {
    const [recommendations, setRecommendations] = useState([]);
    const userId = getUserIdFromContext(); // Your auth logic

    useEffect(() => {
        getProductRecommendations(userId, 5)
            .then(data => setRecommendations(data.recommendations))
            .catch(err => console.error(err));
    }, [userId]);

    return (
        <div>
            <h2>Recommended For You</h2>
            <div className="recommendations">
                {recommendations.map(rec => (
                    <ProductCard
                        key={`${rec.product_type}-${rec.product_id}`}
                        productId={rec.product_id}
                        productType={rec.product_type}
                        score={rec.score}
                        reason={rec.reason}
                    />
                ))}
            </div>
        </div>
    );
}
```

### 4. Customer Service: User Dashboard

Show user's purchase history and get recommendations:

```javascript
// Get user purchase history
async function getPurchaseHistory(customerId) {
    const response = await fetch(
        `http://api-gateway:8000/api/recommendations/history/${customerId}/`
    );
    return response.json();
}

// Display in dashboard
export function CustomerDashboard() {
    const [history, setHistory] = useState(null);
    const customerId = getCustomerId();

    useEffect(() => {
        getPurchaseHistory(customerId)
            .then(data => setHistory(data.purchases))
            .catch(err => console.error(err));
    }, [customerId]);

    return (
        <div>
            <h3>My Purchases</h3>
            {history?.map(purchase => (
                <div key={purchase.id}>
                    <p>{purchase.product_type} #{purchase.product_id}</p>
                    <Rating 
                        value={purchase.rating}
                        onRate={(value) => submitRating(purchase, value)}
                    />
                </div>
            ))}
        </div>
    );
}
```

## API Gateway Routing

All recommendation endpoints are accessible through the API Gateway:

```
POST   /api/recommendations/purchase/       → Record purchase
POST   /api/recommendations/rate/          → Rate product
GET    /api/recommendations/recommendations/<user_id>/  → Get recommendations
GET    /api/recommendations/history/<user_id>/          → View purchase history
GET    /api/recommendations/health/        → Health check
```

## Example Flow: Product Purchase to Recommendation

### 1. User buys a laptop on laptop-service

```
laptop-service/api/laptops/123/buy/
│
├─ Process payment
├─ Create order
├─ POST /api/recommendations/purchase/
│   {
│     "user_id": 456,
│     "product_id": 123,
│     "product_type": "laptop",
│     "purchase_price": 999.99
│   }
│
└─ Return confirmation
```

### 2. User rates the laptop later

```
frontend (Product Rating Component)
│
├─ User submits rating: 5 stars
├─ POST /api/recommendations/rate/
│   {
│     "user_id": 456,
│     "product_id": 123,
│     "product_type": "laptop",
│     "rating": 5
│   }
│
└─ Cache invalidated, engine rebuilt
```

### 3. User views product page, sees recommendations

```
frontend (Product Detail Page)
│
├─ GET /api/recommendations/recommendations/456/?count=5&type=laptop
│
├─ Response:
│   {
│     "user_id": 456,
│     "recommendations": [
│       {
│         "product_id": 789,
│         "product_type": "laptop",
│         "score": 0.85
│       },
│       ...
│     ]
│   }
│
└─ Display recommended laptops
```

## Testing the Integration

### Manual Testing with cURL

```bash
# 1. Record a purchase
curl -X POST http://api-gateway:8000/api/recommendations/purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "product_id": 456,
    "product_type": "laptop",
    "purchase_price": 999.99
  }'

# 2. Rate the product
curl -X POST http://api-gateway:8000/api/recommendations/rate/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "product_id": 456,
    "product_type": "laptop",
    "rating": 5
  }'

# 3. Get recommendations
curl http://api-gateway:8000/api/recommendations/recommendations/123/?count=5

# 4. View purchase history
curl http://api-gateway:8000/api/recommendations/history/123/
```

### Python Testing Script

```python
import requests
import json

BASE_URL = "http://api-gateway:8000/api/recommendations"

def test_recommendation_flow():
    # Test data
    user_id = 123
    laptops = [1, 2, 3, 4]  # Laptop product IDs
    
    # 1. Record purchases
    for product_id in laptops:
        response = requests.post(
            f"{BASE_URL}/purchase/",
            json={
                "user_id": user_id,
                "product_id": product_id,
                "product_type": "laptop",
                "purchase_price": 1000.0 - (product_id * 100)
            }
        )
        assert response.status_code == 201
        print(f"✓ Recorded purchase for product {product_id}")
    
    # 2. Rate products
    for product_id, rating in enumerate(laptops, start=3):
        response = requests.post(
            f"{BASE_URL}/rate/",
            json={
                "user_id": user_id,
                "product_id": product_id,
                "product_type": "laptop",
                "rating": rating
            }
        )
        assert response.status_code == 200
        print(f"✓ Rated product {product_id} with {rating} stars")
    
    # 3. Get recommendations
    response = requests.get(
        f"{BASE_URL}/recommendations/{user_id}/?count=5&type=laptop"
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Got {data['count']} recommendations")
    for rec in data['recommendations']:
        print(f"  - Product {rec['product_id']} (score: {rec['score']:.2f})")
    
    # 4. View history
    response = requests.get(f"{BASE_URL}/history/{user_id}/")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ User purchase history: {data['count']} items")

if __name__ == "__main__":
    test_recommendation_flow()
    print("\n✓ All tests passed!")
```

## Best Practices

1. **Make purchase recording async**: Don't wait for recommendation service response
   ```python
   # Use Celery or similar for async tasks
   from celery import shared_task
   
   @shared_task
   def record_purchase_async(user_id, product_id, product_type, price):
       record_purchase_to_recommendation(user_id, product_id, product_type, price)
   ```

2. **Cache recommendations on frontend**: Don't fetch every page load
   ```javascript
   const cache = new Map();
   
   export async function getRecommendations(userId) {
       if (cache.has(userId)) {
           return cache.get(userId);
       }
       const data = await fetch(...);
       cache.set(userId, data);
       return data;
   }
   ```

3. **Handle service unavailability gracefully**:
   ```python
   try:
       record_purchase_to_recommendation(...)
   except Exception:
       # Log but don't fail - recommendation is non-critical
       logger.warning("Failed to record purchase for recommendation")
   ```

4. **Use product_type consistently**:
   - "laptop" from laptop-service
   - "clothes" from clothes-service
   - "mobile" from mobile-service

## Docker Compose Update

The recommendation service has been added to docker-compose.yml with:

```yaml
recommendation-db: PostgreSQL database
recommendation-service: Django service (port 8007)
api-gateway: Updated to include RECOMMENDATION_SERVICE_URL
```

To start all services:
```bash
docker-compose up -d
```

To check recommendation service logs:
```bash
docker-compose logs -f recommendation-service
```
