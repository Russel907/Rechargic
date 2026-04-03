from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Operator, Circle, Plan
from .serializers import OperatorSerializer, CircleSerializer, PlanSerializer

import uuid
from django.db import transaction
from .models import RechargeTransaction, Operator
from .utils import initiate_recharge, check_recharge_status, check_inspay_balance

class OperatorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operators = Operator.objects.filter(is_active=True)
        serializer = OperatorSerializer(operators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CircleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        circles = Circle.objects.filter(is_active=True)
        serializer = CircleSerializer(circles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = Plan.objects.filter(is_active=True)

        # Filters
        operator_id = request.query_params.get('operator')
        circle_id = request.query_params.get('circle')
        plan_type = request.query_params.get('plan_type')
        validity = request.query_params.get('validity')

        if operator_id:
            plans = plans.filter(operator__id=operator_id)
        if circle_id:
            plans = plans.filter(circle__id=circle_id)
        if plan_type:
            plans = plans.filter(plan_type=plan_type)
        if validity:
            plans = plans.filter(validity=validity)

        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InitiateRechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get data from request
        mobile_number = request.data.get('mobile_number')
        amount = request.data.get('amount')
        opcode = request.data.get('opcode')
        operator_id = request.data.get('operator_id')
        value1 = request.data.get('value1', '')
        value2 = request.data.get('value2', '')

        # Validate required fields
        if not mobile_number or not amount or not opcode:
            return Response(
                {"error": "mobile_number, amount and opcode are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique order ID
        order_id = f"RC{uuid.uuid4().hex[:12].upper()}"

        # Get operator if provided
        operator = None
        if operator_id:
            try:
                operator = Operator.objects.get(id=operator_id)
            except Operator.DoesNotExist:
                pass

        # Create pending transaction first
        recharge_txn = RechargeTransaction.objects.create(
            user=request.user,
            operator=operator,
            mobile_number=mobile_number,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        # Call InsPay API
        ok, response = initiate_recharge(
            opcode=opcode,
            number=mobile_number,
            amount=amount,
            order_id=order_id,
            value1=value1,
            value2=value2
        )

        if not ok:
            recharge_txn.status = 'failure'
            recharge_txn.message = response.get('error', 'Unknown error')
            recharge_txn.save()
            return Response(
                {"error": "Recharge failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Update transaction with InsPay response
        inspay_status = response.get('status', 'Pending')
        recharge_txn.inspay_txid = response.get('txid')
        recharge_txn.inspay_opid = response.get('opid')
        recharge_txn.message = response.get('message')

        if inspay_status == 'Success':
            recharge_txn.status = 'success'
        elif inspay_status == 'Failure':
            recharge_txn.status = 'failure'
        else:
            recharge_txn.status = 'pending'

        recharge_txn.save()

        return Response(
            {
                "message": response.get('message'),
                "status": recharge_txn.status,
                "order_id": order_id,
                "txid": response.get('txid'),
                "mobile_number": mobile_number,
                "amount": amount
            },
            status=status.HTTP_200_OK
        )


class RechargeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response(
                {"error": "order_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check in our DB first
        try:
            txn = RechargeTransaction.objects.get(
                order_id=order_id,
                user=request.user
            )
        except RechargeTransaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # If pending check InsPay for latest status
        if txn.status == 'pending':
            ok, response = check_recharge_status(order_id)
            if ok:
                inspay_status = response.get('status', 'Pending')
                if inspay_status == 'Success':
                    txn.status = 'success'
                elif inspay_status == 'Failure':
                    txn.status = 'failure'
                txn.save()

        return Response(
            {
                "order_id": txn.order_id,
                "mobile_number": txn.mobile_number,
                "amount": txn.amount,
                "status": txn.status,
                "message": txn.message,
                "created_at": txn.created_at
            },
            status=status.HTTP_200_OK
        )


class InspayBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ok, response = check_inspay_balance()
        if ok:
            return Response(response, status=status.HTTP_200_OK)
        return Response(
            {"error": "Could not fetch balance."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )