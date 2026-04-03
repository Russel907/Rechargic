from django.db import models


class Offer(models.Model):
    CATEGORY_CHOICES = [
        ('recharge', 'Recharge'),
        ('bill_payment', 'Bill Payment'),
        ('dth', 'DTH'),
        ('broadband', 'Broadband'),
        ('shopping', 'Shopping'),
        ('ott', 'OTT'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    coupon_code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    valid_till = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.coupon_code}"


class OfferRedemption(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='redemptions')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='redemptions')
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone} - {self.offer.coupon_code}"