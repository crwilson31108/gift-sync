#!/usr/bin/env python3
"""
Script to download missing images for specific wishlist items.
Run this on Railway to download images to the production volume.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import WishListItem
from core.utils.image_downloader import download_image_from_url

# Items that need images
ITEMS_TO_FIX = [
    {
        'id': 60,
        'name': 'Peak Design mobile wallet',
        'image_url': 'https://cdn.shopify.com/s/files/1/2986/1172/files/slimwallet-sage-v2-00000_1ef9cf99-c9f0-4c2b-ad57-4c2e04b431c9.jpg'
    },
    {
        'id': 61,
        'name': 'Nanobag',
        'image_url': 'https://nanobag.com/cdn/shop/files/NanobagAmazon7th_grande.jpg'
    }
]

def fix_images():
    print("Fixing missing images for wishlist items...")
    print("=" * 80)

    for item_info in ITEMS_TO_FIX:
        item_id = item_info['id']
        name = item_info['name']
        image_url = item_info['image_url']

        print(f"\n[Item {item_id}] {name}")
        print(f"Image URL: {image_url[:80]}...")

        try:
            item = WishListItem.objects.get(id=item_id)

            # Check if already has image
            if item.image:
                print(f"✓ Already has image: {item.image.name}")
                continue

            # Set the image_url if not set
            if not item.image_url:
                item.image_url = image_url
                item.save()
                print(f"  Set image_url field")

            # Download and save
            print(f"  Downloading image...")
            content_file, filename = download_image_from_url(image_url)
            item.image.save(filename, content_file, save=True)

            # Clear image_url after successful download
            item.image_url = ''
            item.save()

            print(f"✓ Downloaded successfully: {item.image.name}")

        except WishListItem.DoesNotExist:
            print(f"✗ Item {item_id} not found in database")
        except Exception as e:
            print(f"✗ Error: {str(e)}")

    print("\n" + "=" * 80)
    print("Done!")

    # Verify
    print("\nVerification:")
    for item_info in ITEMS_TO_FIX:
        try:
            item = WishListItem.objects.get(id=item_info['id'])
            has_image = bool(item.image)
            print(f"  Item {item_info['id']}: {'✓' if has_image else '✗'} Image stored: {has_image}")
            if has_image:
                print(f"    Path: {item.image.name}")
                print(f"    URL: {item.image.url}")
        except WishListItem.DoesNotExist:
            print(f"  Item {item_info['id']}: ✗ Not found")

if __name__ == '__main__':
    fix_images()
