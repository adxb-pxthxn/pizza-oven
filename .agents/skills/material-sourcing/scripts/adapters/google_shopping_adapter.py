"""Google Shopping and Search aggregator adapter with simulation fallback."""

import html
import os
import random
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from typing import List, Optional

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from .base import BaseAdapter
    from ..models import Listing, BOMItem
except ImportError:
    from adapters.base import BaseAdapter
    from models import Listing, BOMItem


class GoogleShoppingAdapter(BaseAdapter):
    """Google Shopping and web search adapter for retail & commercial hardware prices."""

    RETAILERS = [
        "Amazon Commercial", "BBQ Replacement Parts Direct", "Wood Stove & Fireplace Supply",
        "Pottery & Ceramic Craft Supply", "SendCutSend Laser Service", "Bolt Depot Fasteners",
        "Grainger Industrial", "McMaster-Carr Supply"
    ]

    def __init__(self, default_currency: str = "USD"):
        super().__init__(platform_name="google_shopping", default_currency=default_currency)
        self.base_url = "https://www.google.com/search"

    def search(
        self,
        query: str,
        location: str = "National",
        radius_km: float = 500.0,
        max_results: int = 5,
        condition: Optional[str] = None,
        mock: bool = False,
        part_item: Optional[BOMItem] = None
    ) -> List[Listing]:
        encoded_q = urllib.parse.quote_plus(query)
        search_url = f"{self.base_url}?tbm=shop&q={encoded_q}&hl=en"

        results: List[Listing] = []
        if not mock:
            html_content = self._fetch_url(search_url, timeout=3)
            if html_content and "consent.google.com" not in html_content and "sorry/index" not in html_content:
                # Find h3 headers and bounded context up to next h3
                raw_blocks = re.findall(r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)', html_content, re.DOTALL)
                for idx, (title_raw, context_raw) in enumerate(raw_blocks[:max_results]):
                    title = re.sub(r'<[^>]+>', '', title_raw).strip()
                    if not title:
                        continue
                    price_match = re.search(r'\$([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?)', context_raw)
                    if not price_match:
                        continue
                    price_val = float(price_match.group(1).replace(",", ""))
                    status, note = self.check_safety(title)
                    results.append(Listing(
                        id=self._generate_deterministic_id("google_live", title, idx),
                        title=title,
                        price=price_val,
                        currency=self.default_currency,
                        platform=self.platform_name,
                        seller="Online Merchant",
                        condition="new",
                        location="Online Delivery",
                        distance_km=0.0,
                        url=search_url,
                        matched_part_number=part_item.part_number if part_item else "CUSTOM",
                        is_surplus=False,
                        safety_status=status,
                        safety_note=note,
                        unit_qty_included=1
                    ))

        if not results:
            results = self._simulate_listings(query, location, max_results, part_item, search_url)

        return results

    def _simulate_listings(
        self,
        query: str,
        location: str,
        max_results: int,
        part_item: Optional[BOMItem],
        search_url: str
    ) -> List[Listing]:
        listings: List[Listing] = []
        base_cost = part_item.estimated_unit_cost if part_item else 20.0
        part_num = part_item.part_number if part_item else "PO-GEN-001"
        cat = part_item.category if part_item else "General"

        rng = random.Random(f"google_{query}_{part_num}")

        pool = []
        if cat == "Sheet Metal":
            pool = [
                (f"SendCutSend CNC Laser Cut {part_item.component_name} (AISI 304)", 1.05, "SendCutSend", 1),
                (f"OnlineMetals: AISI 304 2B Stainless Sheet Cut to Size", 1.15, "OnlineMetals", 1),
                (f"Xometry Sheet Metal Fabrication Service", 1.25, "Xometry", 1),
                (f"Industrial Metal Supply: Stainless 304 Sheet 1.5mm", 0.95, "Industrial Metal Supply", 1)
            ]
        elif cat == "Refractory Stone":
            pool = [
                ("Cast Elegance Cordierite Pizza Stone 13.2\" Square (High-Density)", 1.00, "Amazon", 1),
                ("FibraMent-D Baking Stone 13.5\" x 13.5\" x 3/4\"", 1.35, "FibraMent Direct", 1),
                ("Pottery Studio Kiln Shelf Cordierite 340mm Square", 0.88, "Pottery Supply", 1),
                ("Pizzacraft Round Cordierite Baking Stone 13\"", 0.92, "BBQ Depot", 1)
            ]
        elif cat == "Insulation":
            pool = [
                ("Simond Store Ceramic Fiber Blanket 1\" 8# 1260°C (24\" x 12\")", 0.95, "Simond Store / Amazon", 1),
                ("Morgan Thermal Ceramics Superwool Bio-Soluble Blanket 25mm", 1.20, "Refractory Warehouse", 1),
                ("High Temperature Ceramic Fiber Paper Gasket Strip 3mm", 1.05, "McMaster-Carr", 1)
            ]
        elif cat == "Burner/Fuel":
            pool = [
                ("Stanbroil Stainless Steel BBQ U-Burner Tube 25,000 BTU", 0.98, "Amazon", 1),
                ("Copreci Gas Safety Valve FFD with Fast Thermocouple M8", 1.08, "Gas Appliance Spares", 1),
                ("Cavagna Adjustable 0-10 PSI Propane Regulator & Steel Hose", 1.02, "Hardware Distributor", 1),
                ("Universal BBQ Push-Button Piezo Spark Igniter Kit", 0.90, "Universal BBQ Parts", 1)
            ]
        elif cat == "Fasteners":
            pack_size = 50
            pool = [
                (f"Bolt Depot: {part_item.material_spec} (Box of {pack_size})", 0.85, "Bolt Depot", pack_size),
                (f"McMaster-Carr: Metric 304 Stainless Screws (Pack of {pack_size})", 1.10, "McMaster-Carr", pack_size),
                (f"Fastenal: A2-70 Stainless Steel Flange Locknuts (Box of {pack_size})", 0.95, "Fastenal", pack_size)
            ]
        elif cat == "Hardware":
            pool = [
                ("Smoker Thermometer 0-500°C Stainless Steel Bimetal Dial", 0.95, "Smoker Hardware Store", 1),
                ("High Temperature Silicone Leg Detent Caps 25mm", 1.00, "Hardware Store", 1),
                ("A2 Stainless Knurled Thumb Screws M6 x 15mm (Pack of 5)", 0.90, "McMaster-Carr", 1)
            ]
        elif cat == "Consumables":
            pool = [
                ("Rutland 1250°C Refractory Mortar Fireplace Cement 300ml", 1.00, "Home Depot / Stove Store", 1),
                ("Permatex 81878 Ultra Copper High-Temp RTV Silicone 315°C", 0.95, "AutoZone / Amazon", 1),
                ("Loctite LB 8008 High-Temp Copper Anti-Seize Paste 1000°C", 1.05, "Grainger", 1)
            ]
        else:
            pool = [
                (f"{query} Commercial Retail Standard", 1.00, "Online Supplier", 1),
                (f"{query} Premium High-Temp Specification", 1.20, "Industrial Merchant", 1)
            ]

        for i, (title_tpl, factor, seller, unit_qty) in enumerate(pool[:max_results]):
            total_nominal = base_cost * unit_qty
            price = max(1.0, round(total_nominal * factor, 2))
            status, note = self.check_safety(title_tpl)

            item_id = self._generate_deterministic_id("google", query, seller, i)
            listings.append(Listing(
                id=item_id,
                title=title_tpl,
                price=price,
                currency=self.default_currency,
                platform=self.platform_name,
                seller=seller,
                condition="new",
                location="Online Retail / Ships Nationally",
                distance_km=0.0,
                url=f"{search_url}#item={item_id}",
                matched_part_number=part_num,
                spec_match_score=0.98 if status == "safe" else 0.40,
                is_surplus=False,
                safety_status=status,
                safety_note=note,
                unit_qty_included=unit_qty
            ))

        return listings
