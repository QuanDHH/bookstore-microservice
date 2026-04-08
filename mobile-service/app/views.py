from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Mobile
from .serializers import MobileSerializer, MobileListSerializer


class MobileListCreateView(APIView):
    """
    GET  /api/mobiles/      — list all mobiles (with optional filters)
    POST /api/mobiles/      — create a new mobile

    Query params:
      ?search=<keyword>     — matches name or brand (case-insensitive)
      ?min_price=<value>
      ?max_price=<value>
    """
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = Mobile.objects.all()

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

        serializer = MobileListSerializer(qs, many=True, context={"request": request})
        return Response({"count": qs.count(), "results": serializer.data})

    def post(self, request):
        serializer = MobileSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MobileDetailView(APIView):
    """
    GET    /api/mobiles/<id>/  — retrieve
    PUT    /api/mobiles/<id>/  — full update
    PATCH  /api/mobiles/<id>/  — partial update
    DELETE /api/mobiles/<id>/  — delete
    """
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Mobile.objects.get(pk=pk)
        except Mobile.DoesNotExist:
            return None

    def get(self, request, pk):
        mobile = self.get_object(pk)
        if not mobile:
            return Response(
                {"detail": "Mobile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MobileSerializer(mobile, context={"request": request}).data)

    def put(self, request, pk):
        mobile = self.get_object(pk)
        if not mobile:
            return Response(
                {"detail": "Mobile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MobileSerializer(
            mobile, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        mobile = self.get_object(pk)
        if not mobile:
            return Response(
                {"detail": "Mobile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MobileSerializer(
            mobile, data=request.data, partial=True, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        mobile = self.get_object(pk)
        if not mobile:
            return Response(
                {"detail": "Mobile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        mobile.delete()
        return Response(
            {"detail": "Mobile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )