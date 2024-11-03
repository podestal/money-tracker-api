import pytest
from model_bakery import baker
from rest_framework import status
from tracker import models
from core.models import User


@pytest.fixture
def create_projects(create_user):
    active_status = [True, True, False, False, False]
    return [
        baker.make(
            models.Project,
            user=create_user,
            name="New Project",
            description="Test description",
            end_date="2024-12-31",
            is_active=is_active,
        )
        for is_active in active_status
    ]


@pytest.fixture
def create_project(create_user):
    """Fixture to create a project for the authenticated user."""
    return baker.make(
        models.Project,
        user=create_user,
        name="New Project",
        description="Test description",
        end_date="2024-12-31",
    )

@pytest.fixture
def create_user_owner():
    """Fixture to create a separate user for task ownership."""
    return baker.make(User)

@pytest.fixture
def project_data():
    """Fixture to provide project data."""
    return {
        "name": "New Project",
        "description": "Test description",
        "end_date": "2024-12-31",
    }


@pytest.mark.django_db
class TestProject:

    def test_get_projects_unauthenticated_return_401(self, api_client, create_project):
        response = api_client.get("/api/projects/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_projects_for_authenticated_user_is_active_true_return_200(
        self, authenticated_user, create_projects
    ):
        response = authenticated_user.get("/api/projects/?is_active=true")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_projects_for_authenticated_user_is_active_false_return_200(
        self, authenticated_user, create_projects
    ):
        response = authenticated_user.get("/api/projects/?is_active=false")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_project_unauthenticated_return_401(self, api_client, project_data):
        response = api_client.post("/api/projects/", project_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_project_authenticated_return_201(self, authenticated_user, project_data):
        response = authenticated_user.post("/api/projects/", project_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert models.Project.objects.filter(name=project_data["name"]).exists()

    def test_update_project_unauthenticated_return_401(self, api_client, create_project):
        data = {"name": "Updated Project"}
        response = api_client.patch(f"/api/projects/{create_project.id}/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_project_authenticated_return_200(self, authenticated_user, create_project):
        data = {"name": "Updated Project"}
        response = authenticated_user.patch(f"/api/projects/{create_project.id}/", data)
        assert response.status_code == status.HTTP_200_OK
        create_project.refresh_from_db()
        assert create_project.name == "Updated Project"

    def test_delete_project_unauthenticated_return_401(self, api_client, create_project):
        response = api_client.delete(f"/api/projects/{create_project.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_project_authenticated_return_204(self, authenticated_user, create_project):
        response = authenticated_user.delete(f"/api/projects/{create_project.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not models.Project.objects.filter(id=create_project.id).exists()

    def test_task_owner_added_to_project_participants(self, create_project, create_user_owner):
        task = baker.make(
            models.Task,
            project=create_project,
            name="Test Task",
            owner=create_user_owner
        )
        create_project.refresh_from_db()
        assert create_user_owner in create_project.participants.all()
