from typing import List, Optional, Set
from ..models.product import Product
import logging

def filter_by_store(products: List[Product], store: str) -> List[Product]:
    """Filter products by store name."""
    return [p for p in products if p.store.lower() == store.lower()]

def filter_by_package_size(products: List[Product], size: Optional[int] = None) -> List[Product]:
    """
    Filter products by package size.
    If size is None, return single products (package_size == 1).
    If size is a number, return products with that exact package size.
    """
    if size is None:
        return [p for p in products if p.is_single]
    return [p for p in products if p.package_size == size]

def filter_by_price_range(
    products: List[Product], 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None
) -> List[Product]:
    """Filter products by price range."""
    filtered_products = products
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]
    
    return filtered_products

def filter_available(products: List[Product], only_available: bool = True) -> List[Product]:
    """Filter products by availability."""
    return [p for p in products if p.available == only_available]

def filter_in_stock(products: List[Product], min_stock: int = 1) -> List[Product]:
    """Filter products by stock level."""
    return [p for p in products if p.stock is not None and p.stock >= min_stock]

def filter_singles(products: List[Product]) -> List[Product]:
    """Filter for single bars only."""
    return [p for p in products if p.is_single]

def filter_multipacks(products: List[Product]) -> List[Product]:
    """Filter for multipacks only."""
    return [p for p in products if p.is_multipack]

def filter_by_excluded_patterns(products: List[Product], excluded_patterns: Set[str] = None) -> List[Product]:
    """
    Filter out products containing any of the excluded patterns in their name.
    Patterns are case-insensitive and match partial words.
    
    Args:
        products: List of products to filter
        excluded_patterns: Set of strings to exclude (e.g., {'chewy', 'soft'})
        
    Returns:
        Filtered list of products
    """
    if not excluded_patterns:
        return products
    
    filtered_products = []
    for product in products:
        name_lower = product.name.lower()
        should_include = True
        
        for pattern in excluded_patterns:
            if pattern.lower() in name_lower:
                logging.info(f"Excluding product due to pattern '{pattern}': {product.name}")
                should_include = False
                break
                
        if should_include:
            filtered_products.append(product)
            
    #logging.info(f"Filtered out {len(products) - len(filtered_products)} products with patterns: {excluded_patterns}")
    return filtered_products
