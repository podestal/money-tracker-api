from . import models
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Balance
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Transaction
        fields = '__all__'