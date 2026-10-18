"""Scraper and sourcing adapters."""

from .base import BaseAdapter
from .gumtree_adapter import GumtreeAdapter
from .facebook_marketplace_adapter import FacebookMarketplaceAdapter
from .google_shopping_adapter import GoogleShoppingAdapter
from .industrial_adapter import IndustrialSupplierAdapter

__all__ = [
    "BaseAdapter",
    "GumtreeAdapter",
    "FacebookMarketplaceAdapter",
    "GoogleShoppingAdapter",
    "IndustrialSupplierAdapter",
]
