#!/usr/bin/env python3
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.utils.scraper import ProductScraper

# Test URLs
urls = [
    'https://www.peakdesign.com/products/mobile-wallet?Style=Slim+Wallet&Color=Charcoal&Material=Fabric',
    'https://nanobag.com/products/reusable-shopping-bags?variant=44547901653128'
]

for url in urls:
    print(f'\n{"="*80}')
    print(f'Testing: {url}')
    print(f'{"="*80}')

    try:
        scraper = ProductScraper(url)
        data = scraper.scrape()

        print(f'\nTitle: {data.get("title")}')
        print(f'Price: {data.get("price")}')
        print(f'Description: {data.get("description", "")[:100]}...')
        print(f'Image URL: {data.get("image_url")}')
        print(f'All images count: {len(data.get("all_images", []))}')
        print(f'Scrape method: {data.get("scrape_method")}')

        if data.get('error'):
            print(f'Error: {data.get("error")}')

    except Exception as e:
        print(f'Exception: {str(e)}')
        import traceback
        traceback.print_exc()
