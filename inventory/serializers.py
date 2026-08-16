from rest_framework import serializers
from .models import Product, InventoryTransaction


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "quantity",
        ]
        read_only_fields = ["id", 'quantity']

class InventoryChangeSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, 
                                        error_messages={
            "required": "Quantity is required.",
            "invalid": "Quantity must be a valid integer.",
            "min_value": "Quantity must be greater than zero.",
        })
    type = serializers.ChoiceField(choices=["increase", "decrease"],
                                  error_messages={
            "required": "Transaction type is required.",
            "invalid_choice": 
                "Invalid transaction type. "
                "It must be either 'increase' or 'decrease'." }
                )

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