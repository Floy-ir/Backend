from django.contrib import admin
from .models import Website, WebsiteRoute

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_fa', 'uid', 'is_active', 'use_proxy', 'base_url')
    list_filter = ('is_active', 'use_proxy')
    search_fields = ('name', 'name_fa', 'uid')
    fieldsets = (
        ('Basic Information', {
            'fields': ('uid', 'name', 'name_fa', 'logo')
        }),
        ('Proxy Settings', {
            'fields': ('use_proxy',),
            'description': 'Enable proxy rotation for this website to avoid IP bans'
        }),
        ('URL Configuration', {
            'fields': ('base_url', 'redirect_url_template', 'one_adult_url_template', 'two_adult_url_template', 'redirect_url_config')
        }),
        ('Request Configuration', {
            'fields': ('request_payload_structure', 'response_parsing_rules')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

@admin.register(WebsiteRoute)
class WebsiteRouteAdmin(admin.ModelAdmin):
    list_display = ('website', 'origin', 'destination', 'is_supported')
    list_filter = ('website', 'is_supported')
    search_fields = ('origin', 'destination', 'website__name')
    raw_id_fields = ('website',)
