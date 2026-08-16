from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        INCREASE = "increase", "Increase"
        DECREASE = "decrease", "Decrease"

    product = models.ForeignKey(Product, related_name="transactions", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=8, choices=TransactionType.choices)
    quantity = models.PositiveIntegerField()
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)