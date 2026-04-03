from rest_framework import serializers
from .models import RewardPoints, RewardTransaction, RewardItem


class RewardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardTransaction
        fields = ['id', 'points', 'transaction_type', 'category', 'description', 'created_at']


class RewardPointsSerializer(serializers.ModelSerializer):
    transactions = RewardTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = RewardPoints
        fields = ['id', 'total_points', 'created_at', 'updated_at', 'transactions']


class RewardItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardItem
        fields = ['id', 'name', 'description', 'points_required']


class RedeemSerializer(serializers.Serializer):
    reward_item_id = serializers.IntegerField()

    def validate_reward_item_id(self, value):
        if not RewardItem.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive reward item.")
        return value