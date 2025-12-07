import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from urllib.parse import urlparse
import os
from typing import Optional, Tuple
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class ImageDownloadException(Exception):
    """Exception raised when image download fails"""
    pass

def download_image_from_url(url: str, timeout: int = 10) -> Optional[Tuple[ContentFile, str]]:
    """
    Download an image from a URL and return a Django ContentFile along with filename.

    Args:
        url: The URL of the image to download
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Tuple of (ContentFile, filename) or None if download fails

    Raises:
        ImageDownloadException: If download or processing fails
    """
    if not url:
        return None

    try:
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"URL does not point to an image. Content-Type: {content_type}")
            # Still try to process it in case the content-type is wrong

        # Read the image content
        image_content = BytesIO(response.content)

        # Verify it's a valid image and get format
        try:
            img = Image.open(image_content)
            img.verify()  # Verify it's a valid image

            # Reopen for actual processing (verify() closes the file)
            image_content = BytesIO(response.content)
            img = Image.open(image_content)

            # Convert RGBA to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background

            # Save to BytesIO with optimization
            output = BytesIO()
            img_format = img.format or 'JPEG'

            # Use JPEG for most images to save space
            if img_format.upper() in ('PNG', 'JPEG', 'JPG', 'WEBP'):
                if img_format.upper() == 'PNG' and img.mode == 'RGBA':
                    img_format = 'PNG'  # Keep PNG for transparency
                else:
                    img_format = 'JPEG'
                    img = img.convert('RGB')

            img.save(output, format=img_format, quality=85, optimize=True)
            output.seek(0)

        except Exception as e:
            logger.warning(f"Image verification/processing failed: {str(e)}. Using raw content.")
            # If processing fails, use the raw content
            image_content.seek(0)
            output = image_content
            img_format = 'JPEG'

        # Generate filename from URL
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)

        # If no filename or invalid filename, generate one
        if not original_filename or '.' not in original_filename:
            original_filename = 'image.jpg'

        # Ensure proper extension based on format
        name_without_ext = os.path.splitext(original_filename)[0]
        extension = img_format.lower()
        if extension == 'jpeg':
            extension = 'jpg'
        filename = f"{name_without_ext}.{extension}"

        # Create ContentFile
        content_file = ContentFile(output.read(), name=filename)

        logger.info(f"Successfully downloaded image from {url} as {filename}")
        return content_file, filename

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image from {url}: {str(e)}")
        raise ImageDownloadException(f"Network error downloading image: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing image from {url}: {str(e)}")
        raise ImageDownloadException(f"Error processing image: {str(e)}")
