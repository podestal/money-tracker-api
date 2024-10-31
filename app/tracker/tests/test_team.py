import pytest
from model_bakery import baker
from rest_framework import status
from tracker import models
from core.models import User


@pytest.fixture
def create_user():
    """Fixture to create a user."""
    return baker.make(User)


@pytest.fixture
def create_team(create_user):
    """Fixture to create a team for the authenticated user."""
    return baker.make(models.Team, user=create_user)


@pytest.fixture
def team_data(create_user):
    """Fixture to provide team data with multiple members."""
    members = [create_user, baker.make(User), baker.make(User)]
    return {"members": [member.id for member in members]}


@pytest.mark.django_db
class TestTeam:

    def test_get_teams_unauthenticated_return_401(self, api_client):
        response = api_client.get("/api/teams/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_teams_authenticated_return_200(self, authenticated_user, create_team):
        response = authenticated_user.get("/api/teams/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_team_me_authenticated_existing_team(self, authenticated_user, create_team):
        """
        Test that the /me endpoint returns the existing team for the authenticated user.
        """
        response = authenticated_user.get("/api/teams/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == create_team.id
        assert response.data["user"] == create_team.user.id
        assert len(response.data["members"]) == create_team.members.count()

    def test_get_team_me_authenticated_no_existing_team(self, authenticated_user):
        response = authenticated_user.get("/api/teams/me/")
        assert response.status_code == status.HTTP_200_OK
        assert models.Team.objects.count() == 1
        team = models.Team.objects.first()
        assert response.data["id"] == team.id
        assert response.data["user"] == authenticated_user.handler._force_user.id
        assert len(response.data["members"]) == 0

    def test_create_team_unauthenticated_return_401(self, api_client, team_data):
        response = api_client.post("/api/teams/", team_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_team_authenticated_return_201(self, authenticated_user, team_data):
        response = authenticated_user.post("/api/teams/", team_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert models.Team.objects.count() == 1
        team = models.Team.objects.first()
        assert team.members.count() == len(team_data["members"])

    def test_update_team_members_authenticated_return_200(
        self, authenticated_user, create_team, create_user
    ):
        new_member = baker.make(User)
        data = {"members": [new_member.id]}
        response = authenticated_user.patch(f"/api/teams/{create_team.id}/", data)
        assert response.status_code == status.HTTP_200_OK
        create_team.refresh_from_db()
        assert create_team.members.count() == 1
        assert new_member in create_team.members.all()

    def test_delete_team_unauthenticated_return_401(self, api_client, create_team):
        response = api_client.delete(f"/api/teams/{create_team.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_team_authenticated_return_204(self, authenticated_user, create_team):
        response = authenticated_user.delete(f"/api/teams/{create_team.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not models.Team.objects.filter(id=create_team.id).exists()
