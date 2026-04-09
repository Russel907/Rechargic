from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTP
from .serializers import SignupSerializer
from .utils import send_otp_via_messagecentral

OTP_TTL_SECONDS = 600       # 10 minutes
RESEND_COOLDOWN_SECONDS = 60  # 1 minute cooldown

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Account created successfully!", "phone": user.phone},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')

        if not phone:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not User.objects.filter(phone=phone).exists():
            return Response(
                {"error": "No account found with this phone number. Please signup first."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cooldown check
        last_otp = OTP.objects.filter(phone=phone, is_used=False).order_by('-created_at').first()
        if last_otp:
            seconds_passed = (timezone.now() - last_otp.created_at).total_seconds()
            if seconds_passed < RESEND_COOLDOWN_SECONDS:
                retry_after = int(RESEND_COOLDOWN_SECONDS - seconds_passed)
                return Response(
                    {"error": "Please wait before requesting another OTP.", "retry_after_seconds": retry_after},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        sms_text = "Your Rechargic verification code is <<< OTP >>>. It will expire in 10 minutes."

        # Send via MessageCentral — they generate the OTP
        ok, provider_resp = send_otp_via_messagecentral(phone, sms_text)
        if not ok:
            return Response(
                {"error": "Failed to send OTP. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Save OTP record with MessageCentral's verification ID
        otp_obj = OTP.objects.create(phone=phone, otp_code="mc_generated")

        data = provider_resp.get("data") if isinstance(provider_resp, dict) else None
        if data:
            otp_obj.provider_verification_id = data.get("verificationId")
            otp_obj.provider_transaction_id = data.get("transactionId")
            otp_obj.save()

        return Response(
            {
                "message": "OTP sent successfully to your phone number.",
                "expires_in": "10 minutes"
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        otp_code = request.data.get('otp')

        if not phone or not otp_code:
            return Response(
                {"error": "Phone and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get latest unused OTP for this phone
        try:
            otp = OTP.objects.filter(
                phone=phone,
                is_used=False
            ).latest('created_at')
        except OTP.DoesNotExist:
            return Response(
                {"error": "No OTP found. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        expiry_time = otp.created_at + timedelta(seconds=OTP_TTL_SECONDS)
        if timezone.now() > expiry_time:
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate OTP via MessageCentral
        from .utils import _get_auth_token
        from urllib.parse import urlencode
        import requests as req
        import os

        verification_id = otp.provider_verification_id
        if not verification_id:
            return Response(
                {"error": "Verification ID missing. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        country = os.environ.get("MESSAGECENTRAL_COUNTRY_CODE", "91")
        customer_id = os.environ.get("MESSAGECENTRAL_CUSTOMER_ID")
        base = os.environ.get("MESSAGECENTRAL_BASE", "https://cpaas.messagecentral.com")

        params = {
            "countryCode": country,
            "mobileNumber": phone,
            "verificationId": verification_id,
            "customerId": customer_id,
            "code": otp_code
        }
        validate_url = f"{base}/verification/v3/validateOtp?{urlencode(params)}"

        ok, token_or_err = _get_auth_token(country=country)
        if not ok:
            return Response(
                {"error": "Auth error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        headers = {"authToken": token_or_err, "Accept": "application/json"}

        try:
            resp = req.get(validate_url, headers=headers, timeout=10)
        except Exception:
            return Response(
                {"error": "Network error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            j = resp.json()
        except ValueError:
            j = {}

        if not (resp.status_code == 200 and j.get("message") == "SUCCESS"):
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Return JWT tokens — login success
        user = User.objects.get(phone=phone)
        tokens = get_tokens_for_user(user)

        return Response(
            {
                "message": "Login successful!",
                "name": user.name,
                "phone": user.phone,
                "tokens": tokens
            },
            status=status.HTTP_200_OK
        )

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "name": user.name,
                "phone": user.phone,
                "joined": user.created_at,
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        user = request.user
        name = request.data.get('name')
        
        if not name:
            return Response(
                {"error": "Name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.name = name
        user.save()
        
        return Response(
            {
                "message": "Profile updated successfully!",
                "name": user.name,
                "phone": user.phone,
            },
            status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully!"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {"message": "Account deleted successfully!"},
            status=status.HTTP_200_OK
        )