import random
import time
import logging
import requests
from typing import List, Optional, Dict, Any
from django.utils import timezone
from django.db import transaction
from .models import Proxy, ProxyUsageLog, ProxyConfiguration
from .interfaces import (
    AbstractProxyManager, ProxyInfo, ProxyRequest, ProxyResponse,
    NoAvailableProxyException, ProxyHealthCheckFailedException,
    ProxyRotationException
)
from .public_proxy_scraper import PublicProxyScraper

logger = logging.getLogger(__name__)


class ProxyManagerService(AbstractProxyManager):
    """Service for managing proxy rotation and health checking"""

    def __init__(self, config_name: str = "default", auto_discover: bool = True):
        self.config = self._get_configuration(config_name)
        self._current_proxy_index = 0
        self._proxy_cache = []
        self._last_cache_update = 0
        self._cache_ttl = 60  # Cache proxies for 60 seconds
        self.auto_discover = auto_discover
        self.scraper = PublicProxyScraper()
        self._last_discovery = 0
        self._discovery_interval = 3600  # Discover new proxies every hour

    def _get_configuration(self, config_name: str) -> ProxyConfiguration:
        """Get proxy configuration"""
        try:
            return ProxyConfiguration.objects.get(name=config_name, is_active=True)
        except ProxyConfiguration.DoesNotExist:
            # Create default configuration if it doesn't exist
            return ProxyConfiguration.objects.create(
                name=config_name,
                rotation_strategy="round_robin"
            )

    def _get_healthy_proxies(self) -> List[Proxy]:
        """Get all healthy proxies from database"""
        proxies = list(Proxy.objects.filter(
            is_active=True,
            is_enabled=True,
            failure_count__lt=self.config.failure_threshold
        ).order_by('-success_rate', '-created_at'))
        
        # If we have very few proxies and auto-discovery is enabled, try to discover more
        if len(proxies) < 5 and self.auto_discover:
            self._try_auto_discovery()
            # Try again after discovery
            proxies = list(Proxy.objects.filter(
                is_active=True,
                is_enabled=True,
                failure_count__lt=self.config.failure_threshold
            ).order_by('-success_rate', '-created_at'))
        
        return proxies

    def _update_proxy_cache(self) -> None:
        """Update the proxy cache if needed"""
        current_time = time.time()
        if current_time - self._last_cache_update > self._cache_ttl:
            self._proxy_cache = self._get_healthy_proxies()
            self._last_cache_update = current_time

    def get_proxy(self, strategy: str = None) -> Optional[ProxyInfo]:
        """Get a proxy based on the specified strategy"""
        if strategy is None:
            strategy = self.config.rotation_strategy

        self._update_proxy_cache()
        
        if not self._proxy_cache:
            logger.warning("No healthy proxies available")
            # Try auto-discovery if enabled
            if self.auto_discover:
                self._try_auto_discovery()
                self._update_proxy_cache()
                if self._proxy_cache:
                    logger.info(f"Auto-discovery found {len(self._proxy_cache)} proxies")
                else:
                    logger.error("Auto-discovery failed to find any proxies")
            return None

        try:
            if strategy == "round_robin":
                proxy = self._get_round_robin_proxy()
            elif strategy == "random":
                proxy = self._get_random_proxy()
            elif strategy == "least_used":
                proxy = self._get_least_used_proxy()
            elif strategy == "best_performance":
                proxy = self._get_best_performance_proxy()
            else:
                proxy = self._get_round_robin_proxy()

            if proxy:
                return proxy.to_proxy_info()
            return None

        except Exception as e:
            logger.error(f"Error getting proxy with strategy {strategy}: {e}")
            raise ProxyRotationException(f"Failed to get proxy: {e}")

    def _get_round_robin_proxy(self) -> Optional[Proxy]:
        """Get proxy using round-robin strategy"""
        if not self._proxy_cache:
            return None
        
        proxy = self._proxy_cache[self._current_proxy_index]
        self._current_proxy_index = (self._current_proxy_index + 1) % len(self._proxy_cache)
        return proxy

    def _get_random_proxy(self) -> Optional[Proxy]:
        """Get proxy using random strategy"""
        if not self._proxy_cache:
            return None
        return random.choice(self._proxy_cache)

    def _get_least_used_proxy(self) -> Optional[Proxy]:
        """Get proxy with least usage"""
        if not self._proxy_cache:
            return None
        return min(self._proxy_cache, key=lambda p: p.total_requests)

    def _get_best_performance_proxy(self) -> Optional[Proxy]:
        """Get proxy with best performance (highest success rate, lowest response time)"""
        if not self._proxy_cache:
            return None
        
        def performance_score(proxy):
            success_score = proxy.success_rate
            time_score = 1.0 / (proxy.response_time or 1.0)
            return success_score * time_score

        return max(self._proxy_cache, key=performance_score)

    def make_request(self, request: ProxyRequest) -> ProxyResponse:
        """Make a request using proxy rotation"""
        max_retries = request.retry_count or self.config.retry_count
        last_error = None

        for attempt in range(max_retries):
            proxy_info = self.get_proxy()
            if not proxy_info:
                raise NoAvailableProxyException("No healthy proxies available")

            try:
                start_time = time.time()
                response = self._make_proxy_request(request, proxy_info)
                response_time = time.time() - start_time

                # Update proxy stats on success
                self.update_proxy_stats(
                    proxy_info=proxy_info,
                    success=True,
                    response_time=response_time,
                    request_url=request.url,
                    request_method=request.method,
                    status_code=response.status_code,
                    error_message=None
                )

                return ProxyResponse(
                    status_code=response.status_code,
                    content_bytes=response.content,
                    content_json=response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
                    proxy_used=proxy_info,
                    response_time=response_time
                )

            except Exception as e:
                logger.warning(f"Request failed with proxy {proxy_info.host}:{proxy_info.port} - {e}")
                last_error = e
                
                # Update proxy stats on failure
                self.update_proxy_stats(
                    proxy_info=proxy_info,
                    success=False,
                    response_time=0.0,
                    request_url=request.url,
                    request_method=request.method,
                    status_code=0,
                    error_message=str(e)
                )
                
                # If this is not the last attempt, continue to next proxy
                if attempt < max_retries - 1:
                    time.sleep(1)  # Brief delay before trying next proxy
                    continue

        # If all attempts failed
        raise ProxyRotationException(f"All proxy attempts failed. Last error: {last_error}")

    def _make_proxy_request(self, request: ProxyRequest, proxy_info: ProxyInfo) -> requests.Response:
        """Make a single request through a specific proxy"""
        proxy_url = f"{proxy_info.protocol}://"
        
        if proxy_info.username and proxy_info.password:
            proxy_url += f"{proxy_info.username}:{proxy_info.password}@"
        
        proxy_url += f"{proxy_info.host}:{proxy_info.port}"

        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        session = requests.Session()
        session.proxies.update(proxies)
        
        try:
            response = session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                json=request.json,
                timeout=request.timeout
            )
            return response
        finally:
            session.close()

    def update_proxy_stats(
        self,
        proxy_info: ProxyInfo,
        success: bool,
        response_time: float,
        request_url: str,
        request_method: str,
        status_code: int,
        error_message: Optional[str] = None
    ) -> None:
        """Update proxy statistics after a request"""
        try:
            with transaction.atomic():
                proxy = Proxy.objects.get(host=proxy_info.host, port=proxy_info.port)
                
                # Update basic stats
                proxy.total_requests += 1
                proxy.last_used = timezone.now()
                
                if success:
                    proxy.successful_requests += 1
                    proxy.failure_count = max(0, proxy.failure_count - 1)  # Reduce failure count on success
                    
                    # Update response time (moving average)
                    if proxy.response_time:
                        proxy.response_time = (proxy.response_time + response_time) / 2
                    else:
                        proxy.response_time = response_time
                else:
                    proxy.failure_count += 1
                
                # Calculate success rate
                proxy.success_rate = proxy.successful_requests / proxy.total_requests if proxy.total_requests > 0 else 0
                
                # Disable proxy if it exceeds max failures
                if proxy.failure_count >= proxy.max_failures:
                    proxy.is_enabled = False
                    logger.warning(f"Disabled proxy {proxy.host}:{proxy.port} due to excessive failures")
                
                proxy.save()
                
                # Log the usage
                ProxyUsageLog.objects.create(
                    proxy=proxy,
                    url=request_url,
                    method=request_method,
                    status_code=status_code if status_code is not None else (200 if success else 500),
                    response_time=response_time,
                    success=success,
                    error_message=error_message if not success else None
                )

        except Exception as e:
            logger.error(f"Error updating proxy stats: {e}")

    def health_check_proxy(self, proxy_info: ProxyInfo) -> bool:
        """Check if a proxy is healthy"""
        try:
            request = ProxyRequest(
                url=self.config.health_check_url,
                method="GET",
                timeout=10
            )
            
            response = self._make_proxy_request(request, proxy_info)
            is_healthy = response.status_code == 200
            
            # Update stats based on health check
            self.update_proxy_stats(
                proxy_info=proxy_info,
                success=is_healthy,
                response_time=response.elapsed.total_seconds(),
                request_url=request.url,
                request_method=request.method,
                status_code=response.status_code,
                error_message=None
            )
            
            return is_healthy

        except Exception as e:
            logger.warning(f"Health check failed for proxy {proxy_info.host}:{proxy_info.port}: {e}")
            self.update_proxy_stats(
                proxy_info=proxy_info,
                success=False,
                response_time=0.0,
                request_url=self.config.health_check_url,
                request_method="GET",
                status_code=0,
                error_message=str(e)
            )
            return False

    def get_all_proxies(self) -> List[ProxyInfo]:
        """Get all available proxies"""
        proxies = Proxy.objects.filter(is_active=True)
        return [proxy.to_proxy_info() for proxy in proxies]

    def add_proxy(self, proxy_info: ProxyInfo) -> None:
        """Add a new proxy to the pool"""
        try:
            Proxy.objects.create(
                host=proxy_info.host,
                port=proxy_info.port,
                username=proxy_info.username,
                password=proxy_info.password,
                protocol=proxy_info.protocol,
                country=proxy_info.country,
                is_active=proxy_info.is_active,
                max_failures=proxy_info.max_failures
            )
            logger.info(f"Added new proxy: {proxy_info.host}:{proxy_info.port}")
        except Exception as e:
            logger.error(f"Error adding proxy: {e}")
            raise

    def remove_proxy(self, proxy_id: str) -> None:
        """Remove a proxy from the pool"""
        try:
            proxy = Proxy.objects.get(uid=proxy_id)
            proxy.delete()
            logger.info(f"Removed proxy: {proxy.host}:{proxy.port}")
        except Proxy.DoesNotExist:
            logger.warning(f"Proxy with ID {proxy_id} not found")
        except Exception as e:
            logger.error(f"Error removing proxy: {e}")
            raise

    def disable_proxy(self, proxy_id: str) -> None:
        """Temporarily disable a proxy"""
        try:
            proxy = Proxy.objects.get(uid=proxy_id)
            proxy.is_enabled = False
            proxy.save()
            logger.info(f"Disabled proxy: {proxy.host}:{proxy.port}")
        except Proxy.DoesNotExist:
            logger.warning(f"Proxy with ID {proxy_id} not found")
        except Exception as e:
            logger.error(f"Error disabling proxy: {e}")
            raise

    def enable_proxy(self, proxy_id: str) -> None:
        """Re-enable a disabled proxy"""
        try:
            proxy = Proxy.objects.get(uid=proxy_id)
            proxy.is_enabled = True
            proxy.failure_count = 0  # Reset failure count when re-enabling
            proxy.save()
            logger.info(f"Enabled proxy: {proxy.host}:{proxy.port}")
        except Proxy.DoesNotExist:
            logger.warning(f"Proxy with ID {proxy_id} not found")
        except Exception as e:
            logger.error(f"Error enabling proxy: {e}")
            raise

    def run_health_checks(self) -> None:
        """Run health checks on all proxies"""
        logger.info("Starting proxy health checks")
        proxies = Proxy.objects.filter(is_active=True)
        
        for proxy in proxies:
            try:
                proxy_info = proxy.to_proxy_info()
                is_healthy = self.health_check_proxy(proxy_info)
                logger.info(f"Health check for {proxy.host}:{proxy.port}: {'PASSED' if is_healthy else 'FAILED'}")
            except Exception as e:
                logger.error(f"Error during health check for {proxy.host}:{proxy.port}: {e}")
        
        logger.info("Completed proxy health checks")

    def _try_auto_discovery(self) -> None:
        """Try to discover new proxies automatically"""
        current_time = time.time()
        
        # Only try discovery if enough time has passed since last attempt
        if current_time - self._last_discovery < self._discovery_interval:
            return
        
        self._last_discovery = current_time
        
        try:
            logger.info("Starting automatic proxy discovery")
            
            # Get fresh proxies
            fresh_proxies = self.scraper.get_fresh_proxies(min_count=10)
            
            if fresh_proxies:
                # Update database
                added_count = self.scraper.update_proxy_database(fresh_proxies)
                logger.info(f"Auto-discovery added {added_count} new proxies")
            else:
                logger.warning("Auto-discovery found no valid proxies")
                
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")

    def discover_proxies(self, min_count: int = 20) -> int:
        """Manually trigger proxy discovery"""
        try:
            logger.info("Starting manual proxy discovery")
            fresh_proxies = self.scraper.get_fresh_proxies(min_count=min_count)
            
            if fresh_proxies:
                added_count = self.scraper.update_proxy_database(fresh_proxies)
                logger.info(f"Manual discovery added {added_count} new proxies")
                return added_count
            else:
                logger.warning("Manual discovery found no valid proxies")
                return 0
                
        except Exception as e:
            logger.error(f"Manual discovery failed: {e}")
            return 0

    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        total_proxies = Proxy.objects.count()
        active_proxies = Proxy.objects.filter(is_active=True).count()
        enabled_proxies = Proxy.objects.filter(is_active=True, is_enabled=True).count()
        healthy_proxies = Proxy.objects.filter(
            is_active=True,
            is_enabled=True,
            failure_count__lt=self.config.failure_threshold
        ).count()
        
        return {
            'total_proxies': total_proxies,
            'active_proxies': active_proxies,
            'enabled_proxies': enabled_proxies,
            'healthy_proxies': healthy_proxies,
            'cache_size': len(self._proxy_cache),
            'last_discovery': self._last_discovery,
            'auto_discovery_enabled': self.auto_discover
        }
