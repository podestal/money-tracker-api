import pytest
from model_bakery import baker
from rest_framework import status
from tracker import models


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
def create_task(create_user, create_project):
    """Fixture to create a task for the authenticated user."""
    return baker.make(
        models.Task,
        project=create_project,
        user=create_user,
        name="New Task",
        description="Test description",
        status="N",
        priority=1,
        due_date="2024-12-31",
    )


@pytest.fixture
def create_tasks(create_user, create_project):
    task_names = [
        "task1",
        "task2",
        "task3",
        "task4",
        "task5",
    ]

    return [
        baker.make(
            models.Task,
            project=create_project,
            user=create_user,
            name=task_name,
            description="Test description",
            status="N",
            priority=1,
            due_date="2024-12-31",
        )
        for task_name in task_names
    ]


@pytest.fixture
def task_data(create_project):
    """Fixture to provide task data."""
    return {
        "project": create_project.id,
        "name": "New Task",
        "description": "Test task description",
        "status": "N",
        "priority": 1,
        "due_date": "2024-12-31",
    }


@pytest.mark.django_db
class TestTask:

    def test_get_tasks_for_project_unauthenticated_return_401(
        self, api_client, create_project, create_task
    ):
        response = api_client.get(f"/api/projects/{create_project.id}/tasks/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_tasks_for_project_authenticated_return_200(
        self, authenticated_user, create_project, create_tasks
    ):
        response = authenticated_user.get(f"/api/projects/{create_project.id}/tasks/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_get_tasks_for_projects_admin_can_access_all_tasks(
        self,
        admin_user,
    ):
        project_1 = baker.make(models.Project)
        project_2 = baker.make(models.Project)
        baker.make(models.Task, project=project_1, _quantity=2)
        baker.make(models.Task, project=project_2, _quantity=2)

        response = admin_user.get(f"/api/projects/{project_1.id}/tasks/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_task_updates_project(self, authenticated_user, create_project, task_data):

        initial_updated_at = create_project.updated_at
        response = authenticated_user.post(f"/api/projects/{create_project.id}/tasks/", task_data)

        assert response.status_code == status.HTTP_201_CREATED

        create_project.refresh_from_db()
        assert create_project.updated_at > initial_updated_at

    def test_create_task_for_project_unauthenticated_return_401(
        self, api_client, create_project, task_data
    ):
        response = api_client.post(f"/api/projects/{create_project.id}/tasks/", task_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_for_project_authenticated_return_201(
        self, authenticated_user, create_project, task_data
    ):
        response = authenticated_user.post(f"/api/projects/{create_project.id}/tasks/", task_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == task_data["name"]
        assert models.Task.objects.filter(name=task_data["name"]).exists()

    def test_update_task_for_project_unauthenticated_return_401(
        self, api_client, create_project, create_task
    ):
        data = {"name": "Updated Task"}
        response = api_client.patch(
            f"/api/projects/{create_project.id}/tasks/{create_task.id}/", data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_task_for_project_authenticated_return_200(
        self, authenticated_user, create_project, create_task
    ):
        data = {"name": "Updated Task"}
        response = authenticated_user.patch(
            f"/api/projects/{create_project.id}/tasks/{create_task.id}/", data
        )
        assert response.status_code == status.HTTP_200_OK
        create_task.refresh_from_db()
        assert create_task.name == "Updated Task"

    def test_update_task_updates_project(self, authenticated_user, create_project, create_task):
        initial_updated_at = create_project.updated_at
        data = {"name": "Updated Task"}
        response = authenticated_user.patch(
            f"/api/projects/{create_project.id}/tasks/{create_task.id}/", data
        )

        assert response.status_code == status.HTTP_200_OK

        create_project.refresh_from_db()
        assert create_project.updated_at > initial_updated_at

    def test_delete_task_for_project_unauthenticated_return_401(
        self, api_client, create_project, create_task
    ):
        response = api_client.delete(f"/api/projects/{create_project.id}/tasks/{create_task.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_task_for_project_authenticated_return_204(
        self, authenticated_user, create_project, create_task
    ):
        response = authenticated_user.delete(
            f"/api/projects/{create_project.id}/tasks/{create_task.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not models.Task.objects.filter(id=create_task.id).exists()

    def test_delete_task_updates_project(self, authenticated_user, create_project, create_task):

        initial_updated_at = create_project.updated_at
        response = authenticated_user.delete(
            f"/api/projects/{create_project.id}/tasks/{create_task.id}/"
        )
        assert response.status_code == 204

        create_project.refresh_from_db()
        assert create_project.updated_at > initial_updated_at
