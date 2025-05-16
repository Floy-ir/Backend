from django.contrib import admin
from .models import Statistic

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('uid', 'provider', 'redirect_number')