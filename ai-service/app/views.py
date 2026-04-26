from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .recommendation_engine import RAGChatSystem, model_best, le
from neo4j import GraphDatabase
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

@api_view(['POST'])
def recommend_products(request):
    user_id = request.data.get('user_id')
    context = request.data.get('context', 'search')
    limit = request.data.get('limit', 10)

    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )

    with driver.session() as s:
        result = s.run("""
            MATCH (u:User {user_id:$uid}) -[:PURCHASED|CLICKED] ->(p1)
            <-[:VIEWED] -(u2)-[:VIEWED] ->(p2:Product)
            WHERE NOT (u) -[:VIEWED] ->(p2)
            RETURN p2.product_id as pid, p2.name as name,
                   p2.price as price, p2.category as category,
                   count(*) as score
            ORDER BY score DESC LIMIT $limit
        """, uid=user_id, limit=limit)
        products = [dict(r) for r in result]

    return Response({
        'user_id': user_id,
        'context': context,
        'recommendations': products
    })

@api_view(['POST'])
def chat_with_ai(request):
    user_id = request.data.get('user_id')
    message = request.data.get('message')

    if not user_id or not message:
        return Response({'error': 'user_id and message are required'}, status=status.HTTP_400_BAD_REQUEST)

    rag = RAGChatSystem()
    reply = rag.chat(user_id, message)

    return Response({'reply': reply})

@api_view(['POST'])
def predict_behavior(request):
    user_id = request.data.get('user_id')
    sequence = request.data.get('sequence')  # list of action strings

    if not user_id or not sequence:
        return Response({'error': 'user_id and sequence are required'}, status=status.HTTP_400_BAD_REQUEST)

    if not model_best:
        return Response({'error': 'Model not loaded'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Encode sequence
    encoded_seq = le.transform(sequence)
    padded_seq = pad_sequences([encoded_seq], maxlen=10, padding='pre')

    # Predict
    prediction = model_best.predict(padded_seq)
    predicted_action = le.inverse_transform([np.argmax(prediction)])[0]

    return Response({
        'user_id': user_id,
        'predicted_action': predicted_action,
        'probabilities': prediction.tolist()
    })