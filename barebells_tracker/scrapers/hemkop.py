import re
import logging
from typing import Dict, List
from ..models.product import Product 
from .base import BaseScraper


class HemkopScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.hemkop.se/sok?q=barebells&sort=relevance',
            'X-NewRelic-ID': 'VQcCVVdaDhAHV1hVBAICU1A=',
            'Connection': 'keep-alive',
            'Cookie': 'AWSALB=xDpKSNKt27C31lHEfUv7qrk8feHrOqNH7mPDRjGCy35hXbvLrHbnE0Asa6Pmf0g8lowZgJaMSM7jVZ554aRnnL55lwofEPuFY2cpGl4IQfakffV+2TuGw2R3v/Z/; AWSALBCORS=xDpKSNKt27C31lHEfUv7qrk8feHrOqNH7mPDRjGCy35hXbvLrHbnE0Asa6Pmf0g8lowZgJaMSM7jVZ554aRnnL55lwofEPuFY2cpGl4IQfakffV+2TuGw2R3v/Z/; RequestId=4bec1f0e-9dba-45fc-9bab-7d7bc3bd7f21; JSESSIONID=Y0-5a2f9be0-8f62-4b4f-8677-a76e8fca0259',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.hemkop.se/search/multisearchComplete?q=barebells&page=0&size=30&show=Page&sort=relevance']

    def parse_products(self, data: Dict) -> List[Product]:
        products = []
        
        # Check if we have product results
        results = data.get('productSearchPageData', {}).get('results', [])
        
        for item in results:
            try:
                name = item.get('name', '')
                
                # Get base price
                base_price = float(item.get('priceValue', 0))
                
                # Check for promotional price
                promo_price = None
                if item.get('potentialPromotions'):
                    for promo in item['potentialPromotions']:
                        if promo.get('price', {}).get('value'):
                            promo_price = float(promo['price']['value'])
                            break
                
                # Use promotional price if available, otherwise base price
                price = promo_price if promo_price is not None else base_price
                
                # Extract product details
                url = f"https://www.hemkop.se/produkt/{item.get('code', '')}"
                available = not item.get('outOfStock', True)
                
                # Extract package size from productLine2 or displayVolume
                package_size = None
                product_line = item.get('productLine2', '')
                if product_line:
                    # Format is typically "BAREBELLS, 55g"
                    match = re.search(r'(\d+)g', product_line)
                    if match and int(match.group(1)) == 55:  # Single bar
                        package_size = 1
                    elif '12-pack' in name.lower():
                        package_size = 12
                
                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='hemkop',
                    package_size=package_size,
                    per_unit_price=price / package_size if package_size else None,
                    available=available
                )
                
                products.append(product)
                if promo_price:
                    logging.info(f"Found product: {name} at {price} SEK (promotional price, regular: {base_price} SEK)")
                else:
                    logging.info(f"Found product: {name} at {price} SEK")
                
            except Exception as e:
                logging.error(f"Error processing product {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return products
