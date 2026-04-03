from django.contrib import admin
from .models import RewardPoints, RewardTransaction, RewardItem

admin.site.register(RewardPoints)
admin.site.register(RewardTransaction)
admin.site.register(RewardItem)