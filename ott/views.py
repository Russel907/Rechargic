import chargebee
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class OTTPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            result = chargebee.Plan.list({
                "status[is]": "active"
            })
            plans = []
            for entry in result:
                plan = entry.plan
                plans.append({
                    "id": plan.id,
                    "name": plan.name,
                    "price": plan.price / 100,  # Chargebee stores in paise
                    "period": plan.period,
                    "period_unit": plan.period_unit,
                    "description": plan.description,
                })
            return Response(plans, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OTTSubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')

        if not plan_id:
            return Response(
                {"error": "plan_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = request.user

            # Create or get customer in Chargebee
            result = chargebee.Subscription.create({
                "plan_id": plan_id,
                "customer": {
                    "first_name": user.name,
                    "phone": user.phone,
                    "email": f"{user.phone}@rechargic.in"
                }
            })

            subscription = result.subscription
            customer = result.customer

            return Response(
                {
                    "message": "Subscribed successfully!",
                    "subscription_id": subscription.id,
                    "plan_id": subscription.plan_id,
                    "status": subscription.status,
                    "current_term_end": subscription.current_term_end,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OTTCancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription_id = request.data.get('subscription_id')

        if not subscription_id:
            return Response(
                {"error": "subscription_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = chargebee.Subscription.cancel(subscription_id, {
                "end_of_term": True
            })
            subscription = result.subscription

            return Response(
                {
                    "message": "Subscription cancelled successfully!",
                    "subscription_id": subscription.id,
                    "status": subscription.status,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OTTSubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            # Search Chargebee subscriptions by phone
            result = chargebee.Subscription.list({
                "customer_id[is]": user.phone
            })

            subscriptions = []
            for entry in result:
                sub = entry.subscription
                subscriptions.append({
                    "subscription_id": sub.id,
                    "plan_id": sub.plan_id,
                    "status": sub.status,
                    "current_term_start": sub.current_term_start,
                    "current_term_end": sub.current_term_end,
                    "next_billing_at": sub.next_billing_at,
                })

            return Response(subscriptions, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )