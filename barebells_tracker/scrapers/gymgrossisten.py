import re
import logging
from typing import Dict, List
from ..models.product import Product 
from .base import BaseScraper
from bs4 import BeautifulSoup

class GymgrossistenScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.gymgrossisten.com/search?q=barebells&lang=sv_SE']

    def parse_products(self, response_data: Dict) -> List[Product]:
        """Implement required abstract method, but it won't be used directly."""
        return []

    def scrape_products(self) -> List[Product]:
        """Override scrape_products to handle HTML parsing."""
        products = []
        
        try:
            response = self.session.get(
                self.get_product_urls()[0],
                headers=self.get_headers(),
                timeout=15  # Increased timeout due to slow API
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            product_items = soup.find_all('div', class_='product-item')
            
            for item in product_items:
                try:
                    # Check if it's a Barebells product
                    brand = item.get('data-brand')
                    if not brand or brand.lower() != 'barebells':
                        continue

                    # Extract product data
                    name = item.find('p', class_='product-tile-name')
                    name = name.text.strip() if name else None

                    price_div = item.find('div', class_='price-adjusted')
                    if price_div:
                        price = float(price_div.text.strip().replace('kr', '').strip())
                    
                    # Get URL
                    url_elem = item.find('a', class_='product-tile-image-link')
                    url = None
                    if url_elem and url_elem.get('href'):
                        url = 'https://www.gymgrossisten.com' + url_elem['href']
                    
                    # Extract package size from name
                    package_size = None
                    if name:
                        # Look for patterns like "12 x" in name
                        size_match = re.search(r'(\d+)\s*x', name)
                        if size_match:
                            package_size = int(size_match.group(1))
                        elif '12-pack' in name.lower():
                            package_size = 12
                    
                    # Availability check
                    available = True  # Default to True unless we find indication otherwise
                    
                    if name and price and url:
                        product = Product(
                            name=name,
                            price=price,
                            url=url,
                            store='gymgrossisten',
                            package_size=package_size,
                            per_unit_price=price / package_size if package_size else None,
                            available=available
                        )
                        products.append(product)
                        logging.info(f"Found product: {name} at {price} SEK")
                        
                except Exception as e:
                    logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error with GymgrossistenScraper: {str(e)}")
            
        return products
