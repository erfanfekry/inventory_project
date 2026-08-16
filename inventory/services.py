from django.db import transaction
from .models import Product, InventoryTransaction
from .exceptions import InsufficientInventoryError

class InventoryService:

    @staticmethod
    @transaction.atomic
    def change(product_id, transaction_type, amount):
        product = Product.objects.select_for_update().get(id=product_id)
        previous_quantity = product.quantity

        if transaction_type == 'decrease':
            if product.quantity < amount:
                        raise InsufficientInventoryError(
                                f"Insufficient inventory for \'{product.name}\'. "
                                f"Available: {product.quantity}, requested: {amount}."
                            )
            new_quantity = previous_quantity - amount

        else:
              new_quantity = previous_quantity + amount
        product.quantity = new_quantity
        product.save(update_fields=["quantity", "updated_at"])

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=transaction_type,
            quantity=amount,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
        )

        return product
