import logging
from typing import Dict, List
import json
from ..models.product import Product
from .base import BaseScraper

class ICAScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # ICA store ID - could be made configurable
        self.store_id = "1088004"
    
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'application/json; charset=utf-8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'https://handlaprivatkund.ica.se/stores/{self.store_id}/search?q=barebells',
            'Connection': 'keep-alive',
            'Cookie': (
                'OptanonConsent=isGpcEnabled=0&datestamp=Sat+Dec+21+2024+11%3A18%3A55+GMT%2B0100+'
                '(Central+European+Standard+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&'
                'identifierType=Cookie+Unique+Id&hosts=&consentId=b42583c5-e342-494e-b0e4-94be85bd1a12&'
                'interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2C'
                'C0002%3A0%2CC0004%3A0&iType=2&intType=2&geolocation=SE%3BM&AwaitingReconsent=false; '
                'AWSALB=PVm2oVmBikCjhW49R34ZRLonahpgejF8Z3Ie/W069FpWkvW//0lxNBhRVFPK5xZU3jpdHZoBIgfizegwJaQpFh63vnir33G3fA1vHPa8FxTKU7d1y7oplWQras6M; '
                'AWSALBCORS=PVm2oVmBikCjhW49R34ZRLonahpgejF8Z3Ie/W069FpWkvW//0lxNBhRVFPK5xZU3jpdHZoBIgfizegwJaQpFh63vnir33G3fA1vHPa8FxTKU7d1y7oplWQras6M'
            )
        }

    def get_product_urls(self) -> List[str]:
        return [f'https://handlaprivatkund.ica.se/stores/{self.store_id}/api/v5/products/search?offset=0&term=barebells']

    def parse_products(self, data: Dict) -> List[Product]:
        products = []
        
        # The products are in the entities/product section of the response
        product_entries = data.get('entities', {}).get('product', {})
        
        for product_id, product_data in product_entries.items():
            try:
                name = product_data.get('name', '')
                
                # Skip non-Barebells products
                if 'barebells' not in name.lower():
                    continue
                
                # Get price - ICA provides it in a nested structure
                price_data = product_data.get('price', {}).get('current', {})
                if not price_data:
                    continue
                    
                price = float(price_data.get('amount', 0))
                
                # Get availability
                available = product_data.get('available', False)
                
                # Construct URL
                url = f"https://handlaprivatkund.ica.se/stores/{self.store_id}/products/{product_data.get('retailerProductId', '')}"
                
                # Extract package size from name or size
                package_size = None
                size_info = product_data.get('size', {}).get('value', '')
                
                # Try to get package size from the name first
                if '12-pack' in name.lower():
                    package_size = 12
                elif '18 st' in name.lower():
                    package_size = 18
                
                # If no size found in name, try to parse from size info
                if not package_size and size_info:
                    # Size info is typically in format "0.055kg" for single bars
                    try:
                        size_value = float(size_info.replace('kg', ''))
                        if abs(size_value - 0.055) < 0.01:  # Single bar
                            package_size = 1
                        elif abs(size_value - 0.040) < 0.01:  # Single chewy bar
                            package_size = 1
                    except ValueError:
                        pass
                
                # Use price as final fallback for package size detection
                if not package_size:
                    package_size = 12 if price > 100 else 1
                
                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='ica',
                    package_size=package_size,
                    available=available
                )
                
                products.append(product)
                logging.info(f"Found product: {name} at {price} SEK")
                
            except Exception as e:
                logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return products
