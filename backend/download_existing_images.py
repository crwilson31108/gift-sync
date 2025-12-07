#!/usr/bin/env python
"""
Simple script to download images for items that have image_url but no local image.
This will work on Railway because it just downloads from URLs (no scraping needed).
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

def download_existing_images():
    """Download images for items that have image_url"""

    # Get items with image_url but no local image
    items = WishListItem.objects.exclude(image_url='').filter(image='')

    print(f"\nFound {items.count()} items with image_url needing download")
    print("=" * 80)

    success_count = 0
    error_count = 0

    for i, item in enumerate(items, 1):
        print(f"\n[{i}/{items.count()}] {item.title}")
        print(f"  URL: {item.image_url[:80]}...")

        try:
            # Just re-save the item - this triggers the auto-download in save()
            item.save()

            # Check if image was downloaded
            if item.image:
                print(f"  ✓ Downloaded: {item.image.name}")
                success_count += 1
            else:
                print(f"  ✗ Download failed")
                error_count += 1

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            error_count += 1

    print("\n" + "=" * 80)
    print(f"\nDownload complete!")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {items.count()}")

if __name__ == '__main__':
    download_existing_images()
