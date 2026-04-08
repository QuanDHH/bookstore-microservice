from django.db import models


class Mobile(models.Model):
    name       = models.CharField(max_length=255)
    brand      = models.CharField(max_length=100)
    ram        = models.PositiveIntegerField(help_text="RAM in GB")
    storage    = models.PositiveIntegerField(help_text="Storage in GB")
    battery    = models.PositiveIntegerField(help_text="Battery in mAh")
    price      = models.DecimalField(max_digits=12, decimal_places=2)
    stock      = models.PositiveIntegerField(default=0)
    image      = models.ImageField(upload_to="mobiles/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mobiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.name}"