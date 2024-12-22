import logging
from typing import List, Optional, Dict, Set
from .models.product import Product
from .scrapers.base import BaseScraper
from .utils import sorting, filtering

class BarebellsTracker:
    def __init__(self, scrapers: Optional[List[BaseScraper]] = None):
        """Initialize tracker with optional list of scrapers."""
        self.scrapers = scrapers or []
        self._products: List[Product] = []
        self.excluded_patterns: Set[str] = set()  # Patterns to exclude
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def add_scraper(self, scraper: BaseScraper) -> None:
        """Add a new scraper to the tracker."""
        self.scrapers.append(scraper)
        
    def add_exclusion_pattern(self, pattern: str) -> None:
        """Add a pattern to exclude from results."""
        self.excluded_patterns.add(pattern.lower())
        
    def remove_exclusion_pattern(self, pattern: str) -> None:
        """Remove a pattern from exclusions."""
        self.excluded_patterns.discard(pattern.lower())
        
    def clear_exclusion_patterns(self) -> None:
        """Clear all exclusion patterns."""
        self.excluded_patterns.clear()
        
    def get_exclusion_patterns(self) -> Set[str]:
        """Get current exclusion patterns."""
        return self.excluded_patterns.copy()
    
    def run(self) -> List[Product]:
        """Run all scrapers and collect products."""
        self._products = []
        for scraper in self.scrapers:
            try:
                products = scraper.scrape_products()
                self._products.extend(products)
            except Exception as e:
                logging.error(f"Error with scraper {scraper.__class__.__name__}: {str(e)}")
        return self._products
    
    def get_products(self, 
                    store: Optional[str] = None,
                    package_size: Optional[int] = None,
                    min_price: Optional[float] = None,
                    max_price: Optional[float] = None,
                    only_available: bool = True,
                    min_stock: Optional[int] = None,
                    sort_by: Optional[str] = None,
                    reverse_sort: bool = False,
                    apply_exclusions: bool = True) -> List[Product]:
        """Get filtered and sorted products."""
        products = self._products
        
        # Apply filters
        if store:
            products = filtering.filter_by_store(products, store)
        
        if package_size is not None:
            products = filtering.filter_by_package_size(products, package_size)
        
        if min_price is not None or max_price is not None:
            products = filtering.filter_by_price_range(products, min_price, max_price)
        
        if only_available:
            products = filtering.filter_available(products)
        
        if min_stock is not None:
            products = filtering.filter_in_stock(products, min_stock)
            
        # Apply pattern exclusions if enabled
        if apply_exclusions and self.excluded_patterns:
            products = filtering.filter_by_excluded_patterns(products, self.excluded_patterns)
        
        # Apply sorting
        if sort_by:
            if sort_by == 'price':
                products = sorting.sort_by_price(products, reverse_sort)
            elif sort_by == 'unit_price':
                products = sorting.sort_by_per_unit_price(products, reverse_sort)
            elif sort_by == 'package_size':
                products = sorting.sort_by_package_size(products, reverse_sort)
        
        return products
    
    def get_store_summary(self) -> Dict[str, int]:
        """Get summary of product counts by store."""
        summary = {}
        for product in self._products:
            summary[product.store] = summary.get(product.store, 0) + 1
        return summary

    def get_best_deals(self, package_size: Optional[int] = None, limit: int = 5, log: bool = False) -> List[Product]:
        """
        Get the best deals for given package size, removing duplicate prices from same store.
        """
        products = self._products

        if log:
            logging.info(f"Initial product count: {len(products)}")
        
        # Apply initial filters
        if package_size is None:
            products = filtering.filter_singles(products)
            products = filtering.filter_by_price_range(products, max_price=100)
        else:
            products = filtering.filter_by_package_size(products, package_size)
        
        # Filter for available products and apply exclusions
        products = filtering.filter_available(products)
        if self.excluded_patterns:
            products = filtering.filter_by_excluded_patterns(products, self.excluded_patterns)
        
        # Sort by appropriate price metric
        if package_size and package_size > 1:
            products = sorting.sort_by_per_unit_price(products)
        else:
            products = sorting.sort_by_price(products)
        
        # Remove duplicate prices from same store
        seen_prices = {}  # Dictionary to track {(store, price): product}
        unique_products = []
        
        for product in products:
            price_key = (product.store, product.price if package_size is None else product.per_unit_price)
            if price_key not in seen_prices:
                seen_prices[price_key] = product
                unique_products.append(product)
        
        # Get final results
        final_products = unique_products[:limit]
        
        # Debug log the results
        if log:
            for product in final_products:
                logging.info(f"Selected product: {product.name} at {product.price} SEK")
        
        return final_products

    def get_price_range(self, package_size: Optional[int] = None) -> Dict[str, float]:
        """Get price range statistics for given package size, respecting exclusions."""
        # Start with base filtering
        if package_size is None:
            products = filtering.filter_singles(self._products)
            products = filtering.filter_by_price_range(products, max_price=100)
        else:
            products = filtering.filter_by_package_size(self._products, package_size)
        
        # Apply availability filter and exclusions
        products = filtering.filter_available(products)
        if self.excluded_patterns:
            products = filtering.filter_by_excluded_patterns(products, self.excluded_patterns)
        
        if not products:
            return {
                'min_price': None,
                'max_price': None,
                'avg_price': None
            }
        
        # Use the appropriate price metric
        if package_size and package_size > 1:
            prices = [p.per_unit_price for p in products if p.per_unit_price is not None]
        else:
            prices = [p.price for p in products]
        
        return {
            'min_price': min(prices) if prices else None,
            'max_price': max(prices) if prices else None,
            'avg_price': sum(prices) / len(prices) if prices else None
        }

def create_default_tracker() -> BarebellsTracker:
    """Create a tracker instance with all available scrapers."""
    from .scrapers.tyngre import TyngreScraper
    from .scrapers.apotea import ApoteaScraper
    from .scrapers.apohem import ApohemScraper
    from .scrapers.meds import MedsScraper
    from .scrapers.torebrings import TorebringsScraper
    from .scrapers.sportkost import SportkostScraper
    from .scrapers.gymgrossisten import GymgrossistenScraper
    from .scrapers.mmsports import MMSportsScraper
    from .scrapers.hemkop import HemkopScraper
    from .scrapers.willys import WillysScraper
    from .scrapers.ica import ICAScraper
    
    scrapers = [
        TyngreScraper(),
        ApoteaScraper(),
        ApohemScraper(),
        MedsScraper(),
        TorebringsScraper(),
        SportkostScraper(),
        GymgrossistenScraper(),
        MMSportsScraper(),
        HemkopScraper(),
        WillysScraper(),
        ICAScraper()
    ]
    
    return BarebellsTracker(scrapers)
