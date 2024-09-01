from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from . import models
from . import serializers

class CategoryViewSet(ModelViewSet):

    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Category.objects.select_related('user')
        return models.Category.objects.filter(user=self.user).select_related('user')

class BalanceViewSet(ModelViewSet):

    serializer_class = serializers.BalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Balance.objects.select_related('user')
        return models.Balance.objects.filter(user=self.user).select_related('user')

class TransactionViewSet(ModelViewSet):

    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Transaction.objects.select_related('user', 'category')
        return models.Transaction.objects.filter(user=self.user).select_related('user', 'category')
