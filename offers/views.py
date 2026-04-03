from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Offer, OfferRedemption
from .serializers import OfferSerializer, RedeemOfferSerializer


class OfferListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        offers = Offer.objects.filter(is_active=True)

        # Filter by category if provided
        category = request.query_params.get('category')
        if category:
            offers = offers.filter(category=category)

        # Remove expired offers
        offers = offers.filter(
            valid_till__isnull=True
        ) | offers.filter(
            valid_till__gte=timezone.now()
        )

        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RedeemOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RedeemOfferSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data['coupon_code']
            offer = Offer.objects.get(coupon_code=coupon_code)

            # Check if user already redeemed this offer
            already_redeemed = OfferRedemption.objects.filter(
                user=request.user,
                offer=offer
            ).exists()

            if already_redeemed:
                return Response(
                    {"error": "You have already redeemed this offer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save redemption record
            OfferRedemption.objects.create(
                user=request.user,
                offer=offer
            )

            return Response(
                {
                    "message": f"Offer '{offer.title}' redeemed successfully!",
                    "coupon_code": offer.coupon_code,
                    "discount_percentage": offer.discount_percentage,
                    "max_discount": offer.max_discount,
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)