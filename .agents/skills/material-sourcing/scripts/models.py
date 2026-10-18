"""Data models for physical material sourcing, classifieds scraping, and BOM comparison."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json


@dataclass
class BOMItem:
    """Represents a component line item from the Bill of Materials."""
    part_number: str
    component_name: str
    material_spec: str
    qty: int
    category: str
    vendor_ref: str
    estimated_unit_cost: float
    sourcing_notes: str

    @property
    def total_estimated_cost(self) -> float:
        return round(self.qty * self.estimated_unit_cost, 2)


@dataclass
class QueryBundle:
    """Search queries targeted for retail, surplus classifieds, and local services."""
    part_number: str
    component_name: str
    category: str
    material_spec: str
    retail_queries: List[str] = field(default_factory=list)
    surplus_queries: List[str] = field(default_factory=list)
    local_service_queries: List[str] = field(default_factory=list)
    danger_keywords: List[str] = field(default_factory=list)


DEFAULT_EXCHANGE_RATES_TO_USD = {
    "USD": 1.0,
    "AUD": 0.65,
    "CAD": 0.74,
    "EUR": 1.08,
    "GBP": 1.28,
    "NZD": 0.60,
}


@dataclass
class Listing:
    """Discovered marketplace or vendor listing for a material."""
    id: str
    title: str
    price: float
    currency: str
    platform: str  # 'gumtree', 'facebook', 'google_shopping', 'industrial'
    seller: str
    condition: str  # 'new', 'surplus', 'used', 'salvage'
    location: str
    distance_km: float
    url: str
    matched_part_number: str
    spec_match_score: float = 1.0
    is_surplus: bool = False
    safety_status: str = "safe"  # 'safe', 'warning', 'hazard'
    safety_note: str = ""
    unit_qty_included: int = 1

    @property
    def unit_price(self) -> float:
        qty = max(1, self.unit_qty_included)
        val = self.price / qty
        return round(val, 3) if val < 1.0 else round(val, 2)

    def unit_price_in_usd(self, exchange_rates: Optional[Dict[str, float]] = None) -> float:
        """Converts unit price to USD baseline for accurate economic comparison."""
        rates = exchange_rates or DEFAULT_EXCHANGE_RATES_TO_USD
        rate = rates.get(self.currency.upper(), 1.0)
        val = self.unit_price * rate
        return round(val, 3) if val < 1.0 else round(val, 2)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["unit_price"] = self.unit_price
        d["unit_price_usd"] = self.unit_price_in_usd()
        return d


@dataclass
class SourcingComparison:
    """Comparison of a BOM item against discovered vendor and classified listings."""
    bom_item: BOMItem
    listings: List[Listing] = field(default_factory=list)

    @property
    def best_listing(self) -> Optional[Listing]:
        safe_listings = [l for l in self.listings if l.safety_status != "hazard"]
        if not safe_listings:
            return None
        return min(safe_listings, key=lambda l: l.unit_price_in_usd())

    @property
    def best_surplus_listing(self) -> Optional[Listing]:
        surplus = [l for l in self.listings if l.is_surplus and l.safety_status != "hazard"]
        if not surplus:
            return None
        return min(surplus, key=lambda l: l.unit_price_in_usd())

    @property
    def average_market_unit_price(self) -> float:
        safe_listings = [l for l in self.listings if l.safety_status != "hazard"]
        if not safe_listings:
            return self.bom_item.estimated_unit_cost
        avg = sum(l.unit_price_in_usd() for l in safe_listings) / len(safe_listings)
        return round(avg, 3) if avg < 1.0 else round(avg, 2)

    @property
    def unit_savings(self) -> float:
        best = self.best_listing
        if not best:
            return 0.0
        diff = self.bom_item.estimated_unit_cost - best.unit_price_in_usd()
        return round(diff, 3) if abs(diff) < 1.0 else round(diff, 2)

    @property
    def total_savings(self) -> float:
        best = self.best_listing
        if not best:
            return 0.0
        return round((self.bom_item.estimated_unit_cost - best.unit_price_in_usd()) * self.bom_item.qty, 2)

