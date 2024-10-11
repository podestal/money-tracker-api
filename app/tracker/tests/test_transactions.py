import pytest
from rest_framework import status
from model_bakery import baker
from tracker.models import Transaction, Balance
from core.models import User
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db  # Apply to all tests in this module


@pytest.fixture
def api_client():
    """Fixture to create a DRF API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a user."""
    return baker.make(User)


@pytest.fixture
def authenticated_user(api_client, create_user):
    """Fixture to authenticate a user."""
    api_client.force_authenticate(user=create_user)
    return create_user


@pytest.fixture
def create_superuser():
    """Fixture to create a superuser."""
    return baker.make(User, is_superuser=True)


@pytest.fixture
def authenticated_superuser(api_client, create_superuser):
    """Fixture to authenticate a superuser."""
    api_client.force_authenticate(user=create_superuser)
    return create_superuser


@pytest.fixture
def balance(authenticated_user):
    """Fixture to create a balance for the authenticated user."""
    return baker.make(Balance, user=authenticated_user, amount=100.00)


@pytest.fixture
def category(authenticated_user):
    """Fixture to create a category for the transaction."""
    return baker.make("tracker.Category", user=authenticated_user)


@pytest.fixture
def transaction(authenticated_user, category):
    """Fixture to create a transaction for the authenticated user."""
    return baker.make(
        Transaction,
        user=authenticated_user,
        category=category,
        amount=50.00,
        transaction_type="IN",
    )


# 1. Test if unauthenticated users can't access transactions
def test_transaction_list_unauthenticated(api_client):
    response = api_client.get("/api/transactions/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 2. Test retrieving transactions for authenticated users
def test_get_transactions_for_authenticated_user(
    authenticated_user, api_client, transaction
):
    response = api_client.get("/api/transactions/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == transaction.id


# 3. Test creating a transaction
def test_create_transaction(authenticated_user, api_client, category):
    data = {
        "transaction_type": "OUT",
        "amount": 20.00,
        "description": "Test Expense",
        "category": category.id,
    }
    response = api_client.post("/api/transactions/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["amount"] == 20.00
    assert Transaction.objects.filter(user=authenticated_user, amount=20.00).exists()


# 4. Test updating a transaction
def test_update_transaction(authenticated_user, api_client, transaction):
    data = {
        "transaction_type": "OUT",
        "amount": 75.00,
        "description": "Updated Expense",
    }
    response = api_client.patch(f"/api/transactions/{transaction.id}/", data)
    assert response.status_code == status.HTTP_200_OK
    transaction.refresh_from_db()
    assert transaction.amount == 75.00


# 5. Test deleting a transaction
def test_delete_transaction(authenticated_user, api_client, transaction):
    response = api_client.delete(f"/api/transactions/{transaction.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Transaction.objects.filter(id=transaction.id).exists()


# 6. Test balance update after transaction creation
def test_balance_update_after_transaction_creation(
    authenticated_user, api_client, balance
):
    data = {
        "transaction_type": "IN",
        "amount": 100.00,
        "description": "Salary",
    }
    response = api_client.post("/api/transactions/", data)
    assert response.status_code == status.HTTP_201_CREATED
    balance.refresh_from_db()
    assert balance.amount == 200.00  # Original balance 100.00 + 100.00 transaction


# 7. Test balance update after transaction deletion
def test_balance_update_after_transaction_deletion(
    authenticated_user, api_client, transaction, balance
):
    initial_balance = balance.amount
    response = api_client.delete(f"/api/transactions/{transaction.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    balance.refresh_from_db()
    assert (
        balance.amount == initial_balance
    )  # Ensure balance is normalized back to initial amount


# 8. Test superuser can list all transactions
def test_superuser_can_list_all_transactions(
    authenticated_superuser, api_client, transaction
):
    response = api_client.get("/api/transactions/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1  # Ensure superuser can access transactions
