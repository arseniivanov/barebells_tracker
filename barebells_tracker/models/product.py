from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class Product:
    name: str
    price: float
    url: str
    store: str
    per_unit_price: Optional[float] = None
    package_size: Optional[int] = None
    stock: Optional[int] = None
    available: bool = True

    def __post_init__(self):
        """
        Post-initialization processing:
        1. Detect package size if not provided
        2. Calculate per_unit_price if not provided
        """
        self._detect_package_size()
        self._calculate_per_unit_price()

    def _detect_package_size(self):
        """Detect package size using various methods."""
        if self.package_size is not None:
            return

        # Method 1: Check name for explicit package size
        if '12-pack' in self.name.lower():
            self.package_size = 12
            return

        # Method 2: Check for patterns like "12x55g" or "12 st"
        patterns = [
            r'(\d+)\s*x\s*\d+g',  # matches "12x55g"
            r'(\d+)\s*st\b',      # matches "12 st"
            r'(\d+)\s*pack\b',    # matches "12 pack"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.name.lower())
            if match:
                self.package_size = int(match.group(1))
                return

        # Method 3: Price-based heuristic
        # If price is above 100 SEK and no other size detected, likely a multipack
        if self.price > 100:
            self.package_size = 12  # Assume 12-pack as it's most common
        else:
            self.package_size = 1

    def _calculate_per_unit_price(self):
        """Calculate per_unit_price if not provided but package_size exists."""
        if self.per_unit_price is None and self.package_size:
            self.per_unit_price = self.price / self.package_size

    @property
    def is_single(self) -> bool:
        """Check if this is a single bar."""
        return self.package_size == 1

    @property
    def is_multipack(self) -> bool:
        """Check if this is a multipack."""
        return self.package_size > 1 if self.package_size else False
