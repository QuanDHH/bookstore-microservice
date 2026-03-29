from django.db import models


class Laptop(models.Model):
    name          = models.CharField(max_length=255)
    brand         = models.CharField(max_length=100)
    cpu           = models.CharField(max_length=100)
    ram           = models.PositiveIntegerField(help_text="RAM in GB")
    price         = models.DecimalField(max_digits=12, decimal_places=2)
    stock         = models.PositiveIntegerField(default=0)
    image         = models.ImageField(upload_to="laptops/", null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "laptops"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.name}"