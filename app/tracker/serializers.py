"""
Serializers for Tracker
"""

from . import models
from rest_framework import serializers


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
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    """Project serializer"""

    class Meta:
        model = models.Task
        fields = "__all__"
