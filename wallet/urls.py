from django.urls import path
from .views import WalletView, AddMoneyView, TransactionListView, WalletTransferView

urlpatterns = [
    path('', WalletView.as_view(), name='wallet'),
    path('add-money/', AddMoneyView.as_view(), name='add-money'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('transfer/', WalletTransferView.as_view(), name='wallet-transfer'),
]