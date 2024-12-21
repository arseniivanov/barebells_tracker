import re
import logging
from typing import Dict, List
from ..models.product import Product
from .base import BaseScraper


class WillysScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'content-type': 'application/json',
            'Connection': 'keep-alive',
            'Cookie': 'AWSALB=3Ip6475Qn2YrlLPJncvvQouYmgb6E7abb0fUhpMZMNATM77dRnfjqU4vAjV8fMoIdcprUqtvnBQyXearAl/ZQZHYDL9szWWKz04xXd1lzCwQhVdvPv/GUU+CjLZm; AWSALBCORS=3Ip6475Qn2YrlLPJncvvQouYmgb6E7abb0fUhpMZMNATM77dRnfjqU4vAjV8fMoIdcprUqtvnBQyXearAl/ZQZHYDL9szWWKz04xXd1lzCwQhVdvPv/GUU+CjLZm',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.willys.se/search?q=barebells&page=0&size=30']

    def parse_products(self, data: Dict) -> List[Product]:
        products = []
        
        # Check if we have product results
        results = data.get('results', [])
        
        for item in results:
            try:
                name = item.get('name', '')
                
                # Get base price
                base_price = float(item.get('priceValue', 0))
                
                # Check for promotional price
                price = base_price
                if item.get('potentialPromotions'):
                    for promo in item['potentialPromotions']:
                        if promo.get('price', {}).get('value'):
                            price = float(promo['price']['value'])
                            break
                
                # Extract product details
                url = f"https://www.willys.se/produkt/{item.get('code', '')}"
                available = not item.get('outOfStock', True)
                
                # Extract package size from productLine2 or displayVolume
                package_size = None
                display_volume = item.get('displayVolume', '')
                
                if display_volume:
                    # Common format is "55g" for single bars, or may contain multipack info
                    if 'ml' in display_volume.lower():
                        # This is a drink product
                        package_size = 1
                    elif '55g' in display_volume.lower():
                        package_size = 1
                    elif 'x' in display_volume.lower():
                        match = re.search(r'(\d+)\s*x', display_volume)
                        if match:
                            package_size = int(match.group(1))
                
                # Double check name for package size if not found
                if not package_size and '12-pack' in name.lower():
                    package_size = 12
                
                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='willys',
                    package_size=package_size,
                    per_unit_price=price / package_size if package_size else None,
                    available=available
                )
                
                products.append(product)
                if price != base_price:
                    logging.info(f"Found product: {name} at {price} SEK (promotional price, regular: {base_price} SEK)")
                else:
                    logging.info(f"Found product: {name} at {price} SEK")
                
            except Exception as e:
                logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return products
