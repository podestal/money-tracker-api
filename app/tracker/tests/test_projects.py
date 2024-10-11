import pytest
from model_bakery import baker
from rest_framework import status
from tracker import models as tracker_models
from core.models import User

pytestmark = pytest.mark.django_db


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
def project(authenticated_user):
    """Fixture to create a project for the authenticated user."""
    return baker.make(tracker_models.Project, user=authenticated_user)


@pytest.fixture
def project_data():
    """Fixture to provide project data."""
    return {
        "name": "New Project",
        "description": "Test description",
        "end_date": "2024-12-31",
    }


def test_create_project(authenticated_user, api_client, project_data):
    response = api_client.post("/api/projects/", project_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == project_data["name"]
    assert tracker_models.Project.objects.filter(user=authenticated_user).exists()


def test_get_projects_for_authenticated_user(authenticated_user, api_client, project):
    response = api_client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == project.id
    assert response.data[0]["name"] == project.name


def test_update_project(authenticated_user, api_client, project):
    data = {"name": "Updated Project"}
    response = api_client.patch(f"/api/projects/{project.id}/", data)
    assert response.status_code == status.HTTP_200_OK
    project.refresh_from_db()
    assert project.name == "Updated Project"


def test_delete_project(authenticated_user, api_client, project):
    response = api_client.delete(f"/api/projects/{project.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not tracker_models.Project.objects.filter(id=project.id).exists()


def test_superuser_can_list_all_projects(authenticated_superuser, api_client):
    baker.make(tracker_models.Project, _quantity=3)
    response = api_client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3


def test_project_list_unauthenticated(api_client):
    response = api_client.get("/api/projects/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_project_without_optional_fields(authenticated_user, api_client):
    data = {"name": "Project Without Optional Fields"}
    response = api_client.post("/api/projects/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["description"] is None
    assert response.data["end_date"] is None


def test_superuser_can_retrieve_all_projects(authenticated_superuser, api_client):
    baker.make(tracker_models.Project, _quantity=2)  # Projects created by other users
    response = api_client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


def test_user_can_only_access_own_projects(authenticated_user, api_client):
    other_user = baker.make(User)
    baker.make(tracker_models.Project, user=other_user)

    # Authenticated user should only see their own projects
    response = api_client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0  # No projects should be visible to this user
