import os
import json
from neo4j import GraphDatabase
from anthropic import Anthropic
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from django.conf import settings

class KBGraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE")

    def load_data(self, csv_path):
        df = pd.read_csv(csv_path)
        with self.driver.session() as session:
            for _, row in df.iterrows():
                # Create User node
                session.run("""
                    MERGE (u:User {user_id: $uid})
                """, uid=row["user_id"])
                # Create Product node
                session.run("""
                    MERGE (p:Product {product_id: $pid})
                    SET p.name = $name, p.category = $cat, p.price = $price
                """, pid=row["product_id"], name=row["product_name"],
                    cat=row["category"], price=row["price"])
                # Create relationship
                action = row["action"].upper()
                session.run(f"""
                    MATCH (u:User {{user_id: $uid}})
                    MATCH (p:Product {{product_id: $pid}})
                    MERGE (u)-[:{action} {{timestamp: $ts}}]->(p)
                """, uid=row["user_id"], pid=row["product_id"],
                    ts=str(row["timestamp"]))

class RAGChatSystem:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        self.claude = Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.embed_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection("kb_graph")
        self.chat_history = []

    def retrieve_from_graph(self, user_id: str, query: str) -> str:
        with self.driver.session() as s:
            # History
            result = s.run("""
                MATCH (u:User {user_id: $uid}) -[r]->(p:Product)
                RETURN type(r) as action, p.name as product,
                       p.price as price, p.category as category
                ORDER BY r.timestamp DESC LIMIT 10
            """, uid=user_id)
            history = [dict(r) for r in result]
            # Recommendations
            result2 = s.run("""
                MATCH (u:User {user_id: $uid}) -[:PURCHASED] ->(p1)
                      <-[:PURCHASED] -(u2)-[:VIEWED] ->(p2:Product)
                WHERE NOT (u) -[:VIEWED] ->(p2)
                RETURN p2.name as recommended, p2.price as price
                LIMIT 5
            """, uid=user_id)
            recommendations = [dict(r) for r in result2]
        context = f"Lich su hành vi: {json.dumps(history, ensure_ascii=False)} \n"
        context += f"Goi y: {json.dumps(recommendations, ensure_ascii=False)}"
        return context

    def chat(self, user_id: str, user_message: str) -> str:
        context = self.retrieve_from_graph(user_id, user_message)
        system_prompt = f"""
        Ban la tro ly mua sắm AI thông minh của ShopAI.
        Su dung thong tin sau de tra loi người dùng:
        {context}
        Tra loi bang tieng Viet, than thien va chính xác.
        """
        self.chat_history.append({"role": "user", "content": user_message})
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=512,
            system=system_prompt,
            messages=self.chat_history
        )
        answer = response.content[0].text
        self.chat_history.append({"role": "assistant", "content": answer})
        return answer

# Load BiLSTM model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model_best.h5')
if os.path.exists(MODEL_PATH):
    model_best = load_model(MODEL_PATH)
else:
    model_best = None

# Label encoder for actions
ACTIONS = ["view", "click", "add_to_cart", "purchase", "wishlist", "review", "share", "return"]
le = LabelEncoder()
le.fit(ACTIONS)