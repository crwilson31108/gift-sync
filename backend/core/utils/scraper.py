import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self, url: str):
        self.url = url
        self.domain = urlparse(url).netloc
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

<<<<<<< Updated upstream
    def scrape(self) -> Dict:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
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
        except Exception as e:
            logger.error(f"Error scraping {self.url}: {str(e)}")
            return {}
=======
    def scrape(self):
        try:
            # Try regular requests first
            data = self._scrape_with_requests()
            if data:
                return data

            # If regular request fails, try cloudscraper
            data = self._scrape_with_cloudscraper()
            if data:
                return data

            # If both fail, return manual data if available
            if self.manual_data:
                return self.manual_data

            raise Exception("Failed to scrape URL")
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            # Return manual data if available, otherwise re-raise
            if self.manual_data:
                return self.manual_data
            raise

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
>>>>>>> Stashed changes

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
        """Get product price using various selectors"""
        price_patterns = [
            r'\$\s*(\d+(?:\.\d{2})?)',  # $299.00
            r'(\d+(?:\.\d{2})?)\s*dollars',  # 299.00 dollars
            r'Price:\s*\$\s*(\d+(?:\.\d{2})?)',  # Price: $299.00
        ]
        
        selectors = [
            # Accessibility and SR (Screen Reader) elements
            ('span', {'class': 'sr-only'}),
            ('span', {'class': re.compile(r'.*price.*', re.I)}),
            
            # Common price elements
            ('span', {'class': re.compile(r'price|amount|product-price', re.I)}),
            ('div', {'class': re.compile(r'price|amount|product-price', re.I)}),
            ('p', {'class': re.compile(r'price|amount|product-price', re.I)}),
            
            # Price with currency
            ('span', {'class': 'price-value'}),
            ('span', {'class': 'sales-price'}),
            
            # Metadata
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'property': 'og:price:amount'}),
            ('meta', {'itemprop': 'price'}),
        ]
        
        # First try to find price in any text content
        for text in soup.stripped_strings:
            for pattern in price_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue

        # Then try specific selectors
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                # Get text from element and its children
                price_text = ' '.join(element.stripped_strings)
                
                # Try to find price in the text
                for pattern in price_patterns:
                    match = re.search(pattern, price_text)
                    if match:
                        try:
                            return float(match.group(1))
                        except ValueError:
                            continue
                            
                # Check for content attribute (meta tags)
                if tag == 'meta':
                    content = element.get('content', '')
                    try:
                        return float(content)
                    except ValueError:
                        continue
                    
        # Look for structured data price as last resort
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, list):
                        offers = offers[0]
                    if 'price' in offers:
                        try:
                            return float(offers['price'])
                        except ValueError:
                            continue
            except:
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
        """Get all image URLs on the page"""
        images = []
        for img in soup.find_all('img'):
            url = img.get('src') or img.get('data-src')
            if url:
                images.append(urljoin(self.url, url))
        return images 