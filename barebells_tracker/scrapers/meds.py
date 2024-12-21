import re
import logging
from typing import Dict, List
from ..models.product import Product 
from .base import BaseScraper
from bs4 import BeautifulSoup


class MedsScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.meds.se/',
            'Upgrade-Insecure-Requests': '1'
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.meds.se/sok/?q=barebells']

    def parse_products(self, html_content: str) -> List[Product]:
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all product cards
        product_cards = soup.find_all('div', class_='product-card-grid')
        
        for card in product_cards:
            try:
                # Only process Barebells products
                name = card.find('span', class_='display-name')
                if not name or 'barebells' not in name.text.lower():
                    continue
                
                name = name.text.strip()
                
                # Get price - remove 'kr' and convert to float
                price_div = card.find('div', class_='product-card-pricing')
                if price_div and price_div.find('span'):
                    price_text = price_div.find('span').text.strip()
                    price = float(price_text.replace('kr', '').strip())
                else:
                    continue
                
                # Get URL
                url_element = card.find('a', href=True)
                if url_element:
                    url = 'https://www.meds.se' + url_element['href']
                else:
                    continue
                
                # Check availability - look for the buy button
                buy_button = card.find('button', class_='button-pink')
                available = bool(buy_button)
                
                # Extract package size if available
                package_size = None
                if 'x' in name.lower() and 'g' in name.lower():
                    match = re.search(r'(\d+)\s*x', name)
                    if match:
                        package_size = int(match.group(1))
                elif '12-pack' in name.lower():
                    package_size = 12
                
                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='meds',
                    package_size=package_size,
                    per_unit_price=price / package_size if package_size else None,
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
