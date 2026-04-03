from django.urls import path
from .views import OTTPlanListView, OTTSubscribeView, OTTCancelSubscriptionView

urlpatterns = [
    path('plans/', OTTPlanListView.as_view(), name='ott-plans'),
    path('subscribe/', OTTSubscribeView.as_view(), name='ott-subscribe'),
    path('cancel/', OTTCancelSubscriptionView.as_view(), name='ott-cancel'),
]