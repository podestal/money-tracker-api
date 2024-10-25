import pytest
from rest_framework import status
from model_bakery import baker
from tracker.models import Transaction, Balance, Category


@pytest.fixture
def create_balance(create_user):
    """Fixture to retrieve or create a balance for the authenticated user."""
    balance, created = Balance.objects.get_or_create(user=create_user)
    balance.amount = 100.00
    balance.save()
    return balance


@pytest.fixture
def create_category(create_user):
    """Fixture to create a category for the transaction."""
    return baker.make(Category, user=create_user)


@pytest.fixture
def create_transaction(create_user, create_category):
    """Fixture to create a transaction for the authenticated user."""
    return baker.make(
        Transaction,
        user=create_user,
        category=create_category,
        amount=50.00,
        transaction_type="IN",
        created_at="2024-10-29",
    )


@pytest.fixture
def transaction_data(create_category):
    """Fixture to provide transaction data."""

    return {
        "transaction_type": "OUT",
        "amount": 20.00,
        "description": "Test Expense",
        "category": create_category.id,
        "created_at": "2024-10-29",
    }


@pytest.mark.django_db
class TestTransaction:

    def test_transaction_list_unauthenticated_return_401(self, api_client):
        response = api_client.get("/api/transactions/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_transaction_list_authenticated_return_200(
        self, authenticated_user, create_transaction
    ):
        response = authenticated_user.get("/api/transactions/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == create_transaction.id

    def test_create_transaction_unauthenticated_return_401(self, api_client, transaction_data):
        response = api_client.post("/api/transactions/", transaction_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_transaction_authenticated_return_201(
        self, authenticated_user, transaction_data
    ):
        response = authenticated_user.post("/api/transactions/", transaction_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == 20.00
        assert Transaction.objects.filter(description="Test Expense", amount=20.00).exists()

    def test_update_transaction_unauthenticated_return_401(self, api_client, create_transaction):
        update_data = {"description": "New Expense Description"}
        response = api_client.patch(f"/api/transactions/{create_transaction.id}/", update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_transaction_authenticated_return_200(
        self, authenticated_user, create_transaction
    ):
        update_data = {"description": "New Expense Description"}
        response = authenticated_user.patch(
            f"/api/transactions/{create_transaction.id}/", update_data
        )
        assert response.status_code == status.HTTP_200_OK
        create_transaction.refresh_from_db()
        assert create_transaction.description == "New Expense Description"

    def test_delete_project_unauthenticated_return_401(self, api_client, create_transaction):
        response = api_client.delete(f"/api/transactions/{create_transaction.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_project_authenticated_return_204(self, authenticated_user, create_transaction):
        response = authenticated_user.delete(f"/api/transactions/{create_transaction.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Transaction.objects.filter(id=create_transaction.id).exists()
