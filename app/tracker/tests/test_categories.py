import pytest

from rest_framework import status
from model_bakery import baker
from tracker.models import Category
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
def category(authenticated_user):
    """Fixture to create a category for the authenticated user."""
    return baker.make(Category, user=authenticated_user)


# 1. Test if unauthenticated users can't access categories
def test_category_list_unauthenticated(api_client):
    response = api_client.get("/api/categories/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 2. Test creating a category as an authenticated user
def test_create_category(authenticated_user, api_client):
    payload = {"name": "Groceries"}
    response = api_client.post("/api/categories/", payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(user=authenticated_user, name="Groceries").exists()


# 3. Test retrieving categories for the authenticated user
def test_list_categories(authenticated_user, api_client, category):
    response = api_client.get("/api/categories/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == category.name


# 4. Test superuser gets all categories
def test_superuser_gets_all_categories(authenticated_superuser, api_client):
    baker.make(Category, _quantity=5)  # Create 5 categories for different users
    response = api_client.get("/api/categories/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5  # Superuser should get all categories


# 5. Test normal user cannot access another user’s categories
def test_normal_user_cannot_access_other_users_categories(
    authenticated_user, api_client
):
    other_user = baker.make(User)
    other_user_category = baker.make(Category, user=other_user)
    response = api_client.get("/api/categories/")
    assert response.status_code == status.HTTP_200_OK
    assert other_user_category.name not in [cat["name"] for cat in response.data]


# 6. Test updating a category as the authenticated user
def test_update_category(authenticated_user, api_client, category):
    payload = {"name": "New Category Name"}
    response = api_client.patch(f"/api/categories/{category.id}/", payload)
    assert response.status_code == status.HTTP_200_OK
    category.refresh_from_db()
    assert category.name == "New Category Name"


# 7. Test deleting a category as the authenticated user
def test_delete_category(authenticated_user, api_client, category):
    response = api_client.delete(f"/api/categories/{category.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Category.objects.filter(id=category.id).exists()


# 8. Test authenticated users can’t delete other users’ categories
def test_user_cannot_delete_other_users_categories(authenticated_user, api_client):
    other_user = baker.make(User)
    other_user_category = baker.make(Category, user=other_user)
    response = api_client.delete(f"/api/categories/{other_user_category.id}/")
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    )  # Not found for unauthorized access


# 9. Test superuser can delete any category
def test_superuser_can_delete_any_category(authenticated_superuser, api_client):
    user_category = baker.make(Category)
    response = api_client.delete(f"/api/categories/{user_category.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Category.objects.filter(id=user_category.id).exists()


# 10. Test validation for creating a category with an empty name
def test_create_category_with_empty_name(authenticated_user, api_client):
    payload = {"name": ""}
    response = api_client.post("/api/categories/", payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data
