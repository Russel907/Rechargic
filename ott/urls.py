from django.urls import path
from .views import OTTPlanListView, OTTSubscribeView, OTTCancelSubscriptionView, OTTSubscriptionListView

urlpatterns = [
    path('plans/', OTTPlanListView.as_view(), name='ott-plans'),
    path('subscribe/', OTTSubscribeView.as_view(), name='ott-subscribe'),
    path('cancel/', OTTCancelSubscriptionView.as_view(), name='ott-cancel'),
    path('subscriptions/', OTTSubscriptionListView.as_view(), name='ott-subscriptions'),
]