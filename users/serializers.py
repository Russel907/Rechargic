import re
from rest_framework import serializers
from .models import User


class SignupSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = ['name', 'phone', 'referral_code']

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def validate_name(self, value):
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Name should contain only letters.")
        return value

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        user = User.objects.create_user(**validated_data)

        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                user.referred_by = referrer
                user.save()

                from wallet.models import Wallet, Transaction
                from django.db import transaction as db_transaction

                with db_transaction.atomic():
                    referrer_wallet, _ = Wallet.objects.get_or_create(user=referrer)
                    referrer_wallet.balance += 100
                    referrer_wallet.save()

                    Transaction.objects.create(
                        wallet=referrer_wallet,
                        amount=100,
                        transaction_type='credit',
                        category='cashback',
                        description=f'Referral bonus — {user.phone} joined using your code!'
                    )

                    new_user_wallet, _ = Wallet.objects.get_or_create(user=user)
                    new_user_wallet.balance += 100
                    new_user_wallet.save()

                    Transaction.objects.create(
                        wallet=new_user_wallet,
                        amount=100,
                        transaction_type='credit',
                        category='cashback',
                        description=f'Welcome bonus — joined via referral!'
                    )

            except User.DoesNotExist:
                pass

        return user