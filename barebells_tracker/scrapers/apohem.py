import re
import logging
from typing import Dict, List
from ..models.product import Product
from .base import BaseScraper


class ApohemScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.apohem.se/sok?q=barebells',
            'content-type': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Cookie': 'Culture=sv-SE; EPiStateMarker=true',
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.apohem.se/barebells']

    def parse_products(self, data: Dict) -> List[Product]:
        products = []
        
        for product in data.get('products', []):
            try:
                name = product['displayName']
                price = float(product['price']['current']['inclVat'])
                url = 'https://www.apohem.se' + product['url']
                
                # Extract package size if available (e.g., from name)
                package_size = None
                if 'x' in name.lower() and 'g' in name.lower():
                    # Try to extract package size for multi-packs
                    match = re.search(r'(\d+)\s*x', name)
                    if match:
                        package_size = int(match.group(1))
                
                # Determine availability based on stock and buyable status
                available = (product.get('stock') != 'out' and 
                           product.get('buyable', True))
                
                # Convert stock status to numeric if possible
                stock = None
                if product.get('stock') == 'high':
                    stock = 50  # Arbitrary high number
                elif product.get('stock') == 'low':
                    stock = 5   # Arbitrary low number
                elif product.get('stock') == 'out':
                    stock = 0
                
                product_obj = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='apohem',
                    package_size=package_size,
                    per_unit_price=price / package_size if package_size else None,
                    stock=stock,
                    available=available
                )
                
                products.append(product_obj)
                logging.info(f"Found product: {name} at {price} SEK")
                
            except Exception as e:
                logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return products
