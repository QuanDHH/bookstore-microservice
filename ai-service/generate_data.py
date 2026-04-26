import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker("vi_VN")
np.random.seed(42)
random.seed(42)

# Define actions and weights
ACTIONS = ["view","click","add_to_cart","purchase","wishlist","review","share","return"]
ACTION_WEIGHTS = [0.35, 0.25, 0.15, 0.10, 0.07, 0.04, 0.03, 0.01]

# Sample products
PRODUCTS = [
    {"id":"P0023","name":"Laptop Dell XPS 15","cat":"Electronics","price":28990000},
    {"id":"P0045","name":"Dien thoai Samsung S24","cat":"Electronics","price":5500000},
    {"id":"P0067","name":"Tai nghe Sony WH-1000XM5","cat":"Electronics","price":800000},
    {"id":"P0089","name":"Giay the thao Nike Air Max","cat":"Fashion","price":650000},
    {"id":"P0101","name":"Do gia dung Kangaroo","cat":"Home","price":320000},
]

# Generate data for 500 users
rows = []
start_date = datetime(2024, 1, 1)
for i in range(1, 501):
    user_id = f"U{i:03d}"
    n_behaviors = random.randint(15, 30)
    for _ in range(n_behaviors):
        product = random.choice(PRODUCTS)
        action = random.choices(ACTIONS, weights=ACTION_WEIGHTS)[0]
        ts = start_date + timedelta(days=random.randint(0,89),
                                   hours=random.randint(0,23),
                                   minutes=random.randint(0,59))
        converted = 1 if action in ["purchase","add_to_cart","review"] else 0
        rows.append({"user_id":user_id,"product_id":product["id"],
                     "action":action,"timestamp":ts,
                     "product_name":product["name"],
                     "category":product["cat"],"price":product["price"],
                     "converted":converted})

df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
df.to_csv("data_user500.csv", index=False)
print(f"Generated {len(df)} records for {df.user_id.nunique()} users.")