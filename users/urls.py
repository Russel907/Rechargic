from django.urls import path
from .views import SignupView, SendOTPView, VerifyOTPView, UserProfileView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
