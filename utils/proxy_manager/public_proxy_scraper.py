import requests
from requests.exceptions import RequestException, Timeout, ProxyError
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
                'name': 'Advanced-Name',
                'url': 'https://advanced.name/freeproxy/6900e3a291f04?type=https',
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
        
        self.timeout = 5  # Reduced timeout for faster testing
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
            logger.info(f"Fetching from URL: {source['url']}")
            print(f"\n🔍 Fetching from URL: {source['url']}")
            
            response = requests.get(
                source['url'], 
                timeout=30,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ProxyScraper/1.0)'}
            )
            response.raise_for_status()
            
            logger.info(f"Received {len(response.text)} characters from {source['name']}")
            print(f"✅ Received {len(response.text)} characters")
            
            # Show first 100 characters of response
            print(f"\n📝 First 100 characters of response:")
            print(f"  {response.text[:100]}...")
            
            proxies = []
            
            # Try to split by newline first, then by space
            text = response.text.strip()
            
            # Check if it's newline-separated
            if '\n' in text:
                lines = text.split('\n')
                print(f"📊 Response appears to be newline-separated")
            else:
                # Space-separated
                lines = text.split(' ')
                print(f"📊 Response appears to be space-separated")
            
            logger.info(f"Split into {len(lines)} potential proxy entries")
            print(f"📊 Split into {len(lines)} potential proxy entries")
            
            # Limit to first 1000 proxies
            max_proxies = 1000
            lines_to_process = lines[:max_proxies]
            print(f"📊 Processing first {len(lines_to_process)} entries\n")
            
            for line in lines_to_process:
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
            
            logger.info(f"Successfully parsed {len(proxies)} proxies from {source['name']}")
            print(f"✅ Successfully parsed {len(proxies)} proxies")
            
            # Show first 10 parsed proxies
            if proxies:
                print(f"\n📋 First 10 parsed proxies:")
                for i, proxy in enumerate(proxies[:10], 1):
                    print(f"  {i}. {proxy.host}:{proxy.port}")
            
            return proxies
            
        except Timeout:
            logger.error(f"Timeout while scraping from {source['name']}")
            return []
        except RequestException as e:
            logger.error(f"Request error while scraping from {source['name']}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error scraping from {source['name']}: {e}", exc_info=True)
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
        start_time = time.time()
        try:
            proxy_url = f"http://{proxy.host}:{proxy.port}"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test with HTTP first (many free proxies don't support HTTPS properly)
            test_url = 'http://httpbin.org/ip'
            
            try:
                response = requests.get(
                    test_url,
                    proxies=proxies,
                    timeout=self.timeout,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Additional check: make sure we're actually using the proxy
                    try:
                        response_data = response.json()
                        # Check if we got a valid IP response
                        if 'origin' in response_data:
                            print(f"    ✓ {proxy.host}:{proxy.port} - Valid (response time: {response_time:.2f}s) [IP: {response_data['origin']}]")
                            return True
                    except Exception as json_error:
                        # If JSON parsing fails, still consider it valid if status is 200
                        print(f"    ✓ {proxy.host}:{proxy.port} - Valid (response time: {response_time:.2f}s) [JSON error: {str(json_error)[:30]}]")
                        return True
                
                print(f"    ✗ {proxy.host}:{proxy.port} - Invalid (status: {response.status_code})")
                return False
                
            except requests.exceptions.Timeout:
                print(f"    ✗ {proxy.host}:{proxy.port} - Timeout (>5s)")
                return False
            except requests.exceptions.ProxyError as e:
                error_str = str(e)
                # Show the full error to understand what's happening
                if 'Max retries exceeded' in error_str:
                    # This usually means the proxy can't handle HTTPS
                    print(f"    ✗ {proxy.host}:{proxy.port} - Max retries exceeded (proxy may not support SSL/HTTPS)")
                elif 'ProxyError' in str(type(e)):
                    print(f"    ✗ {proxy.host}:{proxy.port} - Proxy error: {error_str[:80]}")
                else:
                    print(f"    ✗ {proxy.host}:{proxy.port} - Proxy error: {error_str[:80]}")
                return False
            except requests.exceptions.ConnectionError as e:
                error_msg = str(e)
                if 'timeout' in error_msg.lower():
                    print(f"    ✗ {proxy.host}:{proxy.port} - Connection timeout")
                elif 'refused' in error_msg.lower():
                    print(f"    ✗ {proxy.host}:{proxy.port} - Connection refused")
                else:
                    print(f"    ✗ {proxy.host}:{proxy.port} - Connection error: {error_msg[:80]}")
                return False
                
        except Exception as e:
            print(f"    ✗ {proxy.host}:{proxy.port} - Unexpected error: {str(e)[:80]}")
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
    
    def get_proxies_without_validation(self) -> List[ProxyInfo]:
        """Get proxies without validation - just scrape and return"""
        logger.info("Starting proxy scraping without validation")
        
        # Scrape proxies
        scraped_proxies = self.scrape_proxies()
        
        if not scraped_proxies:
            logger.warning("No proxies found from scraping")
            return []
        
        return scraped_proxies
    
    def get_valid_proxies_until_count(self, target_count: int = 50) -> List[ProxyInfo]:
        """Get proxies and validate until we find the target count of working proxies"""
        logger.info(f"Starting proxy scraping and validation (target: {target_count} working proxies)")
        
        # First, test internet connectivity without proxy
        print("\n🌐 Testing internet connectivity...")
        try:
            response = requests.get('http://httpbin.org/ip', timeout=5)
            print(f"✓ Internet connection OK - Direct IP: {response.json().get('origin', 'unknown')}")
        except Exception as e:
            print(f"⚠ Internet connection test failed: {e}")
            print("This may affect proxy validation.")
        
        # Scrape proxies
        scraped_proxies = self.scrape_proxies()
        
        if not scraped_proxies:
            logger.warning("No proxies found from scraping")
            return []
        
        print(f"\n🔍 Starting validation to find {target_count} working proxies...")
        print(f"📊 Testing {len(scraped_proxies)} proxies\n")
        print("=" * 70)
        
        valid_proxies = []
        tested = 0
        
        # Validate proxies one by one until we reach target count
        for proxy in scraped_proxies:
            tested += 1
            
            # Show progress every 5 proxies
            if tested % 5 == 0:
                print(f"\n📊 Progress: Tested {tested}/{len(scraped_proxies)}, Found {len(valid_proxies)}/{target_count} working proxies")
                print("-" * 70)
            
            print(f"  [{tested}] Testing {proxy.host}:{proxy.port}...")
            
            is_valid = self._validate_single_proxy(proxy)
            
            if is_valid:
                valid_proxies.append(proxy)
                print(f"\n\n🎉 Valid proxy #{len(valid_proxies)}/{target_count}: {proxy.host}:{proxy.port} ✓\n")
                
                if len(valid_proxies) >= target_count:
                    print("=" * 70)
                    print(f"\n🎉 SUCCESS: Found {len(valid_proxies)} working proxies! Stopping validation.\n")
                    break
        
        print("=" * 70)
        print(f"\n✅ Validation complete: {len(valid_proxies)} working proxies found out of {tested} tested\n")
        
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
