"""
Utilities functions
"""

from . import models
from django.core.exceptions import ValidationError


# Utility class to normalize balance
def normalize_balance(balance, transaction_pk, user):
    """Normalize the balance before any new update to transaction"""
    prev_transaction = models.Transaction.objects.get(pk=transaction_pk)
    if prev_transaction.user != user:
        raise ValidationError("Transaction does not belong to the user")
    if prev_transaction.transaction_type == "IN":
        balance.amount -= prev_transaction.amount
    else:
        balance.amount += prev_transaction.amount
