#!/usr/bin/env python
"""
Test scraper with the actual Etsy URL provided
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

# Disable Playwright for this test since it's having issues on ARM
os.environ['USE_PLAYWRIGHT'] = 'false'

url = "https://www.etsy.com/listing/1733015428/totk-resin-wood-night-light-christmas"

print(f"Testing URL: {url}\n")

scraper = ProductScraper(url)
data = scraper.scrape()

print("Results:")
print(json.dumps(data, indent=2))

print(f"\n\nSummary:")
print(f"Scrape Method: {data.get('scrape_method', 'unknown')}")
print(f"Title: {data.get('title', 'NOT FOUND')}")
print(f"Price: ${data.get('price', 'NOT FOUND')}")
print(f"Image: {data.get('image_url', 'NOT FOUND')[:80]}")
print(f"Has Error: {'Yes' if data.get('error') else 'No'}")
