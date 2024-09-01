from . import models
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ['id', 'name']

    def create(self, validated_data):

        user = self.context['request'].user
        return models.Category.objects.create(user=user, **validated_data)

class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Balance
        fields = ['id', 'amount']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Transaction
        fields = ['id', 'transaction_type', 'amount', 'created_at', 'updated_at', 'description', 'category']

    def create(self, validated_data):
        
        user = self.context['request'].user
        return models.Transaction.objects.create(user=user, **validated_data)