"""Facebook Marketplace classifieds adapter with localized simulation fallback."""

import os
import random
import re
import sys
import urllib.parse
from typing import List, Optional, Dict, Any

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from .base import BaseAdapter
    from ..models import Listing, BOMItem
except ImportError:
    from adapters.base import BaseAdapter
    from models import Listing, BOMItem


class FacebookMarketplaceAdapter(BaseAdapter):
    """Adapter for Facebook Marketplace classifieds with simulated local listings."""

    NEIGHBORHOODS = [
        "West Suburbs", "Industrial Park", "North Shore", "Southside Workshop",
        "East Valley", "Hills District", "Bayside", "River District"
    ]

    SELLER_NAMES = [
        "Dave (Metal Fab Hobbyist)", "Sarah M. (Pottery Studio)", "Tom R. (BBQ & Smoker Builds)",
        "Precision Fab Cleanout", "Alex K. (Home Renovations)", "Mark T. (Boilermaker)",
        "Gareth (DIY Blacksmith)", "Mike S. (Catering Maintenance)"
    ]

    def __init__(self, default_currency: str = "USD"):
        super().__init__(platform_name="facebook_marketplace", default_currency=default_currency)
        self.base_url = "https://www.facebook.com/marketplace"

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
        """Performs search on Facebook Marketplace with simulation fallback."""
        encoded_q = urllib.parse.quote_plus(query)
        marketplace_url = f"{self.base_url}/search/?query={encoded_q}&exact=false"

        results: List[Listing] = []
        if not mock:
            html_content = self._fetch_url(marketplace_url, timeout=3)
            if html_content and "checkpoint" not in html_content.lower():
                # Extract structured marketplace listings if accessible
                item_matches = re.findall(
                    r'"marketplace_listing_title":\s*"([^"]+)".*?"formatted_price":\s*\{\s*"text":\s*"([^"]+)"',
                    html_content
                )
                if not item_matches:
                    # Alternative pattern: link with item ID and title
                    item_matches = re.findall(
                        r'<a[^>]*href="/marketplace/item/(\d+)/?"[^>]*aria-label="([^"]+)"',
                        html_content
                    )
                    # Convert to (title, price_str)
                    reformatted = []
                    for item_id_match, label in item_matches:
                        price_search = re.search(r'\$([0-9]+(?:\.[0-9]{2})?)', label)
                        price_val = price_search.group(1) if price_search else "20.00"
                        reformatted.append((label, price_val))
                    item_matches = reformatted

                for idx, (title, price_str) in enumerate(item_matches[:max_results]):
                    price_clean = re.sub(r"[^\d.]", "", price_str)
                    try:
                        price_val = float(price_clean)
                    except ValueError:
                        price_val = 20.0
                    status, note = self.check_safety(title)
                    results.append(Listing(
                        id=self._generate_deterministic_id("fb_live", title, idx),
                        title=title.strip(),
                        price=price_val,
                        currency=self.default_currency,
                        platform=self.platform_name,
                        seller="Facebook Marketplace Seller",
                        condition="used",
                        location=location,
                        distance_km=round(min(5.0, radius_km), 1),
                        url=marketplace_url,
                        matched_part_number=part_item.part_number if part_item else "CUSTOM",
                        is_surplus="offcut" in title.lower() or "surplus" in title.lower() or "scrap" in title.lower(),
                        safety_status=status,
                        safety_note=note,
                        unit_qty_included=1
                    ))

        if not results:
            results = self._simulate_listings(query, location, radius_km, max_results, part_item, marketplace_url)

        return results

    def _simulate_listings(
        self,
        query: str,
        location: str,
        radius_km: float,
        max_results: int,
        part_item: Optional[BOMItem],
        base_search_url: str
    ) -> List[Listing]:
        listings: List[Listing] = []
        base_cost = part_item.estimated_unit_cost if part_item else 20.0
        part_num = part_item.part_number if part_item else "PO-GEN-001"
        cat = part_item.category if part_item else "General"

        rng = random.Random(f"fb_{query}_{location}_{part_num}")

        pool = []
        if cat == "Sheet Metal":
            pool = [
                ("304 Stainless Steel Sheet Drops & Laser Remnants (1.5mm / 2mm)", 0.40, "surplus", True, 1),
                ("Stainless Steel Sheet Offcut - AISI 304 Food Grade (1.5mm thick)", 0.48, "surplus", True, 1),
                ("430 Brushed Stainless Shroud / Cover Sheet Offcuts", 0.52, "surplus", True, 1),
                ("Metal Fab Shop Clearout - Stainless Sheet Drops", 0.38, "surplus", True, 1),
                ("Galvanized Sheet Offcut Lot - 1.5mm zinc sheet", 0.20, "surplus", True, 1)
            ]
        elif cat == "Refractory Stone":
            pool = [
                ("Cordierite Kiln Shelf Tile 340mm x 340mm (High Temp 1200C)", 0.50, "surplus", True, 1),
                ("Square Pizza Stone 13\" Cordierite Ceramic - Moving Sale", 0.58, "used", False, 1),
                ("Biscotto Clay Stone for Neapolitan Pizza Oven (Brand New)", 0.85, "new", False, 1),
                ("Natural Marble Slab 350mm - Great for Baking", 0.35, "used", False, 1)
            ]
        elif cat == "Insulation":
            pool = [
                ("Ceramic Fiber Blanket 25mm 8# Kaowool - 24\" x 24\" Remnant", 0.45, "surplus", True, 1),
                ("Morgan Cerablanket High Temp 1260C Roll End", 0.52, "surplus", True, 1),
                ("Ceramic Fiber Gasket Paper 3mm Strip Lot", 0.48, "surplus", True, 1),
                ("Pink Fiberglass Batt Offcuts - Free to Collector", 0.05, "surplus", True, 1)
            ]
        elif cat == "Burner/Fuel":
            pool = [
                ("High Output Propane Burner Tube 25k BTU & Air Shutter", 0.62, "new", False, 1),
                ("Gas Safety Shutoff Valve with Thermocouple Sensor M8", 0.55, "surplus", True, 1),
                ("Steel Braided Propane Hose with Adjustable High Pressure Regulator", 0.65, "used", False, 1),
                ("Push Button Spark Generator Piezo Igniter & Electrode", 0.45, "new", False, 1)
            ]
        elif cat == "Fasteners":
            pack_size = 50
            pool = [
                (f"Surplus Stainless Steel Fasteners: M5 Button Head & Flange Nuts ({pack_size}pc)", 0.45, "surplus", True, pack_size),
                (f"A2 Stainless Rivets 4mm Dome Head (Sealed Pack of {pack_size})", 0.55, "new", False, pack_size),
                (f"M6 Stainless Thumb Screws Knurled Detent (Pack of 5)", 0.60, "new", False, 5)
            ]
        elif cat == "Hardware":
            pool = [
                ("0-500C Stainless Dial Thermometer with Long Probe for Smoker/Oven", 0.60, "new", False, 1),
                ("High-Temp Silicone Leg Caps 25mm (Set of 4)", 0.50, "new", False, 1),
                ("Stainless Sheet Metal Handle with Hardwood Grip", 0.55, "used", False, 1)
            ]
        elif cat == "Consumables":
            pool = [
                ("Refractory Fire Cement 1250C Sealant Tub (Brand New)", 0.65, "new", False, 1),
                ("High Heat Silicone RTV 600F Red Tube - Workshop Extra", 0.50, "surplus", True, 1),
                ("Anti-Seize Copper Compound 1000C (Unopened)", 0.55, "surplus", True, 1)
            ]
        else:
            pool = [
                (f"Facebook Marketplace: {query} (Surplus workshop stock)", 0.50, "surplus", True, 1),
                (f"Facebook Marketplace: {query} (Like new condition)", 0.65, "used", False, 1)
            ]

        for i, (title_tpl, factor, cond, is_surp, unit_qty) in enumerate(pool[:max_results]):
            total_nominal_val = base_cost * unit_qty
            price = max(1.5, round(total_nominal_val * factor, 2))
            min_dist = min(0.5, radius_km * 0.2)
            max_dist = max(min_dist, min(radius_km, 35.0))
            dist = round(rng.uniform(min_dist, max_dist), 1)
            neighborhood = rng.choice(self.NEIGHBORHOODS)
            seller = rng.choice(self.SELLER_NAMES)
            status, note = self.check_safety(title_tpl)

            item_id = self._generate_deterministic_id("fb", query, location, i)
            listings.append(Listing(
                id=item_id,
                title=title_tpl,
                price=price,
                currency=self.default_currency,
                platform=self.platform_name,
                seller=seller,
                condition=cond,
                location=f"{neighborhood}, {location}",
                distance_km=dist,
                url=f"{self.base_url}/item/{item_id}/",
                matched_part_number=part_num,
                spec_match_score=0.90 if status == "safe" else 0.35,
                is_surplus=is_surp,
                safety_status=status,
                safety_note=note,
                unit_qty_included=unit_qty
            ))

        return listings
