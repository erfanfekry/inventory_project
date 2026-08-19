import pytest
from rest_framework.test import APIClient

from inventory.models import Product, InventoryTransaction


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="Keyboard",
        quantity=10,
    )


@pytest.mark.django_db
class TestInventoryAPI:

    def test_increase_inventory(self, api_client, product):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": 5,
            },
            format="json",
        )

        assert response.status_code == 200

        product.refresh_from_db()

        assert product.quantity == 15

        transaction = InventoryTransaction.objects.get(
            product=product
        )

        assert transaction.transaction_type == "increase"
        assert transaction.quantity == 5

    def test_decrease_inventory(self, api_client, product):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "decrease",
                "quantity": 4,
            },
            format="json",
        )

        assert response.status_code == 200

        product.refresh_from_db()

        assert product.quantity == 6

        transaction = InventoryTransaction.objects.get(
            product=product
        )

        assert transaction.transaction_type == "decrease"
        assert transaction.quantity == 4

    def test_inventory_cannot_become_negative(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "decrease",
                "quantity": 11,
            },
            format="json",
        )

        assert response.status_code == 409

        product.refresh_from_db()

        # Inventory must remain unchanged.
        assert product.quantity == 10

        # Failed operation must not create a transaction.
        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_inventory_can_be_decreased_to_zero(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "decrease",
                "quantity": 10,
            },
            format="json",
        )

        assert response.status_code == 200

        product.refresh_from_db()

        assert product.quantity == 0

        transaction = InventoryTransaction.objects.get(
            product=product
        )

        assert transaction.transaction_type == "decrease"
        assert transaction.quantity == 10

    def test_inventory_history(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        # 10 + 5 = 15
        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": 5,
            },
            format="json",
        )

        assert response.status_code == 200

        # 15 - 3 = 12
        response = api_client.post(
            url,
            {
                "type": "decrease",
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == 200

        # 12 + 8 = 20
        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": 8,
            },
            format="json",
        )

        assert response.status_code == 200

        product.refresh_from_db()

        assert product.quantity == 20

        history_url = f"/api/products/{product.id}/history/"

        response = api_client.get(history_url)

        assert response.status_code == 200

        history = response.data

        assert len(history) == 3

        assert history[0]["transaction_type"] == "increase"
        assert history[0]["quantity"] == 8

        assert history[1]["transaction_type"] == "decrease"
        assert history[1]["quantity"] == 3

        assert history[2]["transaction_type"] == "increase"
        assert history[2]["quantity"] == 5

    def test_invalid_quantity_zero(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": 0,
            },
            format="json",
        )

        assert response.status_code == 400

        product.refresh_from_db()

        assert product.quantity == 10

        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_invalid_quantity_negative(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": -5,
            },
            format="json",
        )

        assert response.status_code == 400

        product.refresh_from_db()

        assert product.quantity == 10

        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_invalid_quantity_type(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": "abc",
            },
            format="json",
        )

        assert response.status_code == 400

        product.refresh_from_db()

        assert product.quantity == 10

        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_invalid_transaction_type(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "invalid_type",
                "quantity": 5,
            },
            format="json",
        )

        assert response.status_code == 400

        product.refresh_from_db()

        assert product.quantity == 10

        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_missing_transaction_type(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "quantity": 5,
            },
            format="json",
        )

        assert response.status_code == 400

        product.refresh_from_db()

        assert product.quantity == 10

        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_missing_quantity(
        self,
        api_client,
        product,
    ):
        url = f"/api/products/{product.id}/inventory/"

        response = api_client.post(
            url,
            {
                "type": "increase",
            },
            format="json",
        )

        assert response.status_code == 400

        product.refresh_from_db()

        assert product.quantity == 10

        assert not InventoryTransaction.objects.filter(
            product=product
        ).exists()

    def test_nonexistent_product(
        self,
        api_client,
    ):
        url = "/api/products/9999/inventory/"

        response = api_client.post(
            url,
            {
                "type": "increase",
                "quantity": 10,
            },
            format="json",
        )

        assert response.status_code == 404