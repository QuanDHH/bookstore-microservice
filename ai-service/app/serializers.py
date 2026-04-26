from rest_framework import serializers
from .models import User, Product, Behavior

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class BehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Behavior
        fields = '__all__'