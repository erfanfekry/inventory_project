from rest_framework.views import APIView
from rest_framework import generics
from .services import InventoryService
from .exceptions import InsufficientInventoryError
from .serializers import (ProductSerializer,
                          InventoryChangeSerializer,
                          InventoryTransactionSerializer)
from .models import Product
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import status
from rest_framework.views import Response


class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductIncreaseAPIView(APIView):

    def post(self, request, pk):
        serializer = InventoryChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = InventoryService.increase(
            product_id=pk,
            amount=serializer.validated_data["quantity"],
        )

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_200_OK,
        )


class ProductDecreaseAPIView(APIView):

    def post(self, request, pk):
        serializer = InventoryChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = InventoryService.decrease(
                product_id=pk,
                amount=serializer.validated_data["quantity"],
            )
        except InsufficientInventoryError as exc:
            return Response(
                {
                    "error": {
                        "code": "INSUFFICIENT_INVENTORY",
                        "message": str(exc),
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_200_OK,
        )

class ProductHistoryAPIView(APIView):

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        transactions = product.transactions.order_by("-created_at", "-id")

        serializer = InventoryTransactionSerializer(
            transactions,
            many=True,
        )

        return Response({
            "product_id": product.id,
            "current_quantity": product.quantity,
            "transactions": serializer.data,
        })