
from django.contrib import admin
from .models import Operator, Circle, Plan, RechargeTransaction

admin.site.register(Operator)
admin.site.register(Circle)
admin.site.register(Plan)
admin.site.register(RechargeTransaction)