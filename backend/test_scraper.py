#!/usr/bin/env python
"""
Test script for the enhanced product scraper
Tests against major e-commerce sites
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.utils.scraper import ProductScraper
import json

# Test URLs for major e-commerce sites
TEST_URLS = {
    'Amazon': 'https://www.amazon.com/dp/B0BSHF7WHW',  # Example product
    'Etsy': 'https://www.etsy.com/listing/1234567890',  # Will likely fail but tests error handling
    'Best Buy': 'https://www.bestbuy.com/site/example',  # Will test fallback
}

def test_url(name, url):
    """Test a single URL and print results"""
    print(f"\n{'='*60}")
    print(f"Testing {name}: {url}")
    print(f"{'='*60}")

    try:
        scraper = ProductScraper(url)
        data = scraper.scrape()

        print(f"\nScrape Method: {data.get('scrape_method', 'unknown')}")
        print(f"Title: {data.get('title', 'NOT FOUND')[:100]}")
        print(f"Price: ${data.get('price', 'NOT FOUND')}")
        print(f"Image URL: {data.get('image_url', 'NOT FOUND')[:100]}")
        print(f"Description: {data.get('description', 'NOT FOUND')[:100] if data.get('description') else 'NOT FOUND'}")
        print(f"Images Found: {len(data.get('all_images', []))}")

        if data.get('error'):
            print(f"\nError: {data['error']}")

        # Determine success
        has_data = bool(data.get('title') or data.get('price'))
        status = "✓ SUCCESS" if has_data else "✗ FAILED"
        print(f"\nStatus: {status}")

        return has_data

    except Exception as e:
        print(f"\n✗ EXCEPTION: {str(e)}")
        return False

def main():
    print("="*60)
    print("Product Scraper Test Suite")
    print("="*60)

    results = {}

    # Test each URL
    for name, url in TEST_URLS.items():
        success = test_url(name, url)
        results[name] = success

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    total = len(results)
    passed = sum(results.values())

    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Test with a simple known-good URL
    print(f"\n{'='*60}")
    print("Testing with a simple generic page")
    print(f"{'='*60}")

    # Example.com won't have product data but should handle gracefully
    test_url("Generic Page", "https://example.com")

if __name__ == '__main__':
    main()
