from django.contrib import admin
from .models import Airline


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'image')
    search_fields = ('name', 'uid')
    list_filter = ('name',)
    ordering = ('name',)
