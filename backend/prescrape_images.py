#!/usr/bin/env python
"""
Pre-scrape all product URLs to extract actual image URLs.
This runs locally but connects to production database.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import WishListItem
from core.utils.scraper import ProductScraper

def prescrape_images():
    """Pre-scrape all product URLs to get actual image URLs"""

    # Get all items with a link but no image_url (need to scrape)
    items = WishListItem.objects.filter(
        link__isnull=False
    ).exclude(link='').filter(
        image_url__isnull=True
    ) | WishListItem.objects.filter(
        link__isnull=False
    ).exclude(link='').filter(image_url='')

    print(f"\nFound {items.count()} items with product links")
    print("=" * 80)

    success_count = 0
    error_count = 0

    for i, item in enumerate(items, 1):
        print(f"\n[{i}/{items.count()}] Processing: {item.title}")
        print(f"  URL: {item.link}")

        try:
            # Scrape the product page
            scraper = ProductScraper(item.link)
            scraped_data, error = scraper.scrape()

            if scraped_data and scraped_data.get('image_url'):
                image_url = scraped_data['image_url']
                print(f"  ✓ Found image: {image_url[:80]}...")

                # Update the item with the actual image URL
                item.image_url = image_url
                item.save(update_fields=['image_url'])

                success_count += 1
            else:
                print(f"  ✗ No image found")
                if error:
                    print(f"  Error: {error}")
                error_count += 1

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            error_count += 1

    print("\n" + "=" * 80)
    print(f"\nPre-scraping complete!")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {items.count()}")

if __name__ == '__main__':
    prescrape_images()
