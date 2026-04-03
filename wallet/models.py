from django.db import models
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - ₹{self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    TRANSACTION_CATEGORIES = [
        ('add_money', 'Added to Wallet'),
        ('recharge', 'Mobile Recharge'),
        ('dth', 'DTH Recharge'),
        ('electricity', 'Electricity Bill'),
        ('ott', 'OTT Subscription'),
        ('cashback', 'Cashback Received'),
        ('transfer', 'Transfer'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=TRANSACTION_CATEGORIES)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.phone} - {self.transaction_type} - ₹{self.amount}"