from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Clothes
from .serializers import ClothesSerializer, ClothesListSerializer


class ClothesListCreateView(APIView):
    """
    GET  /api/clothes/       — list all clothes (with optional filters)
    POST /api/clothes/       — create a new clothes item

    Query params:
      ?search=<keyword>      — matches name or brand (case-insensitive)
      ?category=<value>      — shirt | pants | dress | jacket | shoes | hat | other
      ?min_price=<value>
      ?max_price=<value>
    """
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = Clothes.objects.all()

        # -- keyword search on name or brand
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(brand__icontains=search)

        # -- category filter
        category = request.query_params.get("category")
        if category:
            qs = qs.filter(category__iexact=category)

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

        serializer = ClothesListSerializer(qs, many=True, context={"request": request})
        return Response({"count": qs.count(), "results": serializer.data})

    def post(self, request):
        serializer = ClothesSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClothesDetailView(APIView):
    """
    GET    /api/clothes/<id>/  — retrieve
    PUT    /api/clothes/<id>/  — full update
    PATCH  /api/clothes/<id>/  — partial update
    DELETE /api/clothes/<id>/  — delete
    """
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Clothes.objects.get(pk=pk)
        except Clothes.DoesNotExist:
            return None

    def get(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"detail": "Clothes item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            ClothesSerializer(clothes, context={"request": request}).data
        )

    def put(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"detail": "Clothes item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ClothesSerializer(
            clothes, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"detail": "Clothes item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ClothesSerializer(
            clothes, data=request.data, partial=True, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response(
                {"detail": "Clothes item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        clothes.delete()
        return Response(
            {"detail": "Clothes item deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )