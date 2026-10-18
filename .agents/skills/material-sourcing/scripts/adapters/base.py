"""Base adapter class for material and classifieds scrapers with simulation fallback."""

import abc
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from typing import List, Dict, Optional, Any

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from ..models import Listing, BOMItem
except ImportError:
    from models import Listing, BOMItem

logger = logging.getLogger(__name__)


class BaseAdapter(abc.ABC):
    """Abstract base class for all classifieds, search, and supplier adapters."""

    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]

    # Global high-heat safety hazards across all physical categories
    HAZARDS = [
        (re.compile(r"\b(galvaniz(?:ed|ing)?|galv|zinc\s*coat(?:ed)?|zinc\s*plat(?:ed)?)\b", re.I),
         "HAZARD: Zinc vaporizes above 200°C releasing toxic zinc oxide fumes causing metal fume fever. Prohibited for food-contact pizza ovens."),
        (re.compile(r"\b(cadmium|cad\s*plat(?:ed)?|lead\s*solder|lead\s*plat(?:ed)?)\b", re.I),
         "HAZARD: Cadmium and lead are heavy metal neurotoxins that volatilize at high oven temperatures. Strictly prohibited in food equipment."),
        (re.compile(r"\b(granite|marble|slate|untreated\s*concrete|window\s*glass)\b", re.I),
         "HAZARD: Stone/glass lacks thermal shock resistance; contains trapped moisture and explodes violently at 450°C+."),
        (re.compile(r"\b(yellow\s*fiberglass|pink\s*fiberglass|rockwool\s*with\s*resin|asbestos|polystyrene|polyurethane\s*foam|expanding\s*foam)\b", re.I),
         "HAZARD: Organic resin binders or polymer foam combust emitting toxic acrolein and formaldehyde smoke. Asbestos is a carcinogenic hazard. Only 1260°C refractory ceramic blanket allowed."),
        (re.compile(r"\b(acrylic\s*caulk|bathroom\s*silicone|polyurethane\s*sealant|epoxy\s*non-heat)\b", re.I),
         "HAZARD: Non-food grade silicone, caulk, or epoxy releases toxic vapors. Must use food-safe high-temp silicone (up to 315°C) or fire mortar."),
        (re.compile(r"\b(painted\s*steel|powder\s*coat(?:ed)?\s*steel)\b", re.I),
         "HAZARD: Paint and powder coatings decompose into toxic vapors above 200°C. Only bare AISI 304/430 stainless steel allowed in hot chamber.")
    ]

    def __init__(self, platform_name: str, default_currency: str = "USD"):
        self.platform_name = platform_name
        self.default_currency = default_currency

    def check_safety(self, text: str) -> tuple[str, str]:
        """Inspects text for dangerous materials. Returns (safety_status, safety_note)."""
        for pattern, note in self.HAZARDS:
            if pattern.search(text):
                return "hazard", note
        if re.search(r"\b(mild\s*steel|uncoated\s*carbon\s*steel)\b", text, re.I):
            return "warning", "Warning: Non-stainless carbon steel rusts rapidly under thermal vapor cycling."
        return "safe", ""

    def _fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 5) -> Optional[str]:
        """Safely fetches URL content using standard library with user-agent rotation."""
        req_headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(url, headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return response.read().decode("utf-8", errors="replace")
        except Exception as e:
            logger.debug("Fetch failed for %s: %s", url, e)
            return None
        return None

    @abc.abstractmethod
    def search(
        self,
        query: str,
        location: str = "Local",
        radius_km: float = 50.0,
        max_results: int = 5,
        condition: Optional[str] = None,
        mock: bool = False,
        part_item: Optional[BOMItem] = None
    ) -> List[Listing]:
        """Executes a search and returns standardized Listings."""
        pass

    def _generate_deterministic_id(self, prefix: str, *args) -> str:
        """Generates a reproducible unique ID for listings."""
        key = "_".join(str(a) for a in args)
        h = hashlib.md5(key.encode("utf-8")).hexdigest()[:8]
        return f"{prefix}_{h}"
