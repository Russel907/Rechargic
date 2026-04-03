from rest_framework import serializers
from .models import Wallet, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'transaction_type',
            'category',
            'description',
            'created_at'
        ]


class WalletSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id',
            'balance',
            'created_at',
            'updated_at',
            'transactions'
        ]


class AddMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        if value > 50000:
            raise serializers.ValidationError("Cannot add more than ₹50,000 at once.")
        return value