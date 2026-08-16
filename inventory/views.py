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


class ProductChangeAPIView(APIView):

    def post(self, request, pk):
        get_object_or_404(Product, pk=pk)
        serializer = InventoryChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction_type = serializer.validated_data.get('type')

        if transaction_type == 'increase':
            product = InventoryService.change(
                product_id=pk,
                transaction_type=transaction_type,
                amount=serializer.validated_data["quantity"],
            )

    
        elif transaction_type == 'decrease':
            try:
                product = InventoryService.change(
                product_id=pk,
                transaction_type=transaction_type,
                amount=serializer.validated_data["quantity"])

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
            status=status.HTTP_200_OK)


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