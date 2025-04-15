from django.contrib import admin
from .models import Website, WebsiteRoute

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_fa', 'uid', 'is_active', 'base_url')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_fa', 'uid')
    readonly_fields = ('uid',)

@admin.register(WebsiteRoute)
class WebsiteRouteAdmin(admin.ModelAdmin):
    list_display = ('website', 'origin', 'destination', 'is_supported')
    list_filter = ('website', 'is_supported')
    search_fields = ('origin', 'destination', 'website__name')
    raw_id_fields = ('website',)
