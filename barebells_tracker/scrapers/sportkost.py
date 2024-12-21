import re
import logging
from typing import Dict, List
from ..models.product import Product 
from .base import BaseScraper
from bs4 import BeautifulSoup

class SportkostScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def get_product_urls(self) -> List[str]:
        # Using the API endpoint instead of regular URLs
        return ['https://core.helloretail.com/api/v1/search/partnerSearch']

    def parse_products(self, response_data: Dict) -> List[Product]:
        """Implement required abstract method, but it won't be used directly."""
        # This method needs to exist but won't be used since we override scrape_products
        return []

    def scrape_products(self) -> List[Product]:
        """Override scrape_products to handle API request."""
        products = []
        
        params = {
            'key': '3742e894-25bb-4f1a-a76a-37dd7138c120',
            'q': 'barebells',
            'device_type': 'DESKTOP',
            'product_count': 100,  # Increase to get more products at once
            'product_start': 0,
            'category_count': 12,
            'category_start': 0,
            'brand_count': 12,
            'brand_start': 0,
            'id': '35164',
            'return_filters': 'true',
            'websiteUuid': '2f6f48f3-18e3-43f6-8119-514f2a02f537'
        }

        try:
            response = self.session.get(
                self.get_product_urls()[0],
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract products from response
            if 'result' in data:
                soup = BeautifulSoup(data['result'], 'html.parser')
                product_divs = soup.find_all('div', class_='hr-search-overlay-product')
                
                for div in product_divs:
                    try:
                        # Extract product info
                        title_elem = div.find('p', class_='hr-search-overlay-product-title')
                        name = title_elem.text.strip() if title_elem else None
                        
                        if not name or 'barebells' not in name.lower():
                            continue
                        # Extract price
                        price_elem = div.find('p', class_='hr-search-overlay-product-price-sale')
                        if price_elem:
                            price = float(price_elem.text.strip().replace('kr', '').strip())
                        
                        # Extract URL
                        url_elem = div.find('a', class_='hr-search-overlay-product-link')
                        url = url_elem['href'] if url_elem else None
                        
                        # Check availability
                        in_stock_elem = div.find('p', class_='hr-inStock')
                        available = bool(in_stock_elem)
                        
                        # Extract package size from name
                        package_size = None
                        if name:
                            size_match = re.search(r'(\d+)x\d+[gm]l?', name)
                            if size_match:
                                package_size = int(size_match.group(1))
                            elif '12-pack' in name.lower():
                                package_size = 12
                            elif '18x' in name.lower():
                                package_size = 18
                        
                        if name and price and url:
                            product = Product(
                                name=name,
                                price=price,
                                url=url,
                                store='sportkost',
                                package_size=package_size,
                                per_unit_price=price / package_size if package_size else None,
                                available=available
                            )
                            products.append(product)
                            
                    except Exception as e:
                        logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                        continue
                        
        except Exception as e:
            logging.error(f"Error with SportkostScraper: {str(e)}")
            
        return products
