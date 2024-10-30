"""
Models for Tracker api
"""

from django.utils import timezone
from django.db import models
from django.conf import settings
from .utilities import normalize_balance


class Category(models.Model):
    """Categoty model"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Balance(models.Model):
    """Balance model"""

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.amount


class Transaction(models.Model):
    """Transaction model"""

    TRANSACTION_TYPE_COICES = [
        ("IN", "Income"),
        ("OUT", "Expense"),
    ]

    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE_COICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.transaction_type

    def save(self, *args, **kwargs):
        """Create or update a transaction, updating the current balance"""
        balance, created = Balance.objects.get_or_create(user=self.user)

        if self.pk:
            normalize_balance(balance, self.pk, self.user)

        if self.transaction_type == "IN":
            balance.amount += self.amount
        else:
            balance.amount -= self.amount

        balance.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete the transaction, updating the current balance"""
        balance = Balance.objects.get(user=self.user)

        normalize_balance(balance, self.pk, self.user)

        balance.save()
        super().delete(*args, **kwargs)


class Team(models.Model):
    """Team Model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team"
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams")

    def __str__(self):
        return f"Team for {self.project.name}"


class Project(models.Model):
    """Project Model"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task Model"""

    STATUS_CHOICES = [
        ("N", "Not Started"),
        ("P", "In Progress"),
        ("R", "In Review"),
        ("C", "Completed"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="N")
    priority = models.PositiveIntegerField(default=0)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owner",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        project = self.project
        super().save(*args, **kwargs)
        project.updated_at = timezone.now()
        project.save()

    def delete(self, *args, **kwargs):

        project = self.project
        super().delete(*args, **kwargs)
        project.updated_at = timezone.now()
        project.save()
