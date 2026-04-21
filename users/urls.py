from django.urls import path
from .views import SignupView, SendOTPView, VerifyOTPView, UserProfileView, LogoutView, DeleteAccountView, ReferralView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('referral/', ReferralView.as_view(), name='referral'),
]
