#!/usr/bin/env python3
"""
Proxy Discovery Script for Flight Crawler

This script helps you discover and set up public proxies for your flight crawler.
Run this script to automatically find and validate public proxies.

Usage:
    python discover_proxies.py
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runner.settings')
django.setup()

from utils.proxy_manager.public_proxy_scraper import PublicProxyScraper
from utils.proxy_manager.models import Proxy, ProxyConfiguration
from django.utils import timezone


def main():
    print("🚀 Starting Proxy Discovery for Flight Crawler")
    print("=" * 50)
    
    # Initialize scraper
    scraper = PublicProxyScraper()
    
    # Check if we have any existing proxies
    existing_count = Proxy.objects.count()
    print(f"📊 Existing proxies in database: {existing_count}")
    
    if existing_count > 0:
        active_count = Proxy.objects.filter(is_active=True, is_enabled=True).count()
        print(f"✅ Active proxies: {active_count}")
        
        if active_count >= 10:
            print("🎉 You already have enough active proxies!")
            print("You can start using the crawler with proxy support.")
            return
    
    print("\n🔍 Starting proxy discovery...")
    
    try:
        # Discover fresh proxies
        fresh_proxies = scraper.get_fresh_proxies(min_count=20)
        
        if not fresh_proxies:
            print("❌ No valid proxies found. This might be due to:")
            print("   - Network connectivity issues")
            print("   - Proxy sources being temporarily unavailable")
            print("   - All discovered proxies failing validation")
            return
        
        print(f"🎯 Found {len(fresh_proxies)} valid proxies")
        
        # Update database
        added_count = scraper.update_proxy_database(fresh_proxies)
        print(f"💾 Added {added_count} new proxies to database")
        
        # Show final statistics
        total_proxies = Proxy.objects.count()
        active_proxies = Proxy.objects.filter(is_active=True, is_enabled=True).count()
        
        print("\n📈 Final Statistics:")
        print(f"   Total proxies: {total_proxies}")
        print(f"   Active proxies: {active_proxies}")
        
        if active_proxies >= 5:
            print("\n🎉 Success! You now have enough proxies to start crawling.")
            print("Your flight crawler will automatically use these proxies to avoid IP bans.")
        else:
            print("\n⚠️  Warning: You have fewer than 5 active proxies.")
            print("Consider running this script again or checking proxy sources.")
        
        print("\n🔧 Next Steps:")
        print("1. Run your flight crawler - it will automatically use proxies")
        print("2. Monitor proxy performance in Django admin")
        print("3. Run 'python manage.py discover_proxies' periodically to refresh proxies")
        
    except Exception as e:
        print(f"❌ Error during proxy discovery: {e}")
        print("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
