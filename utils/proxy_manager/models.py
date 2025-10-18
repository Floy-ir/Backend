from django.db import models
import uuid


class Proxy(models.Model):
    """Model for storing proxy information"""
    uid = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    protocol = models.CharField(max_length=10, default="http", choices=[
        ("http", "HTTP"),
        ("https", "HTTPS"),
        ("socks4", "SOCKS4"),
        ("socks5", "SOCKS5"),
    ])
    country = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_enabled = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    success_rate = models.FloatField(default=0.0)
    response_time = models.FloatField(null=True, blank=True)
    failure_count = models.IntegerField(default=0)
    max_failures = models.IntegerField(default=5)
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-success_rate', '-created_at']

    def __str__(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy based on failure count and success rate"""
        return (
            self.is_active and 
            self.is_enabled and 
            self.failure_count < self.max_failures and
            self.success_rate > 0.3  # At least 30% success rate
        )

    def to_proxy_info(self):
        """Convert to ProxyInfo dataclass"""
        from .interfaces import ProxyInfo
        return ProxyInfo(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            protocol=self.protocol,
            country=self.country,
            is_active=self.is_active,
            last_used=self.last_used.timestamp() if self.last_used else None,
            success_rate=self.success_rate,
            response_time=self.response_time,
            failure_count=self.failure_count,
            max_failures=self.max_failures
        )


class ProxyUsageLog(models.Model):
    """Model for logging proxy usage"""
    proxy = models.ForeignKey(Proxy, on_delete=models.CASCADE, related_name="usage_logs")
    url = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.FloatField()
    success = models.BooleanField()
    error_message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.proxy} - {self.method} {self.url} - {self.status_code}"


class ProxyConfiguration(models.Model):
    """Model for proxy configuration settings"""
    name = models.CharField(max_length=100, unique=True)
    rotation_strategy = models.CharField(max_length=20, default="round_robin", choices=[
        ("round_robin", "Round Robin"),
        ("random", "Random"),
        ("least_used", "Least Used"),
        ("best_performance", "Best Performance"),
    ])
    max_concurrent_requests = models.IntegerField(default=10)
    health_check_interval = models.IntegerField(default=300)  # seconds
    failure_threshold = models.IntegerField(default=3)
    cooldown_period = models.IntegerField(default=60)  # seconds
    health_check_url = models.CharField(max_length=500, default="https://httpbin.org/ip")
    timeout = models.IntegerField(default=30)
    retry_count = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.rotation_strategy}"
