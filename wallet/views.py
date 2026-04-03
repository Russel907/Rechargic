from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Wallet, Transaction
from .serializers import WalletSerializer, AddMoneySerializer, TransactionSerializer


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get or create wallet for user
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddMoneySerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']

            # get_or_create wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)

            # Use atomic transaction — either both save or neither saves
            with transaction.atomic():
                wallet.balance += amount
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='credit',
                    category='add_money',
                    description=f'Added ₹{amount} to wallet'
                )

            return Response(
                {
                    "message": f"₹{amount} added to wallet successfully!",
                    "new_balance": wallet.balance
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all().order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)