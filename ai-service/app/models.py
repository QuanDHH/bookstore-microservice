from django.db import models

# Models for AI Service - using Neo4j primarily, but keeping Django models for compatibility

class User(models.Model):
    user_id = models.CharField(max_length=10, unique=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    segment = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user_id

class Product(models.Model):
    product_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Behavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # view, click, etc.
    timestamp = models.DateTimeField()
    converted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.user_id} - {self.action} - {self.product.name}"