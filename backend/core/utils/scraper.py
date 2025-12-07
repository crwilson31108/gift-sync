import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Dict, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self, url: str):
        self.url = url
        self.domain = urlparse(url).netloc
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def scrape(self) -> Dict:
        """
        Scrape product data from URL
        Returns dict with title, price, image_url, description, all_images
        """
        try:
            logger.info(f"Scraping URL: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            logger.info(f"Got response, status: {response.status_code}, size: {len(response.text)}")

            # Try to extract structured data first (JSON-LD)
            structured_data = self._get_structured_data(soup)
            if structured_data and (structured_data.get('title') or structured_data.get('price')):
                logger.info("Using structured data (JSON-LD)")
                structured_data['all_images'] = self._get_all_images(soup)
                return structured_data

            # Fallback to regular HTML scraping
            logger.info("Using HTML parsing fallback")
            data = {
                'title': self._get_title(soup),
                'price': self._get_price(soup),
                'image_url': self._get_image(soup),
                'description': self._get_description(soup),
                'all_images': self._get_all_images(soup)
            }

            logger.info(f"Scraped data: title={'Yes' if data.get('title') else 'No'}, price={'Yes' if data.get('price') else 'No'}")
            return data

        except Exception as e:
            logger.error(f"Error scraping {self.url}: {str(e)}")
            return {
                'title': None,
                'price': None,
                'image_url': None,
                'description': None,
                'all_images': []
            }

    def _get_structured_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product info from JSON-LD structured data if available"""
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]

                if data.get('@type') in ['Product', 'IndividualProduct']:
                    price = None
                    if 'offers' in data:
                        offers = data['offers']
                        if isinstance(offers, list):
                            offers = offers[0]
                        price = offers.get('price')

                    return {
                        'title': data.get('name'),
                        'price': float(price) if price else None,
                        'image_url': data.get('image'),
                        'description': data.get('description')
                    }
            except:
                continue
        return None

    def _get_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Get product title using various selectors"""
        selectors = [
            # Common meta tags
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),

            # Common title elements
            ('h1', {'class': re.compile(r'product.*title|title|name', re.I)}),
            ('h1', {'id': re.compile(r'product.*title|title|name', re.I)}),
            ('span', {'id': 'productTitle'}),    # Amazon
            ('h1', {'itemprop': 'name'}),       # Schema.org
            ('h1', {}),  # Any h1 as last resort
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    return element.get('content')
                text = element.text.strip()
                if text:
                    return text
        return None

    def _get_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Get product price using various selectors"""
        price_patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $299.00 or $1,299.00
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars|USD)',
            r'Price:\s*\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]

        selectors = [
            ('span', {'class': re.compile(r'.*price.*', re.I)}),
            ('div', {'class': re.compile(r'.*price.*', re.I)}),
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'property': 'og:price:amount'}),
            ('meta', {'itemprop': 'price'}),
        ]

        # Try specific selectors first
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                if tag == 'meta':
                    content = element.get('content', '')
                    try:
                        return float(content.replace(',', ''))
                    except ValueError:
                        continue
                else:
                    price_text = ' '.join(element.stripped_strings)
                    for pattern in price_patterns:
                        match = re.search(pattern, price_text)
                        if match:
                            try:
                                return float(match.group(1).replace(',', ''))
                            except ValueError:
                                continue

        return None

    def _get_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Get product image URL using various selectors"""
        selectors = [
            ('meta', {'property': 'og:image'}),
            ('meta', {'property': 'product:image'}),
            ('meta', {'name': 'twitter:image'}),
            ('img', {'class': re.compile(r'product.*image|main.*image', re.I)}),
            ('img', {'id': re.compile(r'product.*image|main.*image', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    url = element.get('content')
                else:
                    url = element.get('src') or element.get('data-src')

                if url and not url.startswith('data:'):
                    return urljoin(self.url, url)
        return None

    def _get_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Get product description using various selectors"""
        selectors = [
            ('meta', {'property': 'og:description'}),
            ('meta', {'name': 'description'}),
            ('div', {'class': re.compile(r'.*description.*', re.I)}),
            ('div', {'id': re.compile(r'.*description.*', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    return element.get('content', '').strip()
                text = element.text.strip()
                if text and len(text) > 20:  # Avoid short/empty descriptions
                    return text[:500]  # Limit length
        return None

    def _get_all_images(self, soup: BeautifulSoup) -> List[str]:
        """Get all product images from the page"""
        images = set()

        # Look for product images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                full_url = urljoin(self.url, src)
                # Filter out tiny images (likely icons)
                if 'icon' not in full_url.lower() and 'logo' not in full_url.lower():
                    images.add(full_url)

        # Also check JSON-LD for images
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if 'image' in data:
                    if isinstance(data['image'], str):
                        images.add(urljoin(self.url, data['image']))
                    elif isinstance(data['image'], list):
                        for img in data['image']:
                            if isinstance(img, str):
                                images.add(urljoin(self.url, img))
            except:
                continue

        return list(images)[:20]  # Limit to 20 images
