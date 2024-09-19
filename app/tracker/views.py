"""
Tracker Views
"""
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils.timezone import make_aware
from datetime import datetime
import calendar

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
        """ Retrieves filtered transactions for authenticated users, and all for superuser """
        queryset = models.Transaction.objects.select_related('user', 'category').order_by('-id')

        # If the current user is not a superuser, filter transactions for only the logged-in user
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.user)

        # Extract 'created_at' from the request's query parameters
        created_at = self.request.query_params.get('created_at')

        if created_at:
            try:
                # Try parsing the 'created_at' parameter as a date in the format "YYYY-MM-DD"
                date = datetime.strptime(created_at, "%Y-%m-%d")
                
                # Get the first day of the month (e.g., "2024-09-01" for September 2024)
                first_day = make_aware(datetime(date.year, date.month, 1))
                
                # Get the last day of the month by determining the total number of days in that month
                last_day = make_aware(datetime(date.year, date.month, calendar.monthrange(date.year, date.month)[1]))
                
                # Filter the queryset by the range from the first day to the last day of the specified month
                queryset = queryset.filter(created_at__range=(first_day, last_day))

            # Handle any errors caused by invalid date formats
            except ValueError as e:
                # Log the error and return an empty queryset if the date is invalid
                print('Value Error', e)
                queryset = queryset.none()

        # Return the filtered queryset
        return queryset
