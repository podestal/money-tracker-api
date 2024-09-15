"""
Tracker Views
"""
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serializers


class CategoryViewSet(ModelViewSet):
    """Category viewset"""
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieves filtered categories for authenticated users, and all for superuser"""
        if self.request.user.is_superuser:
            return models.Category.objects.select_related('user')
        return models.Category.objects.filter(user=self.user).select_related('user')


class BalanceViewSet(ModelViewSet):
    """Balance viewset"""
    serializer_class = serializers.BalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retrieves filtered balance for authenticated users, and all for superuser"""
        if self.request.user.is_superuser:
            return models.Balance.objects.select_related('user')
        # Return an empty queryset by default for non-superusers
        return models.Balance.objects.none()
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_balance_for_authenticated_user(self, request):
        """Return the balance of the authenticated user or create one if it doesn't exist"""
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
        """Retrieves filtered transactions for authenticated users, and all for superuser"""
        if self.request.user.is_superuser:
            return models.Transaction.objects.select_related('user', 'category').order_by('-created_at')
        return models.Transaction.objects.filter(user=self.user).select_related('user', 'category').order_by('-created_at')
