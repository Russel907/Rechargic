from django.urls import path
from .views import OfferListView, RedeemOfferView

urlpatterns = [
    path('', OfferListView.as_view(), name='offers'),
    path('redeem/', RedeemOfferView.as_view(), name='redeem-offer'),
]