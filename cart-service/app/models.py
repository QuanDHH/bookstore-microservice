from django.db import models


class Cart(models.Model):
    customer_id = models.IntegerField(unique=True)  # FK to customer-service
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart(customer_id={self.customer_id})"

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart         = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product_id   = models.IntegerField()
    product_name = models.CharField(max_length=255)
    quantity     = models.PositiveIntegerField(default=1)
    price        = models.DecimalField(max_digits=12, decimal_places=2)
    added_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        # prevent duplicate products in the same cart
        unique_together = ("cart", "product_id")

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity