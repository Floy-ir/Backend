import requests
import logging
from typing import List, Optional, Tuple
import time
from utils.date_time import interfaces as date_time_interfaces


logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self, 
            proxy_list_url: str = "http://pubproxy.com/api/proxy",
            date_time: date_time_interfaces.AbstractDateTime
            ):
        self.proxy_list_url = proxy_list_url
        self.proxies: List[Tuple[str, float]] = []  # List of (proxy_url, speed) tuples
        self.last_fetch_time = 0
        self.fetch_interval = 60 * 60  # 60 minutes
        self.test_urls = [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://www.amazon.com"
        ]
        self.date_time = date_time

    def _fetch_proxies(self) -> List[Tuple[str, float]]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Accept-Encoding": "gzip, deflate, br"
            }

            proxies = []
            response = requests.get(self.proxy_list_url, headers=headers, timeout=10)
            response_json = response.json()

            if response_json.get('status') == 'success':
                proxy_data = response_json.get('data', [])
                for proxy in proxy_data:
                    ip = proxy.get('ip')
                    port = proxy.get('port')
                    speed = proxy.get('speed', float('inf'))  # Get speed from API, default to infinity if not available
                    if ip and port:
                        proxy_url = f"http://{ip}:{port}"
                        proxies.append((proxy_url, speed))

            # Sort proxies by speed (faster first)
            proxies.sort(key=lambda x: x[1])
            logger.info(f"Fetched {len(proxies)} proxies, sorted by speed")
            self.last_fetch_time = time.time()
            return proxies

        except Exception as e:
            logger.error(f"Error fetching proxies: {str(e)}")
            return []

    def _is_proxy_working(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        try:
            test_url = "https://www.google.com"
            response = requests.get(
                test_url,
                proxies={'http': proxy, 'https': proxy},
                timeout=10,
                verify=False
            )
            return response.status_code == 200
        except:
            return False

    def get_proxy(self) -> Optional[str]:
        """Get a working proxy, preferring faster ones"""
        current_time = time.time()
        if not self.proxies or (current_time - self.last_fetch_time) > self.fetch_interval:
            self.proxies = self._fetch_proxies()

        if not self.proxies:
            return None

        # Try proxies in order of speed (fastest first)
        for proxy, speed in self.proxies[:3]:  # Try top 3 fastest proxies
            if self._is_proxy_working(proxy):
                logger.info(f"Using proxy with speed: {speed}ms")
                return proxy
            self.proxies.remove((proxy, speed))

        return None

    def remove_proxy(self, proxy: str) -> None:
        """Remove a proxy from the list"""
        self.proxies = [(p, s) for p, s in self.proxies if p != proxy]
