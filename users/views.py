from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
import re
from .models import User, OTP
from .serializers import SignupSerializer
from .utils import send_otp_via_messagecentral

OTP_TTL_SECONDS = 300          # OTP valid for 10 mins
RESEND_COOLDOWN_SECONDS = 60   # Wait 60s before resend
MAX_OTP_ATTEMPTS = 5           # 🔒 Max wrong tries per OTP
MAX_OTP_PER_DAY = 20        # high for testing  - change to 5 while production        # 🔒 Max OTPs a phone can request per day
LOCKOUT_DURATION_MINUTES = 2  # change to 30 before going live


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')

        if not phone:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not re.match(r'^\d{10}$', str(phone)):
            return Response(
                {"error": "Phone number must be exactly 10 digits."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔒 Check if account is locked
        user = User.objects.filter(phone=phone).first()
        if user and user.is_locked():
            seconds_left = int((user.locked_until - timezone.now()).total_seconds())
            return Response(
                {
                    "error": "Account temporarily locked due to too many failed attempts.",
                    "retry_after_seconds": seconds_left
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # 🔒 Daily OTP request cap — max 5 OTPs per phone per day
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        todays_otp_count = OTP.objects.filter(
            phone=phone,
            created_at__gte=today_start
        ).count()

        if todays_otp_count >= MAX_OTP_PER_DAY:
            return Response(
                {"error": "Too many OTP requests today. Please try again tomorrow."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Resend cooldown check (already existed)
        last_otp = OTP.objects.filter(
            phone=phone,
            is_used=False,
            is_expired=False
        ).order_by('-created_at').first()

        if last_otp:
            seconds_passed = (timezone.now() - last_otp.created_at).total_seconds()
            if seconds_passed < RESEND_COOLDOWN_SECONDS:
                retry_after = int(RESEND_COOLDOWN_SECONDS - seconds_passed)
                return Response(
                    {
                        "error": "Please wait before requesting another OTP.",
                        "retry_after_seconds": retry_after
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # 🔒 Mark old unused OTP as expired before sending a new one
            last_otp.is_expired = True
            last_otp.save()

        sms_text = "Your Rechargic verification code is <<< OTP >>>. It will expire in 5 minutes."

        ok, provider_resp = send_otp_via_messagecentral(phone, sms_text)
        if not ok:
            return Response(
                {"error": "Failed to send OTP. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        otp_obj = OTP.objects.create(phone=phone, otp_code="mc_generated")

        data = provider_resp.get("data") if isinstance(provider_resp, dict) else None
        if data:
            otp_obj.provider_verification_id = data.get("verificationId")
            otp_obj.provider_transaction_id = data.get("transactionId")
            otp_obj.save()

        return Response(
            {
                "message": "OTP sent successfully.",
                "expires_in": "5 minutes"
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

        # 🔒 Check account lockout
        user = User.objects.filter(phone=phone).first()
        if user and user.is_locked():
            seconds_left = int((user.locked_until - timezone.now()).total_seconds())
            return Response(
                {
                    "error": "Account temporarily locked. Too many failed attempts.",
                    "retry_after_seconds": seconds_left
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            otp = OTP.objects.filter(
                phone=phone,
                is_used=False,
                is_expired=False
            ).latest('created_at')
        except OTP.DoesNotExist:
            return Response(
                {"error": "No OTP found. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        expiry_time = otp.created_at + timedelta(seconds=OTP_TTL_SECONDS)
        if timezone.now() > expiry_time:
            otp.is_expired = True
            otp.save()
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔒 Check max verify attempts on this OTP
        if otp.attempts >= MAX_OTP_ATTEMPTS:
            otp.is_expired = True
            otp.save()
            return Response(
                {"error": "Too many attempts. Please request a new OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # 🔒 Increment attempt counter BEFORE calling provider
        otp.attempts += 1
        otp.save()

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
            # 🔒 Track failed attempts and lock if needed
            if user:
                user.failed_otp_attempts += 1
                if user.failed_otp_attempts >= MAX_OTP_ATTEMPTS:
                    user.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    user.failed_otp_attempts = 0  # reset after lock
                user.save()

            attempts_left = MAX_OTP_ATTEMPTS - otp.attempts
            return Response(
                {
                    "error": "Invalid OTP. Please try again.",
                    "attempts_remaining": max(attempts_left, 0)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ OTP is correct — reset failure counters
        otp.is_used = True
        otp.save()

        if user:
            user.failed_otp_attempts = 0
            user.locked_until = None
            user.save()

        # Check if user exists
        user_exists = User.objects.filter(phone=phone).exists()

        if user_exists:
            user = User.objects.get(phone=phone)
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "message": "Login successful!",
                    "is_new_user": False,
                    "name": user.name,
                    "phone": user.phone,
                    "tokens": tokens
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "message": "OTP verified. Please enter your name to complete registration.",
                    "is_new_user": True,
                    "phone": phone,
                },
                status=status.HTTP_200_OK
            )


# --- All other views unchanged below ---

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "message": "Account created successfully!",
                    "is_new_user": True,
                    "name": user.name,
                    "phone": user.phone,
                    "tokens": tokens
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "name": user.name,
                "phone": user.phone,
                "joined": user.created_at,
                "referral_code": user.referral_code,
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        user = request.user
        name = request.data.get('name')
        if not name:
            return Response({"error": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)
        user.name = name
        user.save()
        return Response({"message": "Profile updated successfully!", "name": user.name, "phone": user.phone})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully!"})
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deleted successfully!"})


class ReferralView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        referrals = User.objects.filter(referred_by=user)
        return Response(
            {
                "referral_code": user.referral_code,
                "referral_link": f"https://rechargic.vercel.app/signup?ref={user.referral_code}",
                "total_referrals": referrals.count(),
                "referrals": [
                    {"name": r.name, "phone": r.phone, "joined": r.created_at}
                    for r in referrals
                ]
            }
        )