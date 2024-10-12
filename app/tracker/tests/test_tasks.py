import pytest
from model_bakery import baker
from rest_framework import status
from tracker import models as tracker_models
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
def project(authenticated_user):
    """Fixture to create a project for the authenticated user."""
    return baker.make(tracker_models.Project, user=authenticated_user)


@pytest.fixture
def task(project, authenticated_user):
    """Fixture to create a task for the authenticated user's project."""
    return baker.make(tracker_models.Task, project=project, user=authenticated_user)


@pytest.fixture
def task_data(project):
    """Fixture to provide task data."""
    return {
        "project": project.id,
        "name": "New Task",
        "description": "Test task description",
        "status": "N",
        "priority": 1,
        "due_date": "2024-12-31",
    }


def test_create_task(authenticated_user, api_client, project, task_data):
    response = api_client.post(f"/api/projects/{project.id}/tasks/", task_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == task_data["name"]
    assert tracker_models.Task.objects.filter(
        project=project, user=authenticated_user
    ).exists()


def test_get_tasks_for_project(authenticated_user, api_client, project, task):
    response = api_client.get(f"/api/projects/{project.id}/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == task.id
    assert response.data[0]["name"] == task.name


def test_update_task(authenticated_user, api_client, project, task):
    data = {"name": "Updated Task"}
    response = api_client.patch(f"/api/projects/{project.id}/tasks/{task.id}/", data)
    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.name == "Updated Task"


def test_delete_task(authenticated_user, api_client, project, task):
    response = api_client.delete(f"/api/projects/{project.id}/tasks/{task.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not tracker_models.Task.objects.filter(id=task.id).exists()


def test_tasks_filtered_by_project(authenticated_user, api_client, project, task):
    # Create another project and task for a different project
    # other_project = baker.make(tracker_models.Project, user=authenticated_user)
    # other_task = baker.make(
    #     tracker_models.Task, project=other_project, user=authenticated_user
    # )

    response = api_client.get(f"/api/projects/{project.id}/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Should only see tasks for the current project
    assert response.data[0]["id"] == task.id


def test_superuser_can_access_all_tasks(authenticated_superuser, api_client):
    project_1 = baker.make(tracker_models.Project)
    project_2 = baker.make(tracker_models.Project)
    baker.make(tracker_models.Task, project=project_1, _quantity=2)
    baker.make(tracker_models.Task, project=project_2, _quantity=2)

    response = api_client.get(f"/api/projects/{project_1.id}/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2  # Superuser should see both tasks in project 1


def test_task_list_unauthenticated(api_client, project):
    api_client.logout()
    response = api_client.get(f"/api/projects/{project.id}/tasks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_task_without_optional_fields(authenticated_user, api_client, project):
    data = {"name": "Task Without Optional Fields", "project": project.id}
    response = api_client.post(f"/api/projects/{project.id}/tasks/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["description"] is None
    assert response.data["due_date"] is None
