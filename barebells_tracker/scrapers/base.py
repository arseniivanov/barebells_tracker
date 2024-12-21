from abc import ABC, abstractmethod
import requests
import logging
from typing import Dict, List
from ..models.product import Product

class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def get_headers(self) -> Dict:
        """Return headers required for the specific vendor."""
        pass

    @abstractmethod
    def get_product_urls(self) -> List[str]:
        """Return list of URLs to scrape for this vendor."""
        pass

    @abstractmethod
    def parse_products(self, response_data: Dict) -> List[Product]:
        """Parse the response data into Product objects."""
        pass

    def scrape_products(self) -> List[Product]:
        """Main scraping method - can be overridden if needed."""
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
                data = response.json()
                products.extend(self.parse_products(data))
            except Exception as e:
                logging.error(f"Error scraping {url}: {str(e)}")
                continue
        
        return products
