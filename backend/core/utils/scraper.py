import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Dict, Optional, List, Union, Tuple
import json
import logging
from time import sleep
from decimal import Decimal
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Browser, Page
from contextlib import contextmanager
from fake_useragent import UserAgent
import cloudscraper
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import os
from django.conf import settings

logger = logging.getLogger(__name__)

class ScraperException(Exception):
    """Custom exception for scraper errors with detailed information"""
    def __init__(self, message: str, details: Dict = None, original_error: Exception = None):
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)

    def to_dict(self) -> Dict:
        error_dict = {
            'message': self.message,
            'details': self.details
        }
        if self.original_error:
            error_dict['original_error'] = str(self.original_error)
        return error_dict

@dataclass
class ManualProductData:
    """Class for storing manually entered product data"""
    title: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    all_images: List[str] = None

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'price': self.price,
            'image_url': self.image_url,
            'description': self.description,
            'all_images': self.all_images or []
        }

class ProductScraper:
    def __init__(self, url: str, manual_data: Optional[ManualProductData] = None):
        self.url = url
        self.domain = urlparse(url).netloc
        self.manual_data = manual_data
        self.ua = UserAgent(browsers=['chrome', 'firefox', 'safari'])
        
        # Enhanced headers with more realistic values
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # Increased retries and delay
        self.max_retries = 5
        self.retry_delay = 3
        
        # Initialize cloudscraper with more browser-like behavior
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            delay=3
        )

    def _get_session(self):
        """Create a session with enhanced retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _scrape_with_requests(self) -> Dict:
        """Enhanced requests scraping with multiple methods"""
        methods = [
            self._try_regular_session,
            self._try_cloudscraper,
            self._try_playwright
        ]

        for method in methods:
            try:
                data = method()
                if data and any(data.values()):
                    return data
            except Exception as e:
                logger.warning(f"Method {method.__name__} failed: {str(e)}")
                continue

        return {}

    def _try_regular_session(self) -> Dict:
        """Try with regular requests session"""
        session = self._get_session()
        session.headers.update(self.headers)
        
        response = session.get(self.url, timeout=15)
        if response.status_code == 200:
            return self._parse_content(response.text)
        return {}

    def _try_cloudscraper(self) -> Dict:
        """Try with cloudscraper"""
        response = self.scraper.get(self.url)
        if response.status_code == 200:
            return self._parse_content(response.text)
        return {}

    @contextmanager
    def get_browser(self):
        """Context manager for Playwright browser"""
        playwright = None
        browser = None
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            yield browser
        except Exception as e:
            logger.error(f"Failed to create browser: {str(e)}")
            raise
        finally:
            try:
                if browser:
                    browser.close()
                if playwright:
                    playwright.stop()
            except Exception as e:
                logger.error(f"Failed to close browser: {str(e)}")

    def _try_playwright(self) -> Dict:
        """Playwright scraping with better error handling"""
        try:
            with self.get_browser() as browser:
                page = browser.new_page()

                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': self.ua.random
                })

                try:
                    # Navigate to the page with timeout
                    page.goto(self.url, timeout=30000, wait_until='domcontentloaded')

                    # Wait a bit for dynamic content
                    page.wait_for_timeout(2000)

                    # Get page content
                    page_content = page.content()

                    if not page_content:
                        raise ScraperException("Empty page source received")

                    data = self._parse_content(page_content)
                    if not any(data.values()):
                        raise ScraperException("No data extracted from page")

                    return data
                except Exception as e:
                    logger.error(f"Playwright navigation/parse error: {str(e)}")
                    # Try to get page content even if wait failed
                    try:
                        return self._parse_content(page.content())
                    except:
                        raise
                finally:
                    page.close()
        except Exception as e:
            logger.error(f"Playwright error: {str(e)}")
            raise ScraperException("Playwright scraping failed",
                                 details={'original_error': str(e)})

    def scrape(self) -> Tuple[Dict, Optional[Dict]]:
        """
        Scrape the URL and return both the data and any error information
        Returns: (data_dict, error_dict)
        """
        error_details = {
            'url': self.url,
            'methods_tried': [],
            'method_errors': {}
        }
        
        try:
            # Try regular requests first
            error_details['methods_tried'].append('requests')
            try:
                data = self._scrape_with_requests()
                if data:
                    return data, None
            except Exception as e:
                error_details['method_errors']['requests'] = str(e)
                logger.error(f"Requests method failed: {str(e)}")

            # Try cloudscraper
            error_details['methods_tried'].append('cloudscraper')
            try:
                data = self._try_cloudscraper()
                if data:
                    return data, None
            except Exception as e:
                error_details['method_errors']['cloudscraper'] = str(e)
                logger.error(f"Cloudscraper method failed: {str(e)}")

            # Try playwright
            error_details['methods_tried'].append('playwright')
            try:
                data = self._try_playwright()
                if data:
                    return data, None
            except Exception as e:
                error_details['method_errors']['playwright'] = str(e)
                logger.error(f"Playwright method failed: {str(e)}")

            # If we have manual data, return it
            if self.manual_data:
                return self.manual_data.to_dict(), None

            # If all methods failed, raise exception with details
            raise ScraperException(
                "All scraping methods failed",
                details=error_details
            )
        except Exception as e:
            error_dict = {
                'error': str(e),
                'details': error_details if isinstance(e, ScraperException) else None
            }
            logger.error(f"Scraping failed: {error_dict}")
            
            # Return manual data if available, otherwise return error
            if self.manual_data:
                return self.manual_data.to_dict(), error_dict
            return None, error_dict

    def _merge_with_manual_data(self, scraped_data: Dict) -> Dict:
        """
        Merge scraped data with manual data, preferring manual data when available
        """
        if not self.manual_data:
            return scraped_data

        manual_dict = self.manual_data.to_dict()
        merged_data = scraped_data.copy()

        # Override scraped data with manual data where manual data exists
        for key, value in manual_dict.items():
            if value is not None:  # Only override if manual value exists
                merged_data[key] = value

        # Special handling for all_images
        if manual_dict.get('all_images'):
            # Add manual images to the beginning of the list
            merged_data['all_images'] = list(dict.fromkeys(
                manual_dict['all_images'] + scraped_data.get('all_images', [])
            ))

        return merged_data

    def _parse_content(self, html_content: str) -> Dict:
        """Enhanced parsing with site-specific handling"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Site-specific handling
        if 'amazon' in self.domain:
            amazon_data = self._get_amazon_data(soup)
            if amazon_data:
                amazon_data['all_images'] = self._get_all_images(soup)
                return amazon_data
        
        # Try structured data first
        structured_data = self._get_structured_data(soup)
        if structured_data:
            structured_data['all_images'] = self._get_all_images(soup)
            return structured_data
        
        # Fallback to regular scraping
        scraped_data = {
            'title': self._get_title(soup),
            'price': self._get_price(soup),
            'image_url': self._get_image(soup),
            'description': self._get_description(soup),
            'all_images': self._get_all_images(soup)
        }
        
        return scraped_data

    def _get_structured_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product info from structured data if available"""
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
            ('meta', {'name': 'title'}),
            
            # Common title elements
            ('h1', {'class': re.compile(r'product.*title|title|name', re.I)}),
            ('h1', {'id': re.compile(r'product.*title|title|name', re.I)}),
            
            # Site specific selectors
            ('h1', {'class': 'product-title'}),  # Common in many shops
            ('span', {'id': 'productTitle'}),    # Amazon
            ('h1', {'itemprop': 'name'}),       # Schema.org
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    return element.get('content')
                return element.text.strip()
        return None

    def _get_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Enhanced price extraction with more patterns and currency handling"""
        price_patterns = [
            r'[\$\£\€]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $299.00, €299.00
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[\$\£\€]',  # 299.00$
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Just numbers
            r'Price:\s*[\$\£\€]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        additional_selectors = [
            ('span', {'class': 'product-price'}),
            ('span', {'class': 'price-current'}),
            ('div', {'class': 'product-price-current'}),
            ('span', {'class': 'sales'}),
            ('div', {'class': 'price-box'}),
            # Add site-specific selectors
            ('span', {'class': 'money'}),  # Shopify sites
            ('span', {'data-product-price': True}),  # Some e-commerce platforms
        ]
        
        # Add new selectors to existing ones
        selectors = additional_selectors

        # First try to find price in structured data
        structured_price = self._extract_structured_price(soup)
        if structured_price is not None:
            return structured_price

        # Then try specific selectors
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                price_text = ' '.join(element.stripped_strings)
                price = self._extract_price_from_text(price_text, price_patterns)
                if price is not None:
                    return price

        return None

    def _extract_price_from_text(self, text: str, patterns: List[str]) -> Optional[float]:
        """Extract price from text using various patterns"""
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    # Remove commas and convert to float
                    price_str = match.group(1).replace(',', '')
                    return float(price_str)
                except (ValueError, IndexError):
                    continue
        return None

    def _get_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Get product image URL using various selectors"""
        selectors = [
            # Common meta tags
            ('meta', {'property': 'og:image'}),
            ('meta', {'property': 'product:image'}),
            ('meta', {'name': 'twitter:image'}),
            
            # Common image elements
            ('img', {'class': re.compile(r'product.*image|main.*image', re.I)}),
            ('img', {'id': re.compile(r'product.*image|main.*image', re.I)}),
            
            # Site specific selectors
            ('img', {'id': 'landingImage'}),     # Amazon
            ('img', {'class': 'primary-image'}), # Common pattern
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    url = element.get('content')
                else:
                    url = element.get('src') or element.get('data-src')
                
                if url:
                    # Convert relative URLs to absolute
                    return urljoin(self.url, url)
        return None

    def _get_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Get product description using various selectors"""
        selectors = [
            # Common meta tags
            ('meta', {'property': 'og:description'}),
            ('meta', {'name': 'description'}),
            ('meta', {'name': 'twitter:description'}),
            
            # Common description elements
            ('div', {'class': re.compile(r'product.*description|description', re.I)}),
            ('div', {'id': re.compile(r'product.*description|description', re.I)}),
            
            # Site specific selectors
            ('div', {'id': 'productDescription'}),  # Amazon
            ('div', {'class': 'product-details'}),  # Common pattern
            ('div', {'itemprop': 'description'}),   # Schema.org
        ]
        
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                if tag == 'meta':
                    content = element.get('content', '').strip()
                else:
                    content = element.text.strip()
                if content:
                    return content
        return None

    def _get_all_images(self, soup: BeautifulSoup) -> list:
        """Enhanced image extraction including lazy-loaded images"""
        images = set()
        
        # Regular image sources
        img_attrs = ['src', 'data-src', 'data-lazy-src', 'data-original',
                    'data-srcset', 'data-lazy', 'data-zoom-image']
        
        for img in soup.find_all(['img', 'source']):
            for attr in img_attrs:
                url = img.get(attr)
                if url:
                    if isinstance(url, str):
                        images.add(urljoin(self.url, url))
                    elif isinstance(url, list):
                        for u in url:
                            images.add(urljoin(self.url, u))

        # Look for images in JSON-LD data
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
                            images.add(urljoin(self.url, img))
            except:
                continue

        return list(images)

    def _get_amazon_data(self, soup: BeautifulSoup) -> Dict:
        """Special handling for Amazon pages"""
        data = {}
        
        # Amazon title
        title_element = soup.find('span', {'id': 'productTitle'})
        if title_element:
            data['title'] = title_element.text.strip()
        
        # Amazon price - multiple possible locations
        price_elements = [
            soup.find('span', {'class': 'a-price-whole'}),
            soup.find('span', {'id': 'priceblock_ourprice'}),
            soup.find('span', {'id': 'priceblock_dealprice'}),
            soup.find('span', {'class': 'a-offscreen'})
        ]
        
        for element in price_elements:
            if element:
                price_text = element.text.strip()
                try:
                    # Extract numbers from price text
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    data['price'] = price
                    break
                except ValueError:
                    continue
        
        # Amazon images
        image_element = soup.find('img', {'id': 'landingImage'})
        if image_element:
            data['image_url'] = image_element.get('data-old-hires') or image_element.get('src')
        
        # Amazon description
        description_element = soup.find('div', {'id': 'productDescription'})
        if description_element:
            data['description'] = description_element.text.strip()
        
        return data

    def _extract_structured_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from structured data"""
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                
                # Check for price in offers
                if 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, list):
                        offers = offers[0]
                    if isinstance(offers, dict):
                        price = offers.get('price')
                        if price:
                            return float(price)
                
                # Direct price property
                if 'price' in data:
                    return float(data['price'])
            except:
                continue
        return None 