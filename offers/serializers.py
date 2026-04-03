from rest_framework import serializers
from .models import Offer, OfferRedemption
from django.utils import timezone


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'description',
            'coupon_code',
            'category',
            'discount_percentage',
            'max_discount',
            'min_amount',
            'valid_till',
        ]


class RedeemOfferSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=50)

    def validate_coupon_code(self, value):
        try:
            offer = Offer.objects.get(coupon_code=value, is_active=True)
        except Offer.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive coupon code.")

        if offer.valid_till and offer.valid_till < timezone.now():
            raise serializers.ValidationError("This coupon has expired.")

        return value