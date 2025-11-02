import abc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from libs.exceptions import ServiceExceptions


class ProxyInfo(BaseModel):
    """Data class representing proxy information"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"  # http, https, socks4, socks5
    country: Optional[str] = None
    is_active: bool = True
    last_used: Optional[float] = None
    success_rate: float = 0.0
    response_time: Optional[float] = None
    failure_count: int = 0
    max_failures: int = 5


class ProxyRotationStrategy(BaseModel):
    """Configuration for proxy rotation strategy"""
    strategy: str = "round_robin"  # round_robin, random, least_used, best_performance
    max_concurrent_requests: int = 10
    health_check_interval: int = 300  # seconds
    failure_threshold: int = 3
    cooldown_period: int = 60  # seconds


class ProxyRequest(BaseModel):
    """Request for proxy operations"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retry_count: int = 3


class ProxyResponse(BaseModel):
    """Response from proxy request"""
    status_code: int
    content_bytes: bytes = None
    content_json: object = None
    proxy_used: Optional[ProxyInfo] = None
    response_time: float = 0.0


class ProxyManagerBaseException(ServiceExceptions):
    pass


class NoAvailableProxyException(ProxyManagerBaseException):
    def __init__(self, message: str = "No available proxies"):
        super().__init__(message)


class ProxyHealthCheckFailedException(ProxyManagerBaseException):
    def __init__(self, proxy: ProxyInfo, message: str = "Proxy health check failed"):
        self.proxy = proxy
        super().__init__(message)


class ProxyRotationException(ProxyManagerBaseException):
    def __init__(self, message: str = "Proxy rotation failed"):
        super().__init__(message)


class AbstractProxyManager(abc.ABC):
    """Abstract interface for proxy management"""

    @abc.abstractmethod
    def get_proxy(self, strategy: str = "round_robin") -> Optional[ProxyInfo]:
        """Get a proxy based on the specified strategy"""
        pass

    @abc.abstractmethod
    def make_request(self, request: ProxyRequest) -> ProxyResponse:
        """Make a request using proxy rotation"""
        pass

    @abc.abstractmethod
    def update_proxy_stats(self, proxy: ProxyInfo, success: bool, response_time: float) -> None:
        """Update proxy statistics after a request"""
        pass

    @abc.abstractmethod
    def health_check_proxy(self, proxy: ProxyInfo) -> bool:
        """Check if a proxy is healthy"""
        pass

    @abc.abstractmethod
    def get_all_proxies(self) -> List[ProxyInfo]:
        """Get all available proxies"""
        pass

    @abc.abstractmethod
    def add_proxy(self, proxy: ProxyInfo) -> None:
        """Add a new proxy to the pool"""
        pass

    @abc.abstractmethod
    def remove_proxy(self, proxy_id: str) -> None:
        """Remove a proxy from the pool"""
        pass

    @abc.abstractmethod
    def disable_proxy(self, proxy_id: str) -> None:
        """Temporarily disable a proxy"""
        pass

    @abc.abstractmethod
    def enable_proxy(self, proxy_id: str) -> None:
        """Re-enable a disabled proxy"""
        pass
