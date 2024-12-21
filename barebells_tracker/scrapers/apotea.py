import re
import logging
from typing import Dict, List, Optional
from ..models.product import Product
from .base import BaseScraper
from bs4 import BeautifulSoup

class ApoteaScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.apotea.se/sok?q=barebells']

    def extract_package_size(self, name: str) -> Optional[int]:
        """Extract package size from product name."""
        # Look for patterns like "12 st", "8 st", etc.
        match = re.search(r'(\d+)\s*st\b', name)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None

    def scrape_products(self) -> List[Product]:
        """Main scraping method - overridden for HTML handling."""
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

    def parse_products(self, html_content: str) -> List[Product]:
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all product blocks
        product_blocks = soup.find_all('div', class_='product-block-container')
        
        for block in product_blocks:
            try:
                # Get the article wrapper
                article_wrapper = block.find('div', class_='article-wrapper')
                if not article_wrapper:
                    continue

                # Get name
                name_div = article_wrapper.find('div', class_='name')
                if not name_div:
                    continue
                name = name_div.text.strip()
                
                # Only process Barebells products
                if 'barebells' not in name.lower():
                    continue
                
                # Get price
                price_tag = article_wrapper.find('div', class_='price-tag')
                if not price_tag:
                    continue
                price_text = price_tag.text.strip()
                price = float(price_text.replace('kr', '').strip())
                
                # Get URL
                url = 'https://www.apotea.se' + article_wrapper.get('data-article-url', '')
                
                # Extract package size
                package_size = self.extract_package_size(name)
                
                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='apotea',
                    package_size=package_size,
                    per_unit_price=price / package_size if package_size else None
                )
                products.append(product)
                
                # Log with package size info if present
                if package_size:
                    logging.info(f"Found multipack: {name} ({package_size} st) at {price} SEK")
                else:
                    logging.info(f"Found product: {name} at {price} SEK")
                
            except Exception as e:
                logging.error(f"Error processing product block: {str(e)}")
                continue
                
        return products
