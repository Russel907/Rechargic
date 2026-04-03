from django.urls import path
from .views import RewardPointsView, RewardItemListView, RedeemRewardView

urlpatterns = [
    path('', RewardPointsView.as_view(), name='rewards'),
    path('items/', RewardItemListView.as_view(), name='reward-items'),
    path('redeem/', RedeemRewardView.as_view(), name='redeem-reward'),
]