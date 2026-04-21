from django.urls import path
from .views import (
    OperatorListView,
    CircleListView,
    PlanListView,
    InitiateRechargeView,
    RechargeStatusView,
    InspayBalanceView,
    RechargeHistoryView,
    ActivePlanView
)

urlpatterns = [
    path('operators/', OperatorListView.as_view(), name='operators'),
    path('circles/', CircleListView.as_view(), name='circles'),
    path('plans/', PlanListView.as_view(), name='plans'),
    path('initiate/', InitiateRechargeView.as_view(), name='initiate-recharge'),
    path('status/', RechargeStatusView.as_view(), name='recharge-status'),
    path('balance/', InspayBalanceView.as_view(), name='inspay-balance'),
    path('history/', RechargeHistoryView.as_view(), name='recharge-history'),
    path('active-plan/', ActivePlanView.as_view(), name='active-plan'),
]