from typing import List
from ..models.product import Product

def sort_by_price(products: List[Product], reverse: bool = False) -> List[Product]:
    """Sort products by price."""
    return sorted(products, key=lambda x: x.price, reverse=reverse)

def sort_by_per_unit_price(products: List[Product], reverse: bool = False) -> List[Product]:
    """Sort products by price per unit, ignoring None values."""
    products_with_unit_price = [p for p in products if p.per_unit_price is not None]
    products_without_unit_price = [p for p in products if p.per_unit_price is None]
    
    sorted_products = sorted(
        products_with_unit_price, 
        key=lambda x: x.per_unit_price, 
        reverse=reverse
    )
    return sorted_products + products_without_unit_price

def sort_by_package_size(products: List[Product], reverse: bool = False) -> List[Product]:
    """Sort products by package size, putting None values last."""
    products_with_size = [p for p in products if p.package_size is not None]
    products_without_size = [p for p in products if p.package_size is None]
    
    sorted_products = sorted(
        products_with_size, 
        key=lambda x: x.package_size, 
        reverse=reverse
    )
    return sorted_products + products_without_size
