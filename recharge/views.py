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
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import re
from .models import (
    RechargeTransaction, Operator, DTHTransaction,
    ElectricityTransaction, FastagTransaction,
    BroadbandTransaction, LPGTransaction,
    WaterTransaction, InsuranceTransaction
)
from .models import DTHPlan
from .serializers import DTHPlanSerializer

def award_recharge_points(user, amount):
    from rewards.models import RewardPoints, RewardTransaction
    # 1 point for every ₹10 spent
    points_earned = int(float(amount) // 10)

    if points_earned > 0:
        reward, _ = RewardPoints.objects.get_or_create(user=user)
        reward.total_points += points_earned
        reward.save()

        RewardTransaction.objects.create(
            reward=reward,
            points=points_earned,
            transaction_type='earned',
            category='recharge',
            description=f'Earned {points_earned} points for ₹{amount} recharge'
        )

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

@method_decorator(ratelimit(key='user', rate='10/h', method='POST', block=True), name='post')
class InitiateRechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mobile_number = str(request.data.get('mobile_number', '')).strip()
        amount = request.data.get('amount')
        opcode = str(request.data.get('opcode', '')).strip()
        operator_id = request.data.get('operator_id')
        value1 = str(request.data.get('value1', '')).strip()
        value2 = str(request.data.get('value2', '')).strip()

        # Validations
        if not mobile_number or not amount or not opcode:
            return Response(
                {"error": "mobile_number, amount and opcode are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not re.match(r'^\d{10}$', mobile_number):
            return Response(
                {"error": "Invalid mobile number. Must be exactly 10 digits."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if amount > 10000:
                return Response(
                    {"error": "Amount cannot exceed ₹10,000 per transaction."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount."},
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

        # Create pending transaction first — always save before calling API
        # This way if API call crashes, we still have a record
        recharge_txn = RechargeTransaction.objects.create(
            user=request.user,
            operator=operator,
            mobile_number=mobile_number,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        # Call Inspay API
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

        inspay_status = response.get('status', 'Pending')
        recharge_txn.inspay_txid = response.get('txid')
        recharge_txn.inspay_opid = response.get('opid')
        recharge_txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            recharge_txn.status = 'success'
            # Points NOT awarded here — webhook confirms and awards
        elif inspay_status == 'Failure':
            recharge_txn.status = 'failure'
        else:
            recharge_txn.status = 'pending'
            recharge_txn.save()
            import time
            time.sleep(3)  # give Inspay a moment to finalize

            status_ok, status_response = check_recharge_status(order_id)
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    recharge_txn.status = 'success'
                    recharge_txn.inspay_txid = status_response.get('txid', recharge_txn.inspay_txid)
                elif final_status == 'Failure':
                    recharge_txn.status = 'failure'

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

# class RechargeStatusView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         order_id = request.query_params.get('order_id')

#         if not order_id:
#             return Response(
#                 {"error": "order_id is required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Check in our DB first
#         try:
#             txn = RechargeTransaction.objects.get(
#                 order_id=order_id,
#                 user=request.user
#             )
#         except RechargeTransaction.DoesNotExist:
#             return Response(
#                 {"error": "Transaction not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # If pending check InsPay for latest status
#         if txn.status == 'pending':
#             ok, response = check_recharge_status(order_id)
#             if ok:
#                 inspay_status = response.get('status', 'Pending')
#                 if inspay_status == 'Success':
#                     txn.status = 'success'
#                 elif inspay_status == 'Failure':
#                     txn.status = 'failure'
#                 txn.save()

#         return Response(
#             {
#                 "order_id": txn.order_id,
#                 "mobile_number": txn.mobile_number,
#                 "amount": txn.amount,
#                 "status": txn.status,
#                 "message": txn.message,
#                 "created_at": txn.created_at
#             },
#             status=status.HTTP_200_OK
#         )
class RechargeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response(
                {"error": "order_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine transaction type from order_id prefix
        # RC = Mobile, DTH = DTH, ELEC = Electricity, FT = Fastag
        # BB = Broadband, LPG = LPG, WT = Water, INS = Insurance

        txn_data = None

        # Mobile recharge
        if order_id.startswith('RC'):
            try:
                txn = RechargeTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "Mobile Recharge",
                    "number": txn.mobile_number,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except RechargeTransaction.DoesNotExist:
                pass

        # DTH
        elif order_id.startswith('DTH'):
            try:
                txn = DTHTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "DTH Recharge",
                    "number": txn.customer_id,
                    "operator": txn.operator_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except DTHTransaction.DoesNotExist:
                pass

        # Electricity
        elif order_id.startswith('ELEC'):
            try:
                txn = ElectricityTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "Electricity Bill",
                    "number": txn.consumer_number,
                    "biller": txn.biller_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except ElectricityTransaction.DoesNotExist:
                pass

        # Fastag
        elif order_id.startswith('FT'):
            try:
                txn = FastagTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "Fastag",
                    "number": txn.vehicle_number,
                    "operator": txn.operator_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except FastagTransaction.DoesNotExist:
                pass

        # Broadband
        elif order_id.startswith('BB'):
            try:
                txn = BroadbandTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "Broadband",
                    "number": txn.account_number,
                    "operator": txn.operator_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except BroadbandTransaction.DoesNotExist:
                pass

        # LPG
        elif order_id.startswith('LPG'):
            try:
                txn = LPGTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "LPG Gas",
                    "number": txn.consumer_number,
                    "operator": txn.operator_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except LPGTransaction.DoesNotExist:
                pass

        # Water
        elif order_id.startswith('WT'):
            try:
                txn = WaterTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "Water Bill",
                    "number": txn.consumer_number,
                    "biller": txn.biller_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except WaterTransaction.DoesNotExist:
                pass

        # Insurance
        elif order_id.startswith('INS'):
            try:
                txn = InsuranceTransaction.objects.get(order_id=order_id, user=request.user)
                if txn.status == 'pending':
                    ok, response = check_recharge_status(order_id)
                    if ok:
                        inspay_status = response.get('status', 'Pending')
                        if inspay_status == 'Success':
                            txn.status = 'success'
                        elif inspay_status == 'Failure':
                            txn.status = 'failure'
                        txn.save()
                txn_data = {
                    "order_id": txn.order_id,
                    "type": "Insurance",
                    "number": txn.policy_number,
                    "provider": txn.provider_name,
                    "amount": txn.amount,
                    "status": txn.status,
                    "message": txn.message,
                    "created_at": txn.created_at
                }
            except InsuranceTransaction.DoesNotExist:
                pass

        if txn_data:
            return Response(txn_data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Transaction not found."},
            status=status.HTTP_404_NOT_FOUND
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

class RechargeHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = RechargeTransaction.objects.filter(
            user=request.user
        ).order_by('-created_at')

        data = []
        for t in transactions:
            data.append({
                "order_id": t.order_id,
                "mobile_number": t.mobile_number,
                "operator": t.operator.name if t.operator else None,
                "amount": t.amount,
                "status": t.status,
                "txid": t.inspay_txid,
                "message": t.message,
                "created_at": t.created_at,
            })

        return Response(data, status=status.HTTP_200_OK)

class ActivePlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get latest successful recharge for each operator
        from django.db.models import Max

        latest_recharges = RechargeTransaction.objects.filter(
            user=request.user,
            status='success'
        ).order_by('-created_at')

        data = []
        for txn in latest_recharges:
            data.append({
                "operator": txn.operator.name if txn.operator else "Unknown",
                "mobile_number": txn.mobile_number,
                "amount": txn.amount,
                "recharged_at": txn.created_at,
                "order_id": txn.order_id,
            })

        return Response(data, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class InspayWebhookView(APIView):
    permission_classes = []

    def get(self, request):
        order_id = request.query_params.get('orderid')
        status_val = request.query_params.get('status')
        opid = request.query_params.get('opid')
        utr = request.query_params.get('utr')

        if not order_id or not status_val:
            return Response({"error": "Missing params"}, status=400)

        # Mobile recharge
        txn = RechargeTransaction.objects.filter(order_id=order_id).first()
        if txn and txn.status == 'pending':
            if status_val == 'Success':
                txn.status = 'success'
                txn.inspay_opid = opid
                txn.message = f"UTR: {utr}"
                txn.save()
                award_recharge_points(txn.user, txn.amount)
            elif status_val == 'Failure':
                txn.status = 'failure'
                txn.save()
            return Response({"message": "OK"}, status=200)

        # DTH
        dth_txn = DTHTransaction.objects.filter(order_id=order_id).first()
        if dth_txn and dth_txn.status == 'pending':
            if status_val == 'Success':
                dth_txn.status = 'success'
                dth_txn.inspay_opid = opid
                dth_txn.save()
                award_recharge_points(dth_txn.user, dth_txn.amount)
            elif status_val == 'Failure':
                dth_txn.status = 'failure'
                dth_txn.save()
            return Response({"message": "OK"}, status=200)

        # Electricity
        elec_txn = ElectricityTransaction.objects.filter(order_id=order_id).first()
        if elec_txn and elec_txn.status == 'pending':
            if status_val == 'Success':
                elec_txn.status = 'success'
                elec_txn.inspay_opid = opid
                elec_txn.save()
                award_recharge_points(elec_txn.user, elec_txn.amount)
            elif status_val == 'Failure':
                elec_txn.status = 'failure'
                elec_txn.save()
            return Response({"message": "OK"}, status=200)

        # Fastag
        ft_txn = FastagTransaction.objects.filter(order_id=order_id).first()
        if ft_txn and ft_txn.status == 'pending':
            if status_val == 'Success':
                ft_txn.status = 'success'
                ft_txn.inspay_opid = opid
                ft_txn.save()
                award_recharge_points(ft_txn.user, ft_txn.amount)
            elif status_val == 'Failure':
                ft_txn.status = 'failure'
                ft_txn.save()
            return Response({"message": "OK"}, status=200)

        # Broadband
        bb_txn = BroadbandTransaction.objects.filter(order_id=order_id).first()
        if bb_txn and bb_txn.status == 'pending':
            if status_val == 'Success':
                bb_txn.status = 'success'
                bb_txn.inspay_opid = opid
                bb_txn.save()
                award_recharge_points(bb_txn.user, bb_txn.amount)
            elif status_val == 'Failure':
                bb_txn.status = 'failure'
                bb_txn.save()
            return Response({"message": "OK"}, status=200)

        # LPG
        lpg_txn = LPGTransaction.objects.filter(order_id=order_id).first()
        if lpg_txn and lpg_txn.status == 'pending':
            if status_val == 'Success':
                lpg_txn.status = 'success'
                lpg_txn.inspay_opid = opid
                lpg_txn.save()
                award_recharge_points(lpg_txn.user, lpg_txn.amount)
            elif status_val == 'Failure':
                lpg_txn.status = 'failure'
                lpg_txn.save()
            return Response({"message": "OK"}, status=200)

        # Water
        wt_txn = WaterTransaction.objects.filter(order_id=order_id).first()
        if wt_txn and wt_txn.status == 'pending':
            if status_val == 'Success':
                wt_txn.status = 'success'
                wt_txn.inspay_opid = opid
                wt_txn.save()
                award_recharge_points(wt_txn.user, wt_txn.amount)
            elif status_val == 'Failure':
                wt_txn.status = 'failure'
                wt_txn.save()
            return Response({"message": "OK"}, status=200)

        # Insurance
        ins_txn = InsuranceTransaction.objects.filter(order_id=order_id).first()
        if ins_txn and ins_txn.status == 'pending':
            if status_val == 'Success':
                ins_txn.status = 'success'
                ins_txn.inspay_opid = opid
                ins_txn.save()
                award_recharge_points(ins_txn.user, ins_txn.amount)
            elif status_val == 'Failure':
                ins_txn.status = 'failure'
                ins_txn.save()
            return Response({"message": "OK"}, status=200)

        return Response({"message": "OK"}, status=200)

DTH_OPERATORS = {
    'ATV': 'Airtel DTH',
    'DTV': 'Dish TV',
    'STV': 'Sun Direct TV',
    'TTV': 'TATA Play',
    'VTV': 'Videocon DTH',
}

class DTHOperatorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operators = [
            {"code": code, "name": name}
            for code, name in DTH_OPERATORS.items()
        ]
        return Response(operators, status=status.HTTP_200_OK)


class InitiateDTHRechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer_id = request.data.get('customer_id')
        amount = request.data.get('amount')
        opcode = request.data.get('opcode')

        # Validations
        if not customer_id or not amount or not opcode:
            return Response(
                {"error": "customer_id, amount and opcode are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if opcode not in DTH_OPERATORS:
            return Response(
                {"error": "Invalid DTH operator code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not customer_id.strip():
            return Response(
                {"error": "Invalid customer ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_id = f"DTH{uuid.uuid4().hex[:12].upper()}"

        # Create pending transaction
        dth_txn = DTHTransaction.objects.create(
            user=request.user,
            operator_code=opcode,
            operator_name=DTH_OPERATORS[opcode],
            customer_id=customer_id,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        # Call Inspay — same API, different opcode
        ok, response = initiate_recharge(
            opcode=opcode,
            number=customer_id,
            amount=amount,
            order_id=order_id
        )

        if not ok:
            dth_txn.status = 'failure'
            dth_txn.message = response.get('error', 'Unknown error')
            dth_txn.save()
            return Response(
                {"error": "DTH recharge failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        inspay_status = response.get('status', 'Pending')
        dth_txn.inspay_txid = response.get('txid')
        dth_txn.inspay_opid = response.get('opid')
        dth_txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            dth_txn.status = 'success'
            # award_recharge_points(request.user, amount)
        elif inspay_status == 'Failure':
            dth_txn.status = 'failure'
        else:
            dth_txn.status = 'pending'
            dth_txn.save()

            import time
            time.sleep(3)  # give Inspay a moment to finalize

            status_ok, status_response = check_recharge_status(order_id)
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    dth_txn.status = 'success'
                    dth_txn.inspay_txid = status_response.get('txid', dth_txn.inspay_txid)
                elif final_status == 'Failure':
                    dth_txn.status = 'failure'
        dth_txn.save()

        return Response(
            {
                "message": response.get('message') or "Transaction failed. Please check details and try again.",
                "status": dth_txn.status,
                "order_id": order_id,
                "txid": response.get('txid'),
                "customer_id": customer_id,
                "operator": DTH_OPERATORS[opcode],
                "amount": amount
            },
            status=status.HTTP_200_OK
        )


class DTHHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = DTHTransaction.objects.filter(
            user=request.user
        ).order_by('-created_at')

        data = [
            {
                "order_id": t.order_id,
                "customer_id": t.customer_id,
                "operator": t.operator_name,
                "amount": t.amount,
                "status": t.status,
                "message": t.message,
                "created_at": t.created_at,
            }
            for t in transactions
        ]
        return Response(data, status=status.HTTP_200_OK)

# Electricity biller list — taken from Inspay operator codes
ELECTRICITY_BILLERS = {
    'BESCOM': 'Bangalore Electricity Supply Co. Ltd',
    'MSEDCL': 'Maharashtra State Electricity Distbn Co Ltd',
    'UPPCL': 'UPPCL-Postpaid and Smart Prepaid Meter Recharge',
    'TNPDCL': 'Tamil Nadu Power Distribution Corporation Limited',
    'PSPCL': 'Punjab State Power Corporation Ltd',
    'AEML': 'Adani Electricity Mumbai Limited',
    'BSESRSL': 'BSES Rajdhani Power Limited',
    'BSESYPL': 'BSES Yamuna Power Limited',
    'DHBVN': 'Dakshin Haryana Bijli Vitran Nigam',
    'UHBVN': 'Uttar Haryana Bijli Vitran Nigam',
    'KSEBL': 'Kerala State Electricity Board Ltd',
    'TPDDL': 'Tata Power - Delhi',
    'WBSEDCL': 'West Bengal State Electricity Distribution Company Ltd',
    'JBVNL': 'Jharkhand Bijli Vitran Nigam Limited',
    'CSPDCL': 'Chhattisgarh State Power Distribution Co. Ltd',
}


class ElectricityBillerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        billers = [
            {"code": code, "name": name}
            for code, name in ELECTRICITY_BILLERS.items()
        ]
        return Response(billers, status=status.HTTP_200_OK)


class FetchElectricityBillView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        consumer_number = str(request.data.get('consumer_number', '')).strip()
        biller_code = str(request.data.get('biller_code', '')).strip()

        if not consumer_number or not biller_code:
            return Response(
                {"error": "consumer_number and biller_code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if biller_code not in ELECTRICITY_BILLERS:
            return Response(
                {"error": "Invalid biller code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not consumer_number:
            return Response(
                {"error": "Invalid consumer number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "biller_code": biller_code,
                "biller_name": ELECTRICITY_BILLERS[biller_code],
                "consumer_number": consumer_number,
                "message": "Consumer number validated. Please enter bill amount to pay.",
            },
            status=status.HTTP_200_OK
        )


class PayElectricityBillView(APIView):
    """
    Step 2 — Pay the bill after user confirms.
    Frontend sends consumer_number, biller_code, amount.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        consumer_number = request.data.get('consumer_number')
        biller_code = request.data.get('biller_code')
        amount = request.data.get('amount')
        mobile = request.data.get('mobile', request.user.phone)
        customer_name = request.data.get('customer_name', '')
        bill_amount = request.data.get('bill_amount', '')
        due_date = request.data.get('due_date', '')

        if not consumer_number or not biller_code or not amount:
            return Response(
                {"error": "consumer_number, biller_code and amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if biller_code not in ELECTRICITY_BILLERS:
            return Response(
                {"error": "Invalid biller code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_id = f"ELEC{uuid.uuid4().hex[:12].upper()}"

        # Save transaction as pending
        elec_txn = ElectricityTransaction.objects.create(
            user=request.user,
            biller_code=biller_code,
            biller_name=ELECTRICITY_BILLERS[biller_code],
            consumer_number=consumer_number,
            amount=amount,
            order_id=order_id,
            status='pending',
            customer_name=customer_name,
            bill_amount=bill_amount,
            due_date=due_date
        )

        # Call Inspay to pay
        ok, response = initiate_recharge(
            opcode=biller_code,
            number=consumer_number,
            amount=amount,
            order_id=order_id,
            value1=mobile
        )

        if not ok:
            elec_txn.status = 'failure'
            elec_txn.message = response.get('error', 'Unknown error')
            elec_txn.save()
            return Response(
                {"error": "Bill payment failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        inspay_status = response.get('status', 'Pending')
        elec_txn.inspay_txid = response.get('txid')
        elec_txn.inspay_opid = response.get('opid')
        elec_txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            elec_txn.status = 'success'
            award_recharge_points(request.user, amount)
        elif inspay_status == 'Failure':
            elec_txn.status = 'failure'
        else:
            elec_txn.status = 'pending'
            elec_txn.save()

            import time
            time.sleep(3)

            status_ok, status_response = check_recharge_status(order_id)   # ← fixed, was check_elec_status
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    elec_txn.status = 'success'
                    elec_txn.inspay_txid = status_response.get('txid', elec_txn.inspay_txid)
                elif final_status == 'Failure':
                    elec_txn.status = 'failure'
        elec_txn.save()
        
        return Response(
            {
                "message": response.get('message'),
                "status": elec_txn.status,
                "order_id": order_id,
                "txid": response.get('txid'),
                "consumer_number": consumer_number,
                "biller": ELECTRICITY_BILLERS[biller_code],
                "amount": amount
            },
            status=status.HTTP_200_OK
        )


class ElectricityHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = ElectricityTransaction.objects.filter(
            user=request.user
        ).order_by('-created_at')

        data = [
            {
                "order_id": t.order_id,
                "consumer_number": t.consumer_number,
                "biller": t.biller_name,
                "amount": t.amount,
                "status": t.status,
                "customer_name": t.customer_name,
                "due_date": t.due_date,
                "created_at": t.created_at,
            }
            for t in transactions
        ]
        return Response(data, status=status.HTTP_200_OK)

FASTAG_OPERATORS = {
    'HDFCFT': 'HDFC Bank FASTag',
    'ICICIFT': 'ICICI Bank FASTag',
    'SBOIFT': 'State Bank of India NETC FASTag',
    'YBLFT': 'Yes Bank FASTag',
    'IDFCFT': 'IDFC FIRST Bank FASTag',
    'KMBFT': 'Kotak Mahindra Bank FASTag',
    'PNBLFT': 'Punjab National Bank FASTag',
    'BOBFT': 'Bank of Baroda FASTag',
    'IBFT': 'IndusInd Bank FASTag',
    'IDBIFT': 'IDBI Bank FASTag',
    'FBFT': 'Federal Bank FASTag',
    'AXISFT': 'Axis Bank FASTag',
}


class FastagOperatorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operators = [
            {"code": code, "name": name}
            for code, name in FASTAG_OPERATORS.items()
        ]
        return Response(operators, status=status.HTTP_200_OK)


class InitiateFastagRechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vehicle_number = str(request.data.get('vehicle_number', '')).strip().upper()
        amount = request.data.get('amount')
        opcode = str(request.data.get('opcode', '')).strip()

        # Validations
        if not vehicle_number or not amount or not opcode:
            return Response(
                {"error": "vehicle_number, amount and opcode are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if opcode not in FASTAG_OPERATORS:
            return Response(
                {"error": "Invalid Fastag operator code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Indian vehicle number format validation
        # Formats: MH12AB1234 or MH12A1234
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$', vehicle_number):
            return Response(
                {"error": "Invalid vehicle number format. Example: MH12AB1234"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if amount > 50000:
                return Response(
                    {"error": "Amount cannot exceed ₹50,000."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_id = f"FT{uuid.uuid4().hex[:12].upper()}"

        fastag_txn = FastagTransaction.objects.create(
            user=request.user,
            operator_code=opcode,
            operator_name=FASTAG_OPERATORS[opcode],
            vehicle_number=vehicle_number,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        # Inspay — vehicle number goes as 'number' field
        ok, response = initiate_recharge(
            opcode=opcode,
            number=vehicle_number,
            amount=amount,
            order_id=order_id
        )

        if not ok:
            fastag_txn.status = 'failure'
            fastag_txn.message = response.get('error', 'Unknown error')
            fastag_txn.save()
            return Response(
                {"error": "Fastag recharge failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        inspay_status = response.get('status', 'Pending')
        fastag_txn.inspay_txid = response.get('txid')
        fastag_txn.inspay_opid = response.get('opid')
        fastag_txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            fastag_txn.status = 'success'
        elif inspay_status == 'Failure':
            fastag_txn.status = 'failure'
        else:
            fastag_txn.status = 'pending'
            fastag_txn.save()

            import time
            time.sleep(3)

            status_ok, status_response = check_recharge_status(order_id)   # ← fixed, was check_fastag_status
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    fastag_txn.status = 'success'
                    fastag_txn.inspay_txid = status_response.get('txid', fastag_txn.inspay_txid)
                elif final_status == 'Failure':
                    fastag_txn.status = 'failure'
        fastag_txn.save()

        return Response(
            {
                "message": response.get('message'),
                "status": fastag_txn.status,
                "order_id": order_id,
                "txid": response.get('txid'),
                "vehicle_number": vehicle_number,
                "operator": FASTAG_OPERATORS[opcode],
                "amount": amount
            },
            status=status.HTTP_200_OK
        )


class FastagHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = FastagTransaction.objects.filter(
            user=request.user
        ).order_by('-created_at')

        data = [
            {
                "order_id": t.order_id,
                "vehicle_number": t.vehicle_number,
                "operator": t.operator_name,
                "amount": t.amount,
                "status": t.status,
                "message": t.message,
                "created_at": t.created_at,
            }
            for t in transactions
        ]
        return Response(data, status=status.HTTP_200_OK)

BROADBAND_OPERATORS = {
    '129': 'ACT Fibernet',
    '135': 'Hathway Broadband',
    '136': 'Connect Broadband',
    '137': 'SpectraNet Broadband',
    '284': 'Timbl Broadband',
    '305': 'Netplus Broadband',
    '519': 'Alliance Broadband',
    '523': 'AirJaldi Rural Broadband',
    '56': 'Tikona Infinet',
    '828': 'TATA PLAY FIBER',
    '28' : 'Airtel Broadband',
    '1574': 'Airtel Wi-Fi Recharge',
}

LPG_OPERATORS = {
    'BPCLGC': 'Bharat Gas (BPCL)',
    'HPCLGC': 'HP Gas (HPCL)',
    'IOCLGC': 'Indane Gas (Indian Oil)',
    'BPCLCGC': 'Bharat Gas Commercial',
}

WATER_BILLERS = {
    '70': 'Bangalore Water Supply (BWSSB)',
    '262': 'Delhi Jal Board',
    '298': 'Kerala Water Authority',
    '330': 'Municipal Corporation Chandigarh',
    '644': 'MCGM Water Department',
    '157': 'Pune Municipal Corporation Water',
    '232': 'Surat Municipal Corporation Water',
    '149': 'Uttarakhand Jal Sansthan',
}

INSURANCE_PROVIDERS = {
    '285': 'HDFC Life Insurance',
    '37': 'ICICI Prudential Life Insurance',
    '134': 'SBI Life Insurance',
    '42': 'TATA AIA Life Insurance',
    '239': 'Axis Max Life Insurance',
    '306': 'Care Health Insurance',
    '693': 'Star Health Insurance',
    '417': 'Niva Bupa Health Insurance',
    '537': 'Aditya Birla Health Insurance',
}


class BroadbandOperatorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            [{"code": k, "name": v} for k, v in BROADBAND_OPERATORS.items()],
            status=status.HTTP_200_OK
        )


class InitiateBroadbandRechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account_number = str(request.data.get('account_number', '')).strip()
        amount = request.data.get('amount')
        opcode = str(request.data.get('opcode', '')).strip()

        if not account_number or not amount or not opcode:
            return Response(
                {"error": "account_number, amount and opcode are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if opcode not in BROADBAND_OPERATORS:
            return Response(
                {"error": "Invalid broadband operator code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"error": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        order_id = f"BB{uuid.uuid4().hex[:12].upper()}"

        txn = BroadbandTransaction.objects.create(
            user=request.user,
            operator_code=opcode,
            operator_name=BROADBAND_OPERATORS[opcode],
            account_number=account_number,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        ok, response = initiate_recharge(
            opcode=opcode,
            number=account_number,
            amount=amount,
            order_id=order_id
        )

        if not ok:
            txn.status = 'failure'
            txn.message = response.get('error', 'Unknown error')
            txn.save()
            return Response({"error": "Broadband recharge failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        inspay_status = response.get('status', 'Pending')
        txn.inspay_txid = response.get('txid')
        txn.inspay_opid = response.get('opid')
        txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            txn.status = 'success'
        elif inspay_status == 'Failure':
            txn.status = 'failure'
        else:
            txn.status = 'pending'
            txn.save()

            import time
            time.sleep(3)

            status_ok, status_response = check_recharge_status(order_id)
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    txn.status = 'success'
                    txn.inspay_txid = status_response.get('txid', txn.inspay_txid)
                elif final_status == 'Failure':
                    txn.status = 'failure'
        txn.save()

        return Response({
            "message": response.get('message'),
            "status": txn.status,
            "order_id": order_id,
            "txid": response.get('txid'),
            "account_number": account_number,
            "operator": BROADBAND_OPERATORS[opcode],
            "amount": amount
        }, status=status.HTTP_200_OK)


class BroadbandHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = BroadbandTransaction.objects.filter(user=request.user).order_by('-created_at')
        return Response([{
            "order_id": t.order_id,
            "account_number": t.account_number,
            "operator": t.operator_name,
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at,
        } for t in transactions], status=status.HTTP_200_OK)


class LPGOperatorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            [{"code": k, "name": v} for k, v in LPG_OPERATORS.items()],
            status=status.HTTP_200_OK
        )


class InitiateLPGRechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        consumer_number = str(request.data.get('consumer_number', '')).strip()
        amount = request.data.get('amount')
        opcode = str(request.data.get('opcode', '')).strip()

        if not consumer_number or not amount or not opcode:
            return Response(
                {"error": "consumer_number, amount and opcode are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if opcode not in LPG_OPERATORS:
            return Response({"error": "Invalid LPG operator code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"error": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        order_id = f"LPG{uuid.uuid4().hex[:12].upper()}"

        txn = LPGTransaction.objects.create(
            user=request.user,
            operator_code=opcode,
            operator_name=LPG_OPERATORS[opcode],
            consumer_number=consumer_number,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        ok, response = initiate_recharge(
            opcode=opcode,
            number=consumer_number,
            amount=amount,
            order_id=order_id
        )

        if not ok:
            txn.status = 'failure'
            txn.message = response.get('error', 'Unknown error')
            txn.save()
            return Response({"error": "LPG recharge failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        inspay_status = response.get('status', 'Pending')
        txn.inspay_txid = response.get('txid')
        txn.inspay_opid = response.get('opid')
        txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            txn.status = 'success'
        elif inspay_status == 'Failure':
            txn.status = 'failure'
        else:
            txn.status = 'pending'
            txn.save()

            import time
            time.sleep(3)

            status_ok, status_response = check_recharge_status(order_id)
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    txn.status = 'success'
                    txn.inspay_txid = status_response.get('txid', txn.inspay_txid)
                elif final_status == 'Failure':
                    txn.status = 'failure'
        txn.save()

        return Response({
            "message": response.get('message'),
            "status": txn.status,
            "order_id": order_id,
            "txid": response.get('txid'),
            "consumer_number": consumer_number,
            "operator": LPG_OPERATORS[opcode],
            "amount": amount
        }, status=status.HTTP_200_OK)


class LPGHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = LPGTransaction.objects.filter(user=request.user).order_by('-created_at')
        return Response([{
            "order_id": t.order_id,
            "consumer_number": t.consumer_number,
            "operator": t.operator_name,
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at,
        } for t in transactions], status=status.HTTP_200_OK)


class WaterBillerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            [{"code": k, "name": v} for k, v in WATER_BILLERS.items()],
            status=status.HTTP_200_OK
        )


class PayWaterBillView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        consumer_number = str(request.data.get('consumer_number', '')).strip()
        biller_code = str(request.data.get('biller_code', '')).strip()
        amount = request.data.get('amount')
        mobile = str(request.data.get('mobile', request.user.phone)).strip()

        if not consumer_number or not biller_code or not amount:
            return Response(
                {"error": "consumer_number, biller_code and amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if biller_code not in WATER_BILLERS:
            return Response({"error": "Invalid biller code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"error": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        order_id = f"WT{uuid.uuid4().hex[:12].upper()}"

        txn = WaterTransaction.objects.create(
            user=request.user,
            biller_code=biller_code,
            biller_name=WATER_BILLERS[biller_code],
            consumer_number=consumer_number,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        ok, response = initiate_recharge(
            opcode=biller_code,
            number=consumer_number,
            amount=amount,
            order_id=order_id,
            value1=mobile
        )

        if not ok:
            txn.status = 'failure'
            txn.message = response.get('error', 'Unknown error')
            txn.save()
            return Response({"error": "Water bill payment failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        inspay_status = response.get('status', 'Pending')
        txn.inspay_txid = response.get('txid')
        txn.inspay_opid = response.get('opid')
        txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            txn.status = 'success'
        elif inspay_status == 'Failure':
            txn.status = 'failure'
        else:
            txn.status = 'pending'
            txn.save()

            import time
            time.sleep(3)

            status_ok, status_response = check_recharge_status(order_id)
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    txn.status = 'success'
                    txn.inspay_txid = status_response.get('txid', txn.inspay_txid)
                elif final_status == 'Failure':
                    txn.status = 'failure'
        txn.save()

        return Response({
            "message": response.get('message'),
            "status": txn.status,
            "order_id": order_id,
            "txid": response.get('txid'),
            "consumer_number": consumer_number,
            "biller": WATER_BILLERS[biller_code],
            "amount": amount
        }, status=status.HTTP_200_OK)


class WaterHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = WaterTransaction.objects.filter(user=request.user).order_by('-created_at')
        return Response([{
            "order_id": t.order_id,
            "consumer_number": t.consumer_number,
            "biller": t.biller_name,
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at,
        } for t in transactions], status=status.HTTP_200_OK)


class InsuranceProviderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            [{"code": k, "name": v} for k, v in INSURANCE_PROVIDERS.items()],
            status=status.HTTP_200_OK
        )


class PayInsurancePremiumView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        policy_number = str(request.data.get('policy_number', '')).strip()
        provider_code = str(request.data.get('provider_code', '')).strip()
        amount = request.data.get('amount')
        mobile = str(request.data.get('mobile', request.user.phone)).strip()

        if not policy_number or not provider_code or not amount:
            return Response(
                {"error": "policy_number, provider_code and amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if provider_code not in INSURANCE_PROVIDERS:
            return Response({"error": "Invalid provider code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"error": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        order_id = f"INS{uuid.uuid4().hex[:12].upper()}"

        txn = InsuranceTransaction.objects.create(
            user=request.user,
            provider_code=provider_code,
            provider_name=INSURANCE_PROVIDERS[provider_code],
            policy_number=policy_number,
            mobile=mobile,
            amount=amount,
            order_id=order_id,
            status='pending'
        )

        ok, response = initiate_recharge(
            opcode=provider_code,
            number=policy_number,
            amount=amount,
            order_id=order_id,
            value1=mobile
        )

        if not ok:
            txn.status = 'failure'
            txn.message = response.get('error', 'Unknown error')
            txn.save()
            return Response({"error": "Insurance payment failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        inspay_status = response.get('status', 'Pending')
        txn.inspay_txid = response.get('txid')
        txn.inspay_opid = response.get('opid')
        txn.message = response.get('message') or "Transaction failed. Please check details and try again."

        if inspay_status == 'Success':
            txn.status = 'success'
        elif inspay_status == 'Failure':
            txn.status = 'failure'
        else:
            txn.status = 'pending'
            txn.save()

            import time
            time.sleep(3)

            status_ok, status_response = check_recharge_status(order_id)
            if status_ok:
                final_status = status_response.get('status', 'Pending')
                if final_status == 'Success':
                    txn.status = 'success'
                    txn.inspay_txid = status_response.get('txid', txn.inspay_txid)
                elif final_status == 'Failure':
                    txn.status = 'failure'
        txn.save()

        return Response({
            "message": response.get('message'),
            "status": txn.status,
            "order_id": order_id,
            "txid": response.get('txid'),
            "policy_number": policy_number,
            "provider": INSURANCE_PROVIDERS[provider_code],
            "amount": amount
        }, status=status.HTTP_200_OK)


class InsuranceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = InsuranceTransaction.objects.filter(user=request.user).order_by('-created_at')
        return Response([{
            "order_id": t.order_id,
            "policy_number": t.policy_number,
            "provider": t.provider_name,
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at,
        } for t in transactions], status=status.HTTP_200_OK)

class DTHPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        opcode = request.query_params.get('opcode')
        category = request.query_params.get('category')

        plans = DTHPlan.objects.filter(is_active=True)

        if opcode:
            plans = plans.filter(operator_code=opcode)
        if category:
            plans = plans.filter(category=category)

        serializer = DTHPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)