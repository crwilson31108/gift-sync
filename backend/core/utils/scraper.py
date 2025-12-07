import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Dict, Optional, List
import json
import logging
import os

logger = logging.getLogger(__name__)

# Site-specific configurations for reliable scraping
SITE_CONFIGS = {
    'amazon.com': {
        'title_selectors': ['#productTitle', 'h1.product-title'],
        'price_selectors': [
            '.a-price .a-offscreen',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.a-price-whole'
        ],
        'image_selectors': ['#landingImage', '#imgBlkFront', '.a-dynamic-image'],
        'price_json_keys': ['apexPriceToPay', 'priceblock']
    },
    'amazon.co.uk': {
        'title_selectors': ['#productTitle'],
        'price_selectors': ['.a-price .a-offscreen', '#priceblock_ourprice'],
        'image_selectors': ['#landingImage', '#imgBlkFront']
    },
    'etsy.com': {
        'title_selectors': ['h1[data-buy-box-listing-title]', 'h1.wt-text-body-01'],
        'price_selectors': ['p[class*="wt-text-title-03"]', 'p.wt-text-title-larger'],
        'image_selectors': ['img[data-key="listing-page-image"]', 'img.wt-max-width-full']
    },
    'bestbuy.com': {
        'title_selectors': ['.sku-title h1', 'h1[class*="heading"]'],
        'price_selectors': ['[data-testid="customer-price"]', '.priceView-customer-price'],
        'image_selectors': ['.primary-image', 'img[class*="primary"]']
    },
    'target.com': {
        'title_selectors': ['h1[data-test="product-title"]', 'h1'],
        'price_selectors': ['[data-test="product-price"]', 'span[class*="Price"]'],
        'image_selectors': ['img[data-test="product-image"]', 'picture img']
    },
    'walmart.com': {
        'title_selectors': ['h1[itemprop="name"]', 'h1'],
        'price_selectors': ['span[itemprop="price"]', '[data-automation-id="product-price"]'],
        'image_selectors': ['img[data-testid="hero-image"]', 'img.hover-zoom-hero-image']
    },
    'wayfair.com': {
        'title_selectors': ['h1[data-enzyme-id="ProductTitle"]', 'h1'],
        'price_selectors': ['.BasePriceBlock', '.SFPrice'],
        'image_selectors': ['img[data-enzyme-id="PrimaryProductImage"]']
    },
    'homedepot.com': {
        'title_selectors': ['h1.product-details__title', 'h1'],
        'price_selectors': ['[data-testid="product-price"]', '.price-format__main-price'],
        'image_selectors': ['img.mediaBrowser__image', 'img[data-testid="product-image"]']
    },
    'ebay.com': {
        'title_selectors': ['h1.x-item-title__mainTitle', 'h1'],
        'price_selectors': ['.x-price-primary', '.x-bin-price'],
        'image_selectors': ['img.ux-image-magnify__image', 'img#icImg']
    },
}

# Try to import Playwright (optional dependency)
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    logger.info("Playwright is available for JavaScript rendering")
except ImportError:
    logger.info("Playwright not available - will use requests-only scraping")

# Check if Playwright is enabled via environment variable
USE_PLAYWRIGHT = os.getenv('USE_PLAYWRIGHT', 'true').lower() == 'true' and PLAYWRIGHT_AVAILABLE

