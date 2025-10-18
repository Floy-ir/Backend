from django.core.management.base import BaseCommand
from django.utils import timezone
from utils.proxy_manager.public_proxy_scraper import PublicProxyScraper
from utils.proxy_manager.models import Proxy
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Discover and validate public proxies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-count',
            type=int,
            default=20,
            help='Minimum number of proxies to discover (default: 20)'
        )
        parser.add_argument(
            '--max-workers',
            type=int,
            default=50,
            help='Maximum number of workers for validation (default: 50)'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old inactive proxies'
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate existing proxies without scraping new ones'
        )

    def handle(self, *args, **options):
        scraper = PublicProxyScraper()
        
        if options['validate_only']:
            self.validate_existing_proxies(scraper)
        else:
            self.discover_new_proxies(scraper, options)
        
        if options['cleanup']:
            self.cleanup_old_proxies(scraper)

    def discover_new_proxies(self, scraper, options):
        """Discover and add new proxies"""
        self.stdout.write("Starting proxy discovery...")
        
        try:
            # Get fresh proxies
            fresh_proxies = scraper.get_fresh_proxies(min_count=options['min_count'])
            
            if not fresh_proxies:
                self.stdout.write(
                    self.style.WARNING("No valid proxies found")
                )
                return
            
            # Update database
            added_count = scraper.update_proxy_database(fresh_proxies)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully added {added_count} new proxies to the database"
                )
            )
            
            # Show statistics
            total_proxies = Proxy.objects.filter(is_active=True).count()
            enabled_proxies = Proxy.objects.filter(is_active=True, is_enabled=True).count()
            
            self.stdout.write(f"Total active proxies: {total_proxies}")
            self.stdout.write(f"Enabled proxies: {enabled_proxies}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during proxy discovery: {e}")
            )
            logger.error(f"Proxy discovery error: {e}")

    def validate_existing_proxies(self, scraper):
        """Validate existing proxies"""
        self.stdout.write("Validating existing proxies...")
        
        existing_proxies = Proxy.objects.filter(is_active=True)
        
        if not existing_proxies.exists():
            self.stdout.write(
                self.style.WARNING("No existing proxies to validate")
            )
            return
        
        # Convert to ProxyInfo objects
        from utils.proxy_manager.interfaces import ProxyInfo
        proxy_infos = [proxy.to_proxy_info() for proxy in existing_proxies]
        
        # Validate proxies
        valid_proxies = scraper.validate_proxies(proxy_infos)
        
        # Update database based on validation results
        valid_hosts = {f"{p.host}:{p.port}" for p in valid_proxies}
        
        updated_count = 0
        disabled_count = 0
        
        for proxy in existing_proxies:
            proxy_key = f"{proxy.host}:{proxy.port}"
            
            if proxy_key in valid_hosts:
                # Proxy is valid, reset failure count
                if proxy.failure_count > 0:
                    proxy.failure_count = 0
                    proxy.is_enabled = True
                    proxy.save()
                    updated_count += 1
            else:
                # Proxy is invalid, increment failure count
                proxy.failure_count += 1
                if proxy.failure_count >= proxy.max_failures:
                    proxy.is_enabled = False
                    disabled_count += 1
                proxy.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Validation complete: {len(valid_proxies)}/{len(existing_proxies)} proxies are valid"
            )
        )
        self.stdout.write(f"Updated proxies: {updated_count}")
        self.stdout.write(f"Disabled proxies: {disabled_count}")

    def cleanup_old_proxies(self, scraper):
        """Clean up old inactive proxies"""
        self.stdout.write("Cleaning up old proxies...")
        
        try:
            cleaned_count = scraper.cleanup_old_proxies()
            self.stdout.write(
                self.style.SUCCESS(f"Cleaned up {cleaned_count} old proxies")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during cleanup: {e}")
            )
