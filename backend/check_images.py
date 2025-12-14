#!/usr/bin/env python3
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import WishListItem

# Search for items
print('Searching for items...\n')

# Try different search terms
peak = WishListItem.objects.filter(title__icontains='peak').first()
mobile = WishListItem.objects.filter(title__icontains='mobile').first()
wallet = WishListItem.objects.filter(title__icontains='wallet').first()
nano = WishListItem.objects.filter(title__icontains='nano').first()
bag = WishListItem.objects.filter(link__icontains='nanobag').first()
peakdesign = WishListItem.objects.filter(link__icontains='peakdesign').first()

items_to_check = []
if peak: items_to_check.append(('peak', peak))
if mobile: items_to_check.append(('mobile', mobile))
if wallet: items_to_check.append(('wallet', wallet))
if nano: items_to_check.append(('nano', nano))
if bag: items_to_check.append(('nanobag link', bag))
if peakdesign: items_to_check.append(('peakdesign link', peakdesign))

# Remove duplicates
seen_ids = set()
unique_items = []
for label, item in items_to_check:
    if item.id not in seen_ids:
        seen_ids.add(item.id)
        unique_items.append((label, item))

if unique_items:
    for label, item in unique_items:
        print(f'\n=== {item.title} (found via "{label}") ===')
        print(f'ID: {item.id}')
        print(f'Link: {item.link[:80] if item.link else "None"}...')
        print(f'Image (local): {item.image}')
        print(f'Image URL: {item.image_url[:80] if item.image_url else "None"}...')
        print(f'Has local image file: {bool(item.image)}')
        print(f'Has image URL: {bool(item.image_url)}')
else:
    print('No items found with those keywords')

# Get all recent items
print('\n\n=== Recent 10 items ===')
recent = WishListItem.objects.all().order_by('-created_at')[:10]
for item in recent:
    print(f'{item.id}: {item.title[:50]} | Image: {bool(item.image)} | URL: {bool(item.image_url)}')
