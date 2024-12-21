import re
import logging
from typing import Dict, List
from ..models.product import Product 
from .base import BaseScraper
from bs4 import BeautifulSoup

class TorebringsScraper(BaseScraper):
    def get_headers(self) -> Dict:
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.torebrings.se/',
            'Cookie': 'PHPSESSID=0rci6gsloghuj0g2aniie7ccu3; cookiefirst-consent={"necessary":true,"performance":false,"functional":false,"advertising":false,"timestamp":1734769872,"type":"category","version":"4afb6991-371f-44c9-b519-c212d1862c69"}',
            'Upgrade-Insecure-Requests': '1'
        }

    def get_product_urls(self) -> List[str]:
        return ['https://www.torebrings.se/sok?q=barebells']
        
    def extract_price(self, price_text: str) -> float:
        """Extract price from text, handling various formats."""
        # Remove common non-price text
        price_text = price_text.replace('kr', '').strip()
        # Remove any spaces and replace comma with dot
        price_text = price_text.replace(' ', '').replace(',', '.')
        try:
            return float(price_text)*1.12
        except ValueError:
            logging.error(f"Could not parse price from: {price_text}")
            return 0.0
        
    def extract_package_info(self, text: str) -> tuple:
        """Extract package size and unit price from description text.
        Returns (package_size, unit_price)"""
        if not text:
            return None, None
        
        # First try to get the unit price directly from text like "(20,10 kr/st)"
        unit_match = re.search(r'\(([\d,]+)\s*kr/st\)', text)
        if unit_match:
            unit_price = self.extract_price(unit_match.group(1)) * 1.12
            return None, unit_price
        
        # Then look for package size in formats like "1*12x55gr"
        match = re.search(r'(\d+)\*(\d+)x\d+gr', text)
        if match:
            # Get the second number (12 in 1*12x55gr)
            return int(match.group(2)), None
            
        return None, None

    def parse_products(self, html_content: str) -> List[Product]:
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all pricing tables
        product_tables = soup.find_all('div', class_='pricing-table')
        
        for table in product_tables:
            try:
                # Check if it's a Barebells product
                title_div = table.find('div', class_='title')
                if not title_div or 'barebells' not in title_div.text.lower():
                    continue
                
                name = title_div.text.strip()
                
                # Get the product URL
                url_element = title_div.find('a', href=True)
                if url_element:
                    url = 'https://www.torebrings.se' + url_element['href']
                else:
                    continue
                
                # Get price information from the description div
                description = table.find('div', class_='description')
                if not description:
                    logging.error(f"No description div found for {name}")
                    continue
                
                # Find the campaignPrices span first
                campaign_span = description.find('span', class_='campaignPrices')
                if not campaign_span:
                    logging.error(f"No campaignPrices span found for {name}")
                    continue
                
                # Look for spans containing text that starts with a digit
                spans = campaign_span.find_all('span')
                price = None
                for span in spans:
                    span_text = span.text.strip()
                    if span_text and span_text[0].isdigit():
                        try:
                            price = float(span_text.replace(',', '.')) * 1.12
                            break
                        except:
                            continue

                if not price:
                    # Try getting it from the text content
                    try:
                        price_text = campaign_span.get_text()
                        # Look for text after "Förp.pris:" and before "kr"
                        if 'pris:' in price_text and 'kr' in price_text:
                            price_part = price_text.split('pris:')[1].split('kr')[0].strip()
                            price = float(price_part.replace(',', '.')) * 1.12
                    except Exception as e:
                        logging.error(f"Error extracting price from text: {price_text if 'price_text' in locals() else 'unknown'}")
                        logging.error(str(e))
                
                if not price:
                    logging.error(f"Could not find price for product {name}")
                    continue

                # Debug log the found price
                logging.debug(f"Found price for {name}: {price} SEK")
                
                # Get stock information
                stock_div = table.find('div', class_='lager')
                available = True
                stock = None
                if stock_div:
                    stock_text = stock_div.text.strip()
                    stock_match = re.search(r'Lager:\s*(\d+)', stock_text)
                    if stock_match:
                        stock = int(stock_match.group(1))
                        available = stock > 0
                
                # All Barebells products on Torebrings seem to be 12-packs
                # Double check the description for confirmation
                desc_text = description.get_text()
                package_size = 12  # Default for Barebells on Torebrings
                
                # Try to get the explicit unit price if available
                unit_price = None
                unit_match = re.search(r'\(([\d,]+)\s*kr/st\)', desc_text)
                if unit_match:
                    unit_price = self.extract_price(unit_match.group(1))
                
                product = Product(
                    name=name,
                    price=price,
                    url=url,
                    store='torebrings',
                    package_size=package_size,
                    per_unit_price=unit_price if unit_price else price / package_size,
                    stock=stock,
                    available=available
                )
                
                products.append(product)
                logging.info(f"Found product: {name} (12-pack) at {price} SEK")
                
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