class ProductScraper:
    def __init__(self, url: str):
        self.url = url
        self.domain = urlparse(url).netloc
        self.site_config = self._get_site_config()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
        self.scrape_method = 'unknown'  # Track which method succeeded

    def _get_site_config(self) -> Optional[Dict]:
        """Get site-specific configuration if available"""
        for domain, config in SITE_CONFIGS.items():
            if domain in self.domain:
                logger.info(f"Using site-specific config for {domain}")
                return config
        return None

    def scrape(self) -> Dict:
        """
        Scrape product data from URL using multi-tier approach:
        1. Try requests + BeautifulSoup (fast)
        2. If that fails and Playwright is available, try browser rendering

        Returns dict with title, price, image_url, description, all_images, scrape_method, error
        """
        # Try regular scraping first (fast)
        data = self._scrape_with_requests()

        # If we got good data, return it
        if data.get('title') or data.get('price'):
            return data

        # If Playwright is available and enabled, try browser rendering
        if USE_PLAYWRIGHT and not (data.get('title') and data.get('price')):
            logger.info("Regular scraping failed, trying Playwright browser rendering...")
            browser_data = self._scrape_with_playwright()
            if browser_data and (browser_data.get('title') or browser_data.get('price')):
                return browser_data

        # Return whatever we have (might be empty)
        data['error'] = 'Could not extract product information. Please enter details manually.'
        return data

    def _scrape_with_requests(self) -> Dict:
        """
        Standard scraping using requests + BeautifulSoup
        """
        try:
            logger.info(f"Scraping URL with requests: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            logger.info(f"Got response, status: {response.status_code}, size: {len(response.text)}")

            # Try to extract structured data first (JSON-LD)
            structured_data = self._get_structured_data(soup)
            if structured_data and (structured_data.get('title') or structured_data.get('price')):
                logger.info("Using structured data (JSON-LD)")
                self.scrape_method = 'json-ld'
                structured_data['all_images'] = self._get_all_images(soup)
                structured_data['scrape_method'] = self.scrape_method
                return structured_data

            # Try site-specific selectors if available
            if self.site_config:
                site_data = self._scrape_with_site_config(soup)
                if site_data and (site_data.get('title') or site_data.get('price')):
                    logger.info("Using site-specific selectors")
                    self.scrape_method = 'site-specific'
                    site_data['scrape_method'] = self.scrape_method
                    return site_data

            # Fallback to generic HTML scraping
            logger.info("Using generic HTML parsing")
            self.scrape_method = 'generic-html'
            data = {
                'title': self._get_title(soup),
                'price': self._get_price(soup),
                'image_url': self._get_image(soup),
                'description': self._get_description(soup),
                'all_images': self._get_all_images(soup),
                'scrape_method': self.scrape_method
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
                'all_images': [],
                'scrape_method': 'failed',
                'error': str(e)
            }

    def _scrape_with_playwright(self) -> Optional[Dict]:
        """
        Scrape using Playwright for JavaScript-heavy sites
        This is slower but handles dynamic content
        """
        try:
            logger.info(f"Attempting Playwright scraping for {self.url}")

            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']  # Required for some environments
                    )
                except Exception as launch_error:
                    logger.error(f"Failed to launch Playwright browser: {launch_error}")
                    logger.info("Consider running: python -m playwright install chromium")
                    return None

                try:
                    # Create context with realistic settings
                    context = browser.new_context(
                        user_agent=self.headers['User-Agent'],
                        viewport={'width': 1920, 'height': 1080},
                        locale='en-US',
                    )

                    page = context.new_page()

                    # Block unnecessary resources to speed up loading
                    def handle_route(route):
                        try:
                            route.abort()
                        except:
                            pass

                    try:
                        page.route("**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf,eot}", handle_route)
                    except:
                        pass  # Route blocking not critical

                    # Navigate and wait for network to be idle
                    page.goto(self.url, wait_until='networkidle', timeout=30000)

                    # Get the rendered HTML
                    html = page.content()

                finally:
                    try:
                        browser.close()
                    except:
                        pass

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'lxml')

                # Try structured data first
                structured_data = self._get_structured_data(soup)
                if structured_data and (structured_data.get('title') or structured_data.get('price')):
                    logger.info("Playwright: Found structured data")
                    self.scrape_method = 'playwright-json-ld'
                    structured_data['all_images'] = self._get_all_images(soup)
                    structured_data['scrape_method'] = self.scrape_method
                    return structured_data

                # Try site-specific selectors
                if self.site_config:
                    site_data = self._scrape_with_site_config(soup)
                    if site_data and (site_data.get('title') or site_data.get('price')):
                        logger.info("Playwright: Using site-specific selectors")
                        self.scrape_method = 'playwright-site-specific'
                        site_data['scrape_method'] = self.scrape_method
                        return site_data

                # Generic fallback
                logger.info("Playwright: Using generic parsing")
                self.scrape_method = 'playwright-generic'
                data = {
                    'title': self._get_title(soup),
                    'price': self._get_price(soup),
                    'image_url': self._get_image(soup),
                    'description': self._get_description(soup),
                    'all_images': self._get_all_images(soup),
                    'scrape_method': self.scrape_method
                }

                return data

        except Exception as e:
            logger.error(f"Playwright scraping failed: {str(e)}")
            logger.info("Falling back to manual entry")
            return None

    def _scrape_with_site_config(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Use site-specific selectors to extract data"""
        if not self.site_config:
            return None

        data = {
            'title': None,
            'price': None,
            'image_url': None,
            'description': None,
            'all_images': []
        }

        # Try title selectors
        for selector in self.site_config.get('title_selectors', []):
            try:
                element = soup.select_one(selector)
                if element and element.text.strip():
                    data['title'] = element.text.strip()
                    break
            except:
                continue

        # Try price selectors
        for selector in self.site_config.get('price_selectors', []):
            try:
                element = soup.select_one(selector)
                if element:
                    price_text = element.text.strip()
                    price = self._extract_price_from_text(price_text)
                    if price:
                        data['price'] = price
                        break
            except:
                continue

        # Try image selectors
        for selector in self.site_config.get('image_selectors', []):
            try:
                element = soup.select_one(selector)
                if element:
                    url = element.get('src') or element.get('data-src')
                    if url and not url.startswith('data:'):
                        data['image_url'] = urljoin(self.url, url)
                        break
            except:
                continue

        # Get description using generic method
        data['description'] = self._get_description(soup)
        data['all_images'] = self._get_all_images(soup)

        return data if (data['title'] or data['price']) else None

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

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price from text using various patterns"""
        price_patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $299.00 or $1,299.00
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)',
            r'Price:\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:^|\s)(\d+(?:,\d{3})*\.\d{2})(?:\s|$)',  # Just the number with cents
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    return float(price_str)
                except (ValueError, IndexError):
                    continue
        return None

    def _get_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Get product price using various selectors"""
        # Enhanced meta tag selectors
        meta_selectors = [
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'property': 'og:price:amount'}),
            ('meta', {'name': 'price'}),
            ('meta', {'itemprop': 'price'}),
            ('meta', {'name': 'product:price:amount'}),
        ]

        # Try meta tags first
        for tag, attrs in meta_selectors:
            element = soup.find(tag, attrs)
            if element:
                content = element.get('content', '')
                try:
                    # Clean and convert
                    price_str = content.replace(',', '').replace('$', '').strip()
                    return float(price_str)
                except ValueError:
                    continue

        # HTML element selectors
        selectors = [
            ('span', {'class': re.compile(r'.*price.*', re.I)}),
            ('div', {'class': re.compile(r'.*price.*', re.I)}),
            ('span', {'itemprop': 'price'}),
            ('p', {'class': re.compile(r'.*price.*', re.I)}),
        ]

        # Try HTML elements
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                price_text = ' '.join(element.stripped_strings)
                price = self._extract_price_from_text(price_text)
                if price:
                    return price

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
