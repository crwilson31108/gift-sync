from django.core.management.base import BaseCommand
from core.models import WishListItem
from core.utils.image_downloader import download_image_from_url, ImageDownloadException
from core.utils.scraper import ProductScraper
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download and save local copies of all wishlist item images from image_url'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-download images even if local copy exists',
        )
        parser.add_argument(
            '--rescrape',
            action='store_true',
            help='Re-scrape product pages if image download fails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        rescrape = options['rescrape']

        # Find all items with image_url
        if force:
            items = WishListItem.objects.filter(image_url__isnull=False).exclude(image_url='')
            self.stdout.write(f"Found {items.count()} items with image_url (force mode)")
        else:
            # Only items with image_url but no local image
            items = WishListItem.objects.filter(
                image_url__isnull=False
            ).exclude(
                image_url=''
            ).filter(
                image__isnull=True
            ) | WishListItem.objects.filter(
                image_url__isnull=False
            ).exclude(
                image_url=''
            ).filter(
                image=''
            )
            self.stdout.write(f"Found {items.count()} items with image_url but no local image")

        if rescrape:
            self.stdout.write(self.style.WARNING('Rescrape mode enabled - will re-scrape product pages on failed downloads'))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            for item in items:
                self.stdout.write(f"Would download: {item.title} - {item.image_url}")
            return

        success_count = 0
        fail_count = 0
        skip_count = 0
        rescrape_count = 0

        for item in items:
            # Skip if already has local image (unless force)
            if not force and item.image:
                skip_count += 1
                continue

            self.stdout.write(f"Processing: {item.title} (ID: {item.id})")

            # Try to download the existing image_url
            download_success = False
            try:
                result = download_image_from_url(item.image_url)
                if result:
                    content_file, filename = result

                    # Save the image
                    item.image.save(filename, content_file, save=False)

                    # Clear image_url after successful download
                    old_url = item.image_url
                    item.image_url = ''

                    # Save the model
                    item.save()

                    success_count += 1
                    download_success = True
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Downloaded and saved: {filename} (from {old_url})"
                        )
                    )

            except (ImageDownloadException, Exception) as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Failed to download from image_url: {str(e)}"
                    )
                )
                logger.warning(f"Failed to download image for item {item.id}: {str(e)}")

            # If download failed and rescrape is enabled and item has a link
            if not download_success and rescrape and item.link:
                self.stdout.write(f"  → Attempting to re-scrape product page: {item.link}")

                try:
                    # Re-scrape the product page
                    scraper = ProductScraper(item.link)
                    scraped_data, error = scraper.scrape()

                    if scraped_data and scraped_data.get('image_url'):
                        new_image_url = scraped_data['image_url']
                        self.stdout.write(f"  → Found new image from scrape: {new_image_url}")

                        # Try to download the newly scraped image
                        try:
                            result = download_image_from_url(new_image_url)
                            if result:
                                content_file, filename = result

                                # Save the image
                                item.image.save(filename, content_file, save=False)

                                # Clear old image_url
                                item.image_url = ''

                                # Save the model
                                item.save()

                                success_count += 1
                                rescrape_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  ✓ Re-scraped and saved: {filename}"
                                    )
                                )
                            else:
                                fail_count += 1
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"  ✗ Failed to download re-scraped image"
                                    )
                                )
                        except (ImageDownloadException, Exception) as e:
                            fail_count += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f"  ✗ Failed to download re-scraped image: {str(e)}"
                                )
                            )
                    else:
                        fail_count += 1
                        error_msg = error.get('error', 'No image found') if error else 'No image found'
                        self.stdout.write(
                            self.style.ERROR(
                                f"  ✗ Re-scrape failed: {error_msg}"
                            )
                        )

                except Exception as e:
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Re-scrape error: {str(e)}"
                        )
                    )
                    logger.error(f"Re-scrape error for item {item.id}: {str(e)}")

            elif not download_success:
                # Download failed and either rescrape is disabled or item has no link
                fail_count += 1
                if not item.link:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ No product link available for re-scraping"
                        )
                    )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Successfully downloaded: {success_count}"))
        if rescrape_count > 0:
            self.stdout.write(self.style.SUCCESS(f"  - Via re-scraping: {rescrape_count}"))
        if fail_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed to download: {fail_count}"))
        if skip_count > 0:
            self.stdout.write(self.style.WARNING(f"Skipped (already has image): {skip_count}"))
        self.stdout.write("=" * 50)
