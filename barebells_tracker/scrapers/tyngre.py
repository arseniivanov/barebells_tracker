import re
import logging
from typing import Dict, List
from ..models.product import Product
from .base import BaseScraper

class TyngreScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://tyngre.se/',
            'x-nextjs-data': '1',
            'Connection': 'keep-alive'
        }

    def get_product_urls(self) -> List[str]:
        return ['https://tyngre.se/_next/data/f-s3vWyN8RyJDoj27b6Bh/sv-SE/search/all/barebells.json?query=all&query=barebells']

    def parse_products(self, data: Dict) -> List[Product]:
        products = []
        blocks = data.get('pageProps', {}).get('page', {}).get('blocks', [])
        
        for block in blocks:
            if block.get('name') == 'SearchList' and block.get('props', {}).get('variant') == 'product':
                items = block.get('props', {}).get('items', [])
                
                for item in items:
                    try:
                        name = item['name']
                        price = float(item['priceAsNumber'])
                        url = 'https://tyngre.se' + item['href']
                        available = item.get('available', True)
                        
                        # Get stock information
                        stock = None
                        if 'items' in item and item['items']:
                            warehouses = item['items'][0].get('warehouses', [])
                            if warehouses:
                                stock = warehouses[0].get('stock', 0)
                        
                        # Extract package size
                        package_size = None
                        subheading = item.get('var_product_subheading_value')
                        if subheading:
                            match = re.search(r'(\d+)g x (\d+)st', subheading)
                            if match:
                                package_size = int(match.group(2))
                        
                        # For 12-packs in the name
                        if package_size is None and '12-pack' in name:
                            package_size = 12
                        
                        product = Product(
                            name=name,
                            price=price,
                            url=url,
                            store='tyngre',
                            package_size=package_size,
                            stock=stock,
                            available=available
                        )
                        products.append(product)
                        logging.info(f"Found product: {name} at {price} SEK")
                        
                    except Exception as e:
                        logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                        continue
        
        return products
