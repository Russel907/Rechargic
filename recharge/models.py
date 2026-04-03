from django.db import models
import uuid

class Operator(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    logo = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Circle(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    PLAN_TYPES = [
        ('recommended', 'Recommended'),
        ('unlimited_data', 'Unlimited Data'),
        ('talktime', 'Talktime'),
        ('data_only', 'Data Only'),
        ('entertainment', 'Entertainment (OTT)'),
        ('international', 'International Roaming'),
    ]

    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='plans')
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='plans')
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    validity = models.CharField(max_length=50)
    data = models.CharField(max_length=50)
    calls = models.CharField(max_length=100)
    includes = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    is_best_value = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.operator.name} - ₹{self.price} - {self.validity}"


class RechargeTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='recharge_transactions'
    )
    operator = models.ForeignKey(
        Operator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    mobile_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.mobile_number} - ₹{self.amount} - {self.status}"