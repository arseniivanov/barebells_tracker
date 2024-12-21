import re
import logging
from typing import Dict, List
from ..models.product import Product 
from .base import BaseScraper
from bs4 import BeautifulSoup


class MMSportsScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': 'store_language=sv; test-17=0',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.mmsports.se/'
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.mmsports.se/search.php?mode=search&substring=barebells']

    def parse_products(self, html_content: str) -> List[Product]:
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all product containers
        product_containers = soup.find_all('div', class_='product-container')
        
        for container in product_containers:
            try:
                # Get the product div with data attributes
                product_div = container.find('div', class_='product')
                if not product_div:
                    continue

                # Extract name
                title_div = container.find('div', class_='title')
                if not title_div or not title_div.find('a'):
                    continue
                name = title_div.find('a').text.strip()
                
                # Skip if not a Barebells product
                if 'barebells' not in name.lower():
                    continue

                # Extract URL
                url = title_div.find('a').get('href', '')
                if not url.startswith('http'):
                    url = 'https://www.mmsports.se' + url

                # Extract price
                price_row = container.find('div', class_='price-row')
                if not price_row:
                    continue
                price_text = price_row.find('span', class_='currency')
                if not price_text:
                    continue
                try:
                    price = float(price_text.text.strip().replace(':-', '').strip())
                except ValueError:
                    continue

                # Check availability based on buy button presence
                buy_button = container.find('button', class_='button-mm')
                available = bool(buy_button)
                
                # Get stock if available
                stock = None
                if buy_button and 'data-quantity' in buy_button.attrs:
                    try:
                        stock = int(buy_button['data-quantity'])
                    except (ValueError, TypeError):
                        pass

                # Extract package size from name or description
                package_size = None
                if '12-pack' in name.lower():
                    package_size = 12
                else:
                    # Look for patterns like "12 st" or "12x55g"
                    match = re.search(r'(\d+)\s*(?:st|x)', name.lower())
                    if match:
                        package_size = int(match.group(1))

                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='mmsports',
                    package_size=package_size,
                    per_unit_price=price / package_size if package_size else None,
                    stock=stock,
                    available=available
                )
                
                products.append(product)
                logging.info(f"Found product: {name} at {price} SEK")
                
            except Exception as e:
                logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return products

    def scrape_products(self) -> List[Product]:
        """Override scrape_products to handle HTML response."""
        products = []
        urls = self.get_product_urls()
        
        for url in urls:
            try:
                response = self.session.get(
                    url, 
                    headers=self.get_headers(),
                    timeout=10
                )
                response.raise_for_status()
                products.extend(self.parse_products(response.text))
            except Exception as e:
                logging.error(f"Error scraping {url}: {str(e)}")
                continue
        
        return products
