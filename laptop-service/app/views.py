from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Laptop
from .serializers import LaptopSerializer, LaptopListSerializer


class LaptopListCreateView(APIView):
    """
    GET  /api/laptops/          — list all laptops (with optional filters)
    POST /api/laptops/          — create a new laptop

    Query params for filtering:
      ?search=<keyword>         — matches name or brand (case-insensitive)
      ?min_price=<value>
      ?max_price=<value>
    """
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = Laptop.objects.all()

        # -- keyword search on name or brand
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(brand__icontains=search)

        # -- price range filter
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        if min_price:
            try:
                qs = qs.filter(price__gte=float(min_price))
            except ValueError:
                return Response(
                    {"detail": "min_price must be a number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                return Response(
                    {"detail": "max_price must be a number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = LaptopListSerializer(qs, many=True, context={"request": request})
        return Response({"count": qs.count(), "results": serializer.data})

    def post(self, request):
        serializer = LaptopSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LaptopDetailView(APIView):
    """
    GET    /api/laptops/<id>/   — retrieve
    PUT    /api/laptops/<id>/   — full update
    PATCH  /api/laptops/<id>/   — partial update
    DELETE /api/laptops/<id>/   — delete
    """
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Laptop.objects.get(pk=pk)
        except Laptop.DoesNotExist:
            return None

    def get(self, request, pk):
        laptop = self.get_object(pk)
        if not laptop:
            return Response(
                {"detail": "Laptop not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LaptopSerializer(laptop, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        laptop = self.get_object(pk)
        if not laptop:
            return Response(
                {"detail": "Laptop not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LaptopSerializer(
            laptop, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        laptop = self.get_object(pk)
        if not laptop:
            return Response(
                {"detail": "Laptop not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LaptopSerializer(
            laptop, data=request.data, partial=True, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        laptop = self.get_object(pk)
        if not laptop:
            return Response(
                {"detail": "Laptop not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        laptop.delete()
        return Response(
            {"detail": "Laptop deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )