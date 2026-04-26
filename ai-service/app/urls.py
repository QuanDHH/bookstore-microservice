from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_products, name='recommend'),
    path('chat/', views.chat_with_ai, name='chat'),
    path('predict/', views.predict_behavior, name='predict'),
]