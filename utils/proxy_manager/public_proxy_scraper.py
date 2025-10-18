import requests
import time
import logging
import random
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .interfaces import ProxyInfo
from .models import Proxy

logger = logging.getLogger(__name__)


class PublicProxyScraper:
    """Service for scraping and validating public proxies"""
    
    def __init__(self):
        self.proxy_sources = [
            {
                'name': 'FreeProxyList',
                'url': 'https://www.proxy-list.download/api/v1/get?type=http',
                'format': 'text',
                'separator': '\n'
            },
            {
                'name': 'ProxyScrape',
                'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'format': 'text',
                'separator': '\n'
            },
            {
                'name': 'ProxyList',
                'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'format': 'text',
                'separator': '\n'
            },
            {
                'name': 'FreeProxyAPI',
                'url': 'https://api.proxyscrape.com/?request=get&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all',
                'format': 'text',
                'separator': '\n'
            }
        ]
        
        self.test_urls = [
            'https://httpbin.org/ip',
            'https://api.ipify.org?format=json',
            'https://ipapi.co/json/',
            'https://api.myip.com'
        ]
        
        self.timeout = 10
        self.max_workers = 50

    def scrape_proxies(self) -> List[ProxyInfo]:
        """Scrape proxies from multiple sources"""
        all_proxies = []
        
        for source in self.proxy_sources:
            try:
                logger.info(f"Scraping proxies from {source['name']}")
                proxies = self._scrape_from_source(source)
                all_proxies.extend(proxies)
                logger.info(f"Found {len(proxies)} proxies from {source['name']}")
                
                # Add delay between requests to be respectful
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error scraping from {source['name']}: {e}")
                continue
        
        # Remove duplicates
        unique_proxies = self._remove_duplicates(all_proxies)
        logger.info(f"Total unique proxies found: {len(unique_proxies)}")
        
        return unique_proxies

    def _scrape_from_source(self, source: Dict[str, Any]) -> List[ProxyInfo]:
        """Scrape proxies from a single source"""
        try:
            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            
            proxies = []
            lines = response.text.strip().split(source['separator'])
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse proxy format (host:port)
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        host = parts[0].strip()
                        port = parts[1].strip()
                        
                        try:
                            port = int(port)
                            if 1 <= port <= 65535:
                                proxy = ProxyInfo(
                                    host=host,
                                    port=port,
                                    protocol='http',
                                    is_active=True,
                                    success_rate=0.0,
                                    failure_count=0,
                                    max_failures=3
                                )
                                proxies.append(proxy)
                        except ValueError:
                            continue
            
            return proxies
            
        except Exception as e:
            logger.error(f"Error scraping from {source['name']}: {e}")
            return []

    def _remove_duplicates(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicate proxies based on host:port"""
        seen = set()
        unique_proxies = []
        
        for proxy in proxies:
            key = f"{proxy.host}:{proxy.port}"
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        return unique_proxies

    def validate_proxies(self, proxies: List[ProxyInfo], max_workers: int = None) -> List[ProxyInfo]:
        """Validate proxies by testing them"""
        if max_workers is None:
            max_workers = self.max_workers
            
        valid_proxies = []
        
        logger.info(f"Starting validation of {len(proxies)} proxies with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all validation tasks
            future_to_proxy = {
                executor.submit(self._validate_single_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            # Process completed tasks
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_valid = future.result()
                    if is_valid:
                        valid_proxies.append(proxy)
                        logger.debug(f"Valid proxy: {proxy.host}:{proxy.port}")
                except Exception as e:
                    logger.debug(f"Error validating proxy {proxy.host}:{proxy.port}: {e}")
        
        logger.info(f"Validation complete: {len(valid_proxies)}/{len(proxies)} proxies are valid")
        return valid_proxies

    def _validate_single_proxy(self, proxy: ProxyInfo) -> bool:
        """Validate a single proxy"""
        try:
            proxy_url = f"http://{proxy.host}:{proxy.port}"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test with a simple request
            test_url = random.choice(self.test_urls)
            
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            if response.status_code == 200:
                # Additional check: make sure we're actually using the proxy
                try:
                    response_data = response.json()
                    if 'origin' in response_data or 'ip' in response_data:
                        return True
                except:
                    # If JSON parsing fails, still consider it valid if status is 200
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Proxy validation failed for {proxy.host}:{proxy.port}: {e}")
            return False

    def get_fresh_proxies(self, min_count: int = 10) -> List[ProxyInfo]:
        """Get fresh proxies by scraping and validating"""
        logger.info("Starting fresh proxy discovery")
        
        # Scrape proxies
        scraped_proxies = self.scrape_proxies()
        
        if not scraped_proxies:
            logger.warning("No proxies found from scraping")
            return []
        
        # Validate proxies
        valid_proxies = self.validate_proxies(scraped_proxies)
        
        if len(valid_proxies) < min_count:
            logger.warning(f"Only {len(valid_proxies)} valid proxies found, minimum required: {min_count}")
        
        return valid_proxies

    def update_proxy_database(self, proxies: List[ProxyInfo]) -> int:
        """Update the database with new proxies"""
        added_count = 0
        
        for proxy_info in proxies:
            try:
                # Check if proxy already exists
                existing_proxy = Proxy.objects.filter(
                    host=proxy_info.host,
                    port=proxy_info.port
                ).first()
                
                if existing_proxy:
                    # Update existing proxy
                    existing_proxy.is_active = True
                    existing_proxy.is_enabled = True
                    existing_proxy.failure_count = 0
                    existing_proxy.save()
                    logger.debug(f"Updated existing proxy: {proxy_info.host}:{proxy_info.port}")
                else:
                    # Create new proxy
                    Proxy.objects.create(
                        host=proxy_info.host,
                        port=proxy_info.port,
                        protocol=proxy_info.protocol,
                        is_active=proxy_info.is_active,
                        is_enabled=True,
                        max_failures=proxy_info.max_failures,
                        success_rate=0.0,
                        failure_count=0
                    )
                    added_count += 1
                    logger.debug(f"Added new proxy: {proxy_info.host}:{proxy_info.port}")
                    
            except Exception as e:
                logger.error(f"Error updating proxy {proxy_info.host}:{proxy_info.port}: {e}")
                continue
        
        logger.info(f"Updated database with {added_count} new proxies")
        return added_count

    def cleanup_old_proxies(self, max_age_hours: int = 24) -> int:
        """Remove old inactive proxies"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=max_age_hours)
        
        old_proxies = Proxy.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_time
        )
        
        count = old_proxies.count()
        old_proxies.delete()
        
        logger.info(f"Cleaned up {count} old inactive proxies")
        return count
