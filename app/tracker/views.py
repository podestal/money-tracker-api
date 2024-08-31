from rest_framework.viewsets import ModelViewSet
from . import models
from . import serializers

class CategoryViewSet(ModelViewSet):

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

class BalanceViewSet(ModelViewSet):

    queryset = models.Balance.objects.all()
    serializer_class = serializers.BalanceSerializer

class TransactionViewSet(ModelViewSet):

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
