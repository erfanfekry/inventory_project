from rest_framework import serializers
from .models import Product, InventoryTransaction


class InventoryChangeSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "quantity",
        ]

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "transaction_type",
            "quantity",
            "created_at",
        ]
        read_only_fields = fields