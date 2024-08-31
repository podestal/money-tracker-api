from typing import Iterable
from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Balance(models.Model):

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Transaction(models.Model):
    
    TRANSACTION_TYPE_COICES = [
        ('IN', 'Income'),
        ('OUT', 'Expense'),
    ]   

    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE_COICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        print(self.user)
        super().save(*args, **kwargs)