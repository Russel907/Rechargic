from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from decimal import Decimal
from .models import Wallet, Transaction
from .serializers import WalletSerializer, AddMoneySerializer, TransactionSerializer
from recharge.models import (
    RechargeTransaction, DTHTransaction,
    ElectricityTransaction, FastagTransaction,
    BroadbandTransaction, LPGTransaction,
    WaterTransaction, InsuranceTransaction
)

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

class WalletTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_phone = request.data.get('phone')
        amount = request.data.get('amount')

        # Validate
        if not receiver_phone or not amount:
            return Response(
                {"error": "phone and amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = Decimal(str(amount))
        if amount <= 0:
            return Response(
                {"error": "Amount must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check receiver exists
        from users.models import User
        try:
            receiver = User.objects.get(phone=receiver_phone)
        except User.DoesNotExist:
            return Response(
                {"error": "No user found with this phone number."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Can't transfer to yourself
        if receiver == request.user:
            return Response(
                {"error": "Cannot transfer to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get sender wallet
        sender_wallet, _ = Wallet.objects.get_or_create(user=request.user)

        # Check balance
        if sender_wallet.balance < amount:
            return Response(
                {"error": f"Insufficient balance. Your balance is ₹{sender_wallet.balance}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get receiver wallet
        receiver_wallet, _ = Wallet.objects.get_or_create(user=receiver)

        # Transfer atomically
        with transaction.atomic():
            # Deduct from sender
            sender_wallet.balance -= amount
            sender_wallet.save()

            Transaction.objects.create(
                wallet=sender_wallet,
                amount=amount,
                transaction_type='debit',
                category='transfer',
                description=f'Transfer to {receiver_phone}'
            )

            # Add to receiver
            receiver_wallet.balance += amount
            receiver_wallet.save()

            Transaction.objects.create(
                wallet=receiver_wallet,
                amount=amount,
                transaction_type='credit',
                category='transfer',
                description=f'Transfer from {request.user.phone}'
            )

        return Response(
            {
                "message": f"₹{amount} transferred to {receiver_phone} successfully!",
                "new_balance": sender_wallet.balance
            },
            status=status.HTTP_200_OK
        )

class UnifiedHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from recharge.models import RechargeTransaction, DTHTransaction, ElectricityTransaction

        history = []

        # Mobile recharge
        for t in RechargeTransaction.objects.filter(user=request.user):
            history.append({
                "type": "Mobile Recharge",
                "number": t.mobile_number,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })

        # DTH
        for t in DTHTransaction.objects.filter(user=request.user):
            history.append({
                "type": "DTH Recharge",
                "number": t.customer_id,
                "operator": t.operator_name,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })

        # Electricity
        for t in ElectricityTransaction.objects.filter(user=request.user):
            history.append({
                "type": "Electricity Bill",
                "number": t.consumer_number,
                "biller": t.biller_name,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })

        # Wallet transactions
        wallet = Wallet.objects.filter(user=request.user).first()
        if wallet:
            for t in wallet.transactions.all():
                history.append({
                    "type": t.get_category_display(),
                    "amount": str(t.amount),
                    "transaction_type": t.transaction_type,
                    "description": t.description,
                    "date": t.created_at,
                })

        # Sort all by date, newest first
        history.sort(key=lambda x: x['date'], reverse=True)

        return Response(history, status=status.HTTP_200_OK)
        # Broadband
        for t in BroadbandTransaction.objects.filter(user=request.user):
            history.append({
                "type": "Broadband Bill",
                "number": t.account_number,
                "operator": t.operator_name,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })
            
        # LPG
        for t in LPGTransaction.objects.filter(user=request.user):
            history.append({
                "type": "LPG Gas",
                "number": t.consumer_number,
                "operator": t.operator_name,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })
                
        # Water
        for t in WaterTransaction.objects.filter(user=request.user):
            history.append({
                "type": "Water Bill",
                "number": t.consumer_number,
                "biller": t.biller_name,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })
        
        # Insurance
        for t in InsuranceTransaction.objects.filter(user=request.user):
            history.append({
                "type": "Insurance Premium",
                "number": t.policy_number,
                "provider": t.provider_name,
                "amount": str(t.amount),
                "status": t.status,
                "order_id": t.order_id,
                "date": t.created_at,
            })