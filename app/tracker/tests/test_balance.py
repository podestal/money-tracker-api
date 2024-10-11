import pytest
from rest_framework import status
from model_bakery import baker
from tracker.models import Balance
from core.models import User

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
    return baker.make(Balance, user=authenticated_user, amount=100.50)


# 1. Test if unauthenticated users can't access balances
def test_balance_list_unauthenticated(api_client):
    response = api_client.get("/api/balances/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 2. Test retrieving the balance for the authenticated user
def test_get_balance_for_authenticated_user(authenticated_user, api_client):
    response = api_client.get("/api/balances/me/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["amount"] == 0.00  # Default amount if balance is created


# 3. Test retrieving an existing balance for the authenticated user
def test_get_existing_balance_for_authenticated_user(
    authenticated_user, api_client, balance
):
    response = api_client.get("/api/balances/me/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["amount"] == balance.amount


# 4. Test creating a balance when it doesn't exist
def test_create_balance_if_none_exists(authenticated_user, api_client):
    response = api_client.get("/api/balances/me/")
    assert response.status_code == status.HTTP_200_OK
    assert Balance.objects.filter(user=authenticated_user).exists()
