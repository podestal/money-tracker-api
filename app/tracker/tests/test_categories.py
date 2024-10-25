import pytest

from rest_framework import status
from model_bakery import baker
from tracker.models import Category
from core.models import User


@pytest.fixture
def create_category(create_user):
    """Fixture to create a category for the authenticated user."""
    return baker.make(Category, user=create_user)


@pytest.mark.django_db
class TestCategory:

    def test_category_list_unauthenticated_return_401(self, api_client):
        response = api_client.get("/api/categories/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_category_list_authenticated_return_200(self, authenticated_user, create_category):
        response = authenticated_user.get("/api/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == create_category.name

    def test_other_user_cannot_access_other_users_categories(
        self, authenticated_user, create_category
    ):
        other_user = baker.make(User)
        other_user_category = baker.make(Category, user=other_user)
        response = authenticated_user.get("/api/categories/")
        assert response.status_code == status.HTTP_200_OK
        print("response.data", response.data)
        print("other_user_category", other_user_category.id)
        assert other_user_category.name not in [cat["name"] for cat in response.data]

    def test_create_category_authenticated_return_201(self, authenticated_user):
        payload = {"name": "Groceries"}
        response = authenticated_user.post("/api/categories/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="Groceries").exists()

    def test_create_category_unauthenticated_return_401(self, api_client):
        payload = {"name": "Groceries"}
        response = api_client.post("/api/categories/", payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_with_empty_name_authenticated_return_400(self, authenticated_user):
        payload = {"name": ""}
        response = authenticated_user.post("/api/categories/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_update_category_authenticated_return_200(self, authenticated_user, create_category):
        payload = {"name": "New Category Name"}
        response = authenticated_user.patch(f"/api/categories/{create_category.id}/", payload)
        assert response.status_code == status.HTTP_200_OK
        create_category.refresh_from_db()
        assert create_category.name == "New Category Name"

    def test_update_category_unauthenticated_return_401(self, api_client, create_category):
        payload = {"name": "New Category Name"}
        response = api_client.patch(f"/api/categories/{create_category.id}/", payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_category_authenticated_return_204(self, authenticated_user, create_category):
        response = authenticated_user.delete(f"/api/categories/{create_category.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=create_category.id).exists()

    def test_delete_category_unauthenticated_return_401(self, api_client, create_category):
        response = api_client.delete(f"/api/categories/{create_category.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_delete_other_users_categories_return_404(self, authenticated_user):
        other_user = baker.make(User)
        other_user_category = baker.make(Category, user=other_user)
        response = authenticated_user.delete(f"/api/categories/{other_user_category.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
