"""
Tracker Views
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.timezone import make_aware
from datetime import datetime
import calendar

from . import models
from . import serializers
from . import permissions as own_permissions


class CategoryViewSet(ModelViewSet):
    """Category viewset"""

    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieves filtered categories for authenticated users
        and all for superuser"""
        # if self.request.user.is_superuser:
        #     return models.Category.objects.select_related("user")
        return models.Category.objects.filter(user=self.request.user).select_related("user")


class BalanceViewSet(ModelViewSet):
    """Balance viewset"""

    serializer_class = serializers.BalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieves filtered balance for authenticated users, and all for superuser"""
        # if self.request.user.is_superuser:
        #     return models.Balance.objects.select_related("user")
        # Return an empty queryset by default for non-superusers
        return models.Balance.objects.none()

    @action(detail=False, methods=["get"], url_path="me")
    def get_balance_for_authenticated_user(self, request):
        """Return the balance of the authenticated user
        or create one if it doesn't exist"""
        # Get or create the balance for the authenticated user
        balance, created = models.Balance.objects.get_or_create(user=request.user)

        # Serialize the balance object
        serializer = serializers.BalanceSerializer(balance)
        return Response(serializer.data)


class TransactionViewSet(ModelViewSet):
    """Transaction viewset"""

    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieves filtered transactions for authenticated users,
        and all for superuser"""
        queryset = (
            models.Transaction.objects.filter(user=self.request.user)
            .select_related("user", "category")
            .order_by("-created_at", "-id")
        )

        created_at = self.request.query_params.get("created_at")

        if created_at:
            try:
                date = datetime.strptime(created_at, "%Y-%m-%d")
                first_day = make_aware(datetime(date.year, date.month, 1))
                last_day = make_aware(
                    datetime(
                        date.year,
                        date.month,
                        calendar.monthrange(date.year, date.month)[1],
                    )
                )

                queryset = queryset.filter(created_at__range=(first_day, last_day))

            except ValueError as e:
                print("Value Error", e)
                queryset = queryset.none()

        # Return the filtered queryset
        return queryset


class ProjectViewSet(ModelViewSet):
    """Project ViewSet"""

    serializer_class = serializers.ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Project.objects.select_related("user").order_by("-updated_at")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        """Retrieves filtered projects for authenticated users,
        and all for superuser"""
        # if not self.request.user.is_superuser:
        #     return self.queryset.filter(user=self.request.user)
        # return self.queryset.all()
        return self.queryset.filter(user=self.request.user)


class TaskViewSet(ModelViewSet):

    # serializer_class = serializers.TaskSerializer
    permission_classes = [permissions.IsAuthenticated, own_permissions.IsOwnerOfProject]
    queryset = (
        models.Task.objects.select_related("project", "user")
        .prefetch_related("owner")
        .order_by("-updated_at")
    )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateTaskSerializer
        if self.request.method in ["PUT", "PATCH"]:
            return serializers.UpdateTaskSerializer
        return serializers.GetTaskSerializer

    def get_queryset(self):
        """Retrieves filtered tasks for authenticated users, and all for superuser"""
        return self.queryset.filter(
            project__user=self.request.user, project_id=self.kwargs["projects_pk"]
        )


class TeamViewSet(ModelViewSet):

    # permission_classes = [permissions.IsAuthenticated]
    queryset = models.Team.objects.select_related("user").prefetch_related("members")
    serializer_class = serializers.TeamSerializer
