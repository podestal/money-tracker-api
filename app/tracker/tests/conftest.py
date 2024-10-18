import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from core.models import User


@pytest.fixture
def api_client():
    """Fixture to provide APIClient instance."""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a normal user."""
    return baker.make(User)


@pytest.fixture
def create_admin_user():
    """Fixture to create an admin user."""
    return baker.make(User, is_staff=True)


@pytest.fixture
def authenticated_user(api_client, create_user):
    """Fixture to authenticate a normal user."""
    api_client.force_authenticate(user=create_user)
    return api_client


@pytest.fixture
def admin_user(api_client, create_admin_user):
    """Fixture to authenticate an admin user."""
    api_client.force_authenticate(user=create_admin_user)
    return api_client
