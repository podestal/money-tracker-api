from django.db import models
from django.conf import settings
from .utilities import normalize_balance


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
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):

        balance, created = Balance.objects.get_or_create(user=self.user)

        if self.pk:
            normalize_balance(balance, self.pk, self.user)

        if self.transaction_type == 'IN':
            balance.amount += self.amount
        else:
            balance.amount -= self.amount

        balance.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        balance = Balance.objects.get(user=self.user)

        normalize_balance(balance, self.pk, self.user)

        balance.save()
        super().delete(*args, **kwargs)

    
    