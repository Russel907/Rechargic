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
from .models import RechargeTransaction, Operator, DTHTransaction, ElectricityTransaction, FastagTransaction

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
        recharge_txn.message = response.get('message')

        if inspay_status == 'Success':
            recharge_txn.status = 'success'
            # Points NOT awarded here — webhook confirms and awards
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
        dth_txn.message = response.get('message')

        if inspay_status == 'Success':
            dth_txn.status = 'success'
            award_recharge_points(request.user, amount)
        elif inspay_status == 'Failure':
            dth_txn.status = 'failure'
        else:
            dth_txn.status = 'pending'

        dth_txn.save()

        return Response(
            {
                "message": response.get('message'),
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
    """
    Step 1 — Fetch bill details before payment.
    Frontend calls this first to show user their bill amount.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        consumer_number = request.data.get('consumer_number')
        biller_code = request.data.get('biller_code')
        mobile = request.data.get('mobile', request.user.phone)

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

        # Temporary order ID for fetch — not used for payment
        fetch_order_id = f"EFETCH{uuid.uuid4().hex[:10].upper()}"

        ok, response = fetch_electricity_bill(
            opcode=biller_code,
            consumer_number=consumer_number,
            mobile=mobile,
            order_id=fetch_order_id
        )

        if not ok:
            return Response(
                {"error": "Could not fetch bill. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "biller_code": biller_code,
                "biller_name": ELECTRICITY_BILLERS[biller_code],
                "consumer_number": consumer_number,
                "customer_name": response.get('customerName'),
                "bill_amount": response.get('billAmount'),
                "due_date": response.get('dueDate'),
                "message": response.get('message'),
                "raw_status": response.get('status'),
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
        elec_txn.message = response.get('message')

        if inspay_status == 'Success':
            elec_txn.status = 'success'
            award_recharge_points(request.user, amount)
        elif inspay_status == 'Failure':
            elec_txn.status = 'failure'
        else:
            elec_txn.status = 'pending'

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
        fastag_txn.message = response.get('message')

        if inspay_status == 'Success':
            fastag_txn.status = 'success'
        elif inspay_status == 'Failure':
            fastag_txn.status = 'failure'
        else:
            fastag_txn.status = 'pending'

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