from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import RewardPoints, RewardTransaction, RewardItem
from .serializers import RewardPointsSerializer, RewardItemSerializer, RedeemSerializer


class RewardPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reward, created = RewardPoints.objects.get_or_create(user=request.user)
        serializer = RewardPointsSerializer(reward)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class RewardItemListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         items = RewardItem.objects.filter(is_active=True)
#         serializer = RewardItemSerializer(items, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class RewardItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = RewardItem.objects.filter(is_active=True)
        reward, _ = RewardPoints.objects.get_or_create(user=request.user)
        user_points = reward.total_points

        data = []
        for item in items:
            data.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "points_required": item.points_required,
                "min_points_to_unlock": item.min_points_to_unlock,
                "is_locked": user_points < item.min_points_to_unlock,
            })

        return Response(data, status=status.HTTP_200_OK)


class RedeemRewardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RedeemSerializer(data=request.data)
        if serializer.is_valid():
            reward_item_id = serializer.validated_data['reward_item_id']
            reward_item = RewardItem.objects.get(id=reward_item_id)

            reward, created = RewardPoints.objects.get_or_create(user=request.user)

            # Check if user has enough points
            if reward.total_points < reward_item.points_required:
                return Response(
                    {
                        "error": f"Not enough points. You have {reward.total_points} pts but need {reward_item.points_required} pts."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct points and create transaction atomically
            with transaction.atomic():
                reward.total_points -= reward_item.points_required
                reward.save()

                RewardTransaction.objects.create(
                    reward=reward,
                    points=reward_item.points_required,
                    transaction_type='redeemed',
                    category='redemption',
                    description=f'Redeemed {reward_item.name}'
                )

            return Response(
                {
                    "message": f"Successfully redeemed {reward_item.name}!",
                    "points_used": reward_item.points_required,
                    "remaining_points": reward.total_points
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)