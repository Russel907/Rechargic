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

class DTHTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='dth_transactions'
    )
    operator_code = models.CharField(max_length=20)
    operator_name = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.customer_id} - ₹{self.amount} - {self.status}"

class ElectricityTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='electricity_transactions'
    )
    biller_code = models.CharField(max_length=20)
    biller_name = models.CharField(max_length=100)
    consumer_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    # Fetched bill details stored here
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    bill_amount = models.CharField(max_length=20, null=True, blank=True)
    due_date = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.consumer_number} - ₹{self.amount} - {self.status}"

class FastagTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='fastag_transactions'
    )
    operator_code = models.CharField(max_length=20)
    operator_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.vehicle_number} - ₹{self.amount} - {self.status}"

class BroadbandTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='broadband_transactions')
    operator_code = models.CharField(max_length=20)
    operator_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.account_number} - ₹{self.amount} - {self.status}"


class LPGTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lpg_transactions')
    operator_code = models.CharField(max_length=20)
    operator_name = models.CharField(max_length=100)
    consumer_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.consumer_number} - ₹{self.amount} - {self.status}"


class WaterTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='water_transactions')
    biller_code = models.CharField(max_length=20)
    biller_name = models.CharField(max_length=100)
    consumer_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    bill_amount = models.CharField(max_length=20, null=True, blank=True)
    due_date = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.consumer_number} - ₹{self.amount} - {self.status}"


class InsuranceTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='insurance_transactions')
    provider_code = models.CharField(max_length=20)
    provider_name = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    inspay_txid = models.CharField(max_length=100, null=True, blank=True)
    inspay_opid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.policy_number} - ₹{self.amount} - {self.status}"

class DTHPlan(models.Model):
    CATEGORY_CHOICES = [
        ('hindi', 'Hindi'),
        ('regional', 'Regional'),
        ('sports', 'Sports'),
        ('hd', 'HD'),
        ('combo', 'Combo'),
        ('ott', 'OTT'),
        ('basic', 'Basic'),
    ]

    operator_code = models.CharField(max_length=20)   # ATV, DTV, STV, TTV, VTV
    operator_name = models.CharField(max_length=100)
    plan_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    validity = models.CharField(max_length=50)
    channels = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operator_name} - {self.plan_name} - ₹{self.price}"