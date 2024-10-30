"""
Serializers for Tracker
"""

from . import models
from rest_framework import serializers
from djoser.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""

    class Meta:
        model = models.Category
        fields = ["id", "name"]

    def create(self, validated_data):
        """Crates a category using the user info in the request"""
        user = self.context["request"].user
        return models.Category.objects.create(user=user, **validated_data)


class BalanceSerializer(serializers.ModelSerializer):
    """Balance serializer"""

    class Meta:
        model = models.Balance
        fields = ["id", "amount"]


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""

    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "transaction_type",
            "amount",
            "created_at",
            "updated_at",
            "description",
            "category",
        ]

    def create(self, validated_data):
        """Crates a transaction using the user info in the request"""
        user = self.context["request"].user
        return models.Transaction.objects.create(user=user, **validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer"""

    class Meta:
        model = models.Project
        fields = ["id", "name", "description", "end_date", "created_at", "updated_at", "is_active"]

    def create(self, validated_data):
        user = self.context["request"].user
        return models.Project.objects.create(user=user, **validated_data)


class GetTaskSerializer(serializers.ModelSerializer):
    """Get Task serializer"""

    owner = UserSerializer()

    class Meta:
        model = models.Task
        fields = [
            "id",
            "project",
            "name",
            "description",
            "status",
            "priority",
            "owner",
            "due_date",
            "created_at",
            "updated_at",
            "user",
        ]


class UpdateTaskSerializer(serializers.ModelSerializer):
    """Update Task serializer"""

    class Meta:
        model = models.Task
        fields = [
            "project",
            "name",
            "description",
            "status",
            "priority",
            "owner",
            "due_date",
            "created_at",
            "updated_at",
        ]


class CreateTaskSerializer(serializers.ModelSerializer):
    """Create Task serializer"""

    class Meta:
        model = models.Task
        fields = [
            "id",
            "project",
            "name",
            "priority",
            "owner",
            "due_date",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return models.Task.objects.create(user=user, **validated_data)


class GetTeamSerializer(serializers.ModelSerializer):
    """Get Team Serializer"""

    members = UserSerializer(many=True)

    class Meta:
        model = models.Team
        fields = ["id", "user", "members"]


class CreateTeamSerializer(serializers.ModelSerializer):
    """Create Team Serializer"""

    class Meta:
        model = models.Team
        fields = ["members"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        user = self.context["request"].user
        team = models.Team.objects.create(user=user)
        team.members.set(members)

        return team
