from django.db import models


class Category(models.TextChoices):
    SHIRT    = "shirt",    "Shirt"
    PANTS    = "pants",    "Pants"
    DRESS    = "dress",    "Dress"
    JACKET   = "jacket",  "Jacket"
    SHOES    = "shoes",    "Shoes"
    HAT      = "hat",      "Hat"
    OTHER    = "other",    "Other"


class Size(models.TextChoices):
    XS  = "XS",  "XS"
    S   = "S",   "S"
    M   = "M",   "M"
    L   = "L",   "L"
    XL  = "XL",  "XL"
    XXL = "XXL", "XXL"


class Clothes(models.Model):
    name       = models.CharField(max_length=255)
    brand      = models.CharField(max_length=100)
    category   = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    size       = models.CharField(max_length=5, choices=Size.choices)
    price      = models.DecimalField(max_digits=12, decimal_places=2)
    stock      = models.PositiveIntegerField(default=0)
    image      = models.ImageField(upload_to="clothes/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clothes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.name} ({self.size})"