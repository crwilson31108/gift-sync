import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Dict, Optional, List, Union
import json
import logging
from time import sleep
from decimal import Decimal
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import cloudscraper
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

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

@contextmanager
def get_driver():
    """Context manager for creating and cleaning up Selenium driver"""
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    try:
        yield driver
    finally:
        driver.quit()

class ProductScraper:
    def __init__(self, url: str, manual_data: Optional[ManualProductData] = None):
        self.url = url
        self.domain = urlparse(url).netloc
        self.manual_data = manual_data
        self.ua = UserAgent(browsers=['chrome', 'firefox', 'safari'])
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        self.max_retries = 3
        self.retry_delay = 2
        
        # Initialize cloudscraper
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )

    def _get_session(self):
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
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
            self._try_selenium
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
    def get_driver(self):
        """Enhanced Selenium driver setup"""
        options = Options()
        options.add_argument('--headless=new')  # Updated headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={self.ua.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Add more stealth
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Execute stealth scripts
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.ua.random,
            "platform": "Windows",
        })
        
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        try:
            yield driver
        finally:
            driver.quit()

    def _try_selenium(self) -> Dict:
        """Try with Selenium as last resort"""
        with self.get_driver() as driver:
            driver.get(self.url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self._parse_content(driver.page_source)

    def scrape(self) -> Dict:
        """
        Attempt to scrape product data, falling back to manual data if scraping fails
        """
        try:
            # Try regular requests first
            data = self._scrape_with_requests()
            if not any(data.values()):
                # If no data found, try with Selenium
                data = self._try_selenium()

            # Merge with manual data, preferring manual data when available
            return self._merge_with_manual_data(data)
        except Exception as e:
            logger.error(f"Error scraping {self.url}: {str(e)}")
            # Return manual data if available, otherwise empty dict
            return self.manual_data.to_dict() if self.manual_data else {}

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
        """Parse HTML content and extract product information"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Try to extract structured data first
        structured_data = self._get_structured_data(soup)
        if structured_data:
            structured_data['all_images'] = self._get_all_images(soup)
            return structured_data

        # Fallback to regular scraping
        return {
            'title': self._get_title(soup),
            'price': self._get_price(soup),
            'image_url': self._get_image(soup),
            'description': self._get_description(soup),
            'all_images': self._get_all_images(soup)
        }

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