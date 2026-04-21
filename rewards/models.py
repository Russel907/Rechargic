from django.db import models
from django.conf import settings


class RewardPoints(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rewards')
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.total_points} pts"


class RewardTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('redeemed', 'Redeemed'),
    ]

    CATEGORIES = [
        ('recharge', 'Recharge'),
        ('ott', 'OTT Subscription'),
        ('referral', 'Referral'),
        ('cashback', 'Cashback'),
        ('redemption', 'Redemption'),
    ]

    reward = models.ForeignKey(RewardPoints, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reward.user.phone} - {self.transaction_type} - {self.points} pts"


class RewardItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    points_required = models.IntegerField()
    min_points_to_unlock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.points_required} pts"

