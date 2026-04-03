from django.urls import path
from .views import WalletView, AddMoneyView, TransactionListView

urlpatterns = [
    path('', WalletView.as_view(), name='wallet'),
    path('add-money/', AddMoneyView.as_view(), name='add-money'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
]