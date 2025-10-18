from django.contrib import admin
from django.utils.html import format_html
from .models import Proxy, ProxyUsageLog, ProxyConfiguration


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = [
        'host', 'port', 'protocol', 'country', 'is_active', 'is_enabled', 
        'success_rate', 'response_time', 'failure_count', 'total_requests',
        'last_used', 'health_status'
    ]
    list_filter = ['protocol', 'country', 'is_active', 'is_enabled']
    search_fields = ['host', 'country']
    readonly_fields = ['uid', 'success_rate', 'total_requests', 'successful_requests', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uid', 'host', 'port', 'protocol', 'country')
        }),
        ('Authentication', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_enabled', 'max_failures')
        }),
        ('Statistics', {
            'fields': ('success_rate', 'response_time', 'failure_count', 'total_requests', 'successful_requests', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def health_status(self, obj):
        """Display health status with color coding"""
        if obj.is_healthy:
            return format_html('<span style="color: green;">✓ Healthy</span>')
        else:
            return format_html('<span style="color: red;">✗ Unhealthy</span>')
    health_status.short_description = 'Health Status'

    actions = ['enable_proxies', 'disable_proxies', 'reset_failure_count']

    def enable_proxies(self, request, queryset):
        """Enable selected proxies"""
        updated = queryset.update(is_enabled=True, failure_count=0)
        self.message_user(request, f'{updated} proxies enabled successfully.')
    enable_proxies.short_description = "Enable selected proxies"

    def disable_proxies(self, request, queryset):
        """Disable selected proxies"""
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f'{updated} proxies disabled successfully.')
    disable_proxies.short_description = "Disable selected proxies"

    def reset_failure_count(self, request, queryset):
        """Reset failure count for selected proxies"""
        updated = queryset.update(failure_count=0)
        self.message_user(request, f'Failure count reset for {updated} proxies.')
    reset_failure_count.short_description = "Reset failure count"


@admin.register(ProxyUsageLog)
class ProxyUsageLogAdmin(admin.ModelAdmin):
    list_display = ['proxy', 'method', 'url_short', 'status_code', 'response_time', 'success', 'timestamp']
    list_filter = ['success', 'method', 'status_code', 'timestamp']
    search_fields = ['proxy__host', 'url']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def url_short(self, obj):
        """Display shortened URL"""
        return obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
    url_short.short_description = 'URL'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('proxy')


@admin.register(ProxyConfiguration)
class ProxyConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'rotation_strategy', 'max_concurrent_requests', 'health_check_interval', 'is_active']
    list_filter = ['rotation_strategy', 'is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('name', 'is_active')
        }),
        ('Rotation Strategy', {
            'fields': ('rotation_strategy', 'max_concurrent_requests')
        }),
        ('Health Check Settings', {
            'fields': ('health_check_interval', 'failure_threshold', 'cooldown_period', 'health_check_url')
        }),
        ('Request Settings', {
            'fields': ('timeout', 'retry_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
