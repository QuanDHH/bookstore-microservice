# Recommendation Service

A collaborative filtering-based recommendation engine that suggests products to users based on their purchase history and ratings.

## Features

- **Collaborative Filtering**: Uses item-based collaborative filtering with scikit-learn to find similar products
- **Purchase Tracking**: Records user purchases across all product types (laptop, clothes, mobile)
- **Rating System**: Users can rate products (1-5 stars) to improve recommendations
- **Recommendation Caching**: Caches recommendations for 24 hours to improve performance
- **Trending Fallback**: Returns trending products for new users with insufficient history

## Architecture

- **Framework**: Django + Django REST Framework
- **ML Library**: Scikit-learn (cosine similarity)
- **Database**: PostgreSQL
- **Service Port**: 8007

## API Endpoints

### 1. Health Check
```
GET /api/recommendations/health/
```
Simple health check to verify the service is running.

**Response**:
```json
{
    "status": "ok",
    "service": "recommendation-service"
}
```

### 2. Record Purchase
```
POST /api/recommendations/purchase/
```
Record a user's product purchase.

**Request Body**:
```json
{
    "user_id": 123,
    "product_id": 456,
    "product_type": "laptop",
    "purchase_price": 999.99
}
```

**Parameters**:
- `user_id` (integer): Customer ID
- `product_id` (integer): Product ID
- `product_type` (string): One of `"laptop"`, `"clothes"`, `"mobile"`
- `purchase_price` (number): Purchase price

### 3. Rate Product
```
POST /api/recommendations/rate/
```
Submit a rating for a purchased product.

**Request Body**:
```json
{
    "user_id": 123,
    "product_id": 456,
    "product_type": "laptop",
    "rating": 5
}
```

**Parameters**:
- `user_id` (integer): Customer ID
- `product_id` (integer): Product ID
- `product_type` (string): One of `"laptop"`, `"clothes"`, `"mobile"`
- `rating` (integer): Rating from 1 to 5

### 4. Get Recommendations
```
GET /api/recommendations/recommendations/<user_id>/
```
Get product recommendations for a specific user.

**Query Parameters**:
- `count` (optional, default=5): Number of recommendations (max 50)
- `type` (optional): Filter by product type (`"laptop"`, `"clothes"`, or `"mobile"`)

**Response**:
```json
{
    "user_id": 123,
    "recommendations": [
        {
            "product_id": 789,
            "product_type": "laptop",
            "score": 0.85,
            "reason": "Similar to products you liked"
        },
        {
            "product_id": 790,
            "product_type": "laptop",
            "score": 0.72,
            "reason": "Similar to products you liked"
        }
    ],
    "count": 2,
    "generated_at": "2024-04-09T10:30:00Z"
}
```

**Response Fields**:
- `product_id`: The recommended product's ID
- `product_type`: The type of product
- `score`: Recommendation score (0-1, confidence level)
- `reason`: Why the product was recommended

### 5. Purchase History
```
GET /api/recommendations/history/<user_id>/
```
Get a user's complete purchase and rating history.

**Response**:
```json
{
    "user_id": 123,
    "purchases": [
        {
            "id": 1,
            "user_id": 123,
            "product_id": 456,
            "product_type": "laptop",
            "purchase_price": "999.99",
            "rating": 5,
            "purchased_at": "2024-04-01T10:00:00Z",
            "updated_at": "2024-04-05T15:30:00Z"
        }
    ],
    "count": 1
}
```

## How Recommendations Work

### Collaborative Filtering Algorithm

1. **Build User-Product Matrix**: Creates a matrix where rows are users and columns are products, filled with ratings

2. **Compute Similarity**: Calculates cosine similarity between all products based on user ratings

3. **Generate Recommendations**:
   - For a given user, finds products they haven't rated
   - For each unrated product, calculates a recommendation score by:
     - Finding products the user has rated
     - Finding similar products using cosine similarity
     - Weighting by the user's rating for similar products
   - Returns top N products by score

### Example Scenario

If User A rated Laptop X as 5 stars and Laptop Y as 2 stars, and multiple users show Laptop X and Laptop Z are similar:
- The system will recommend Laptop Z to User A with a high score
- If User A hasn't rated Laptop Z yet, it becomes a candidate for recommendation

## Integration with Other Services

### From Product Services (Laptop, Clothes, Mobile)

When a user purchases a product:
```javascript
// Call the recommendation service to record the purchase
POST /api/recommendations/purchase/
{
    "user_id": user_id,
    "product_id": product_id,
    "product_type": "laptop",  // Change based on service
    "purchase_price": product_price
}
```

### From Cart Service

When a purchase is confirmed:
```javascript
// Record the purchase in recommendation service
POST /api/recommendations/purchase/
```

Then later, when displaying recommendations to the user:
```javascript
// Get recommendations from gateway
GET /api/recommendations/recommendations/{user_id}/
```

## Configuration

Environment variables (set in docker-compose.yml):

```yaml
DB_ENGINE: django.db.backends.postgresql
DB_NAME: recommendation_db
DB_USER: recommendation_user
DB_PASSWORD: recommendation_pass
DB_HOST: recommendation-db
DB_PORT: 5432
SECRET_KEY: your-secret-key
DEBUG: "false"  # Set to "true" for development
```

## Development

### Local Setup

```bash
# Navigate to the service
cd recommendation-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export DB_HOST=localhost
export DB_NAME=recommendation_db
export DB_USER=recommendation_user
export DB_PASSWORD=recommendation_pass

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver 8007
```

### Admin Interface

Access the Django admin at `/admin/` to:
- View and manage purchase history
- Monitor recommendation cache
- Manage user data

## Database Models

### UserPurchaseHistory
Tracks user purchases and ratings:
- `user_id`: Customer ID
- `product_id`: Product ID
- `product_type`: Type of product (laptop, clothes, mobile)
- `purchase_price`: Price at purchase time
- `rating`: User rating (1-5, 0 if not rated)
- `purchased_at`: Purchase timestamp
- `updated_at`: Last update timestamp

Indexes on:
- `user_id`
- `product_id`
- `product_type`

Unique constraint: `(user_id, product_id, product_type)` - one rating per user per product

### RecommendationCache
Caches computed recommendations:
- `user_id`: User ID (unique)
- `recommendations`: JSON array of recommendations
- `cached_at`: Cache creation time
- `expires_at`: Cache expiration time (24 hours)

## Performance Considerations

1. **Caching**: Recommendations are cached for 24 hours to avoid recomputation
2. **Sparse Matrix**: Uses scipy sparse matrices for memory efficiency
3. **Cosine Similarity**: Fast computation using sklearn's implementation
4. **Lazy Engine Building**: The recommendation engine is built on-demand and rebuilt only after new ratings

## Troubleshooting

### No recommendations returned for new users
- Expected behavior: New users without rating history get trending products
- Solution: Encourage user to rate products to get personalized recommendations

### Recommendations not updating
- Check if cache has expired (24 hours)
- Verify that ratings are being submitted properly
- Monitor recommendation-db for data

### Service unreachable
- Check docker-compose logs: `docker-compose logs recommendation-service`
- Verify database connection in PostgreSQL
- Check environment variables are correctly set

## Future Enhancements

- [ ] User-based collaborative filtering (in addition to item-based)
- [ ] Content-based filtering using product attributes
- [ ] Hybrid recommendation approach
- [ ] A/B testing framework
- [ ] Real-time recommendation updates
- [ ] Product type cross-recommendations
- [ ] Recommendation diversity
- [ ] Cold-start problem mitigation
