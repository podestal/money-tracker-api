import pytest
from rest_framework import status
from model_bakery import baker
from tracker.models import Balance

# from core.models import User


@pytest.fixture
def create_balance(create_user):
    """Fixture to create a balance for the authenticated user."""
    return baker.make(Balance, user=create_user, amount=100.50)


@pytest.mark.django_db
class TestBalance:

    def test_balance_list_unauthenticated_return_401(self, api_client):
        response = api_client.get("/api/balances/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_balance_list_authenticated_return_200(self, authenticated_user):
        response = authenticated_user.get("/api/balances/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == 0.00

    def test_get_existing_balance_for_authenticated_user(self, authenticated_user, create_balance):
        response = authenticated_user.get("/api/balances/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == create_balance.amount

    def test_create_balance_if_none_exists(self, authenticated_user, create_user):
        response = authenticated_user.get("/api/balances/me/")
        assert response.status_code == status.HTTP_200_OK
        assert Balance.objects.filter(user=create_user).exists()
