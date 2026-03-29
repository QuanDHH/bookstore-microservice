from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    AddItemSerializer,
    RemoveItemSerializer,
)


class CreateCartView(APIView):
    """
    Called internally by customer-service after registration.
    POST /api/carts/create/   { "customer_id": <id> }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        customer_id = request.data.get("customer_id")
        if not customer_id:
            return Response(
                {"detail": "customer_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CartView(APIView):
    """
    GET /api/carts/<customer_id>/   — view the cart
    """
    permission_classes = [AllowAny]

    def get_cart(self, customer_id):
        try:
            return Cart.objects.prefetch_related("items").get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return None

    def get(self, request, customer_id):
        cart = self.get_cart(customer_id)
        if not cart:
            return Response(
                {"detail": "Cart not found for this customer."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CartSerializer(cart).data)


class AddItemView(APIView):
    """
    POST /api/carts/<customer_id>/add/
    {
        "product_id": 1,
        "product_name": "Dell XPS 15",
        "quantity": 2,
        "price": "1500.00"
    }
    If the product already exists in the cart, quantity is incremented.
    """
    permission_classes = [AllowAny]

    def post(self, request, customer_id):
        # Ensure cart exists
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            return Response(
                {"detail": "Cart not found for this customer."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AddItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=data["product_id"],
            defaults={
                "product_name": data["product_name"],
                "quantity":     data["quantity"],
                "price":        data["price"],
            },
        )

        if not created:
            # Product already in cart — increment quantity
            item.quantity += data["quantity"]
            item.save()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK,
        )


class RemoveItemView(APIView):
    """
    DELETE /api/carts/<customer_id>/remove/
    { "product_id": 1 }
    """
    permission_classes = [AllowAny]

    def delete(self, request, customer_id):
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            return Response(
                {"detail": "Cart not found for this customer."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RemoveItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data["product_id"]
        deleted, _ = CartItem.objects.filter(
            cart=cart, product_id=product_id
        ).delete()

        if not deleted:
            return Response(
                {"detail": "Product not found in cart."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)