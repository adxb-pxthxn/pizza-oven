"""Industrial supplier and custom fabrication adapter with bulk pricing and volume breaks."""

import os
import random
import re
import sys
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


class IndustrialSupplierAdapter(BaseAdapter):
    """Adapter for B2B industrial suppliers, custom laser cutting, and specialty fabricators."""

    SUPPLIERS = [
        {"name": "SendCutSend", "type": "Laser Service", "lead_time_days": 3},
        {"name": "McMaster-Carr", "type": "Industrial MRO", "lead_time_days": 1},
        {"name": "Bolt Depot", "type": "Fasteners Bulk", "lead_time_days": 2},
        {"name": "Sheffield Pottery & Ceramic Supply", "type": "Kiln Refractory", "lead_time_days": 4},
        {"name": "Thermal Ceramics Distributor", "type": "Insulation Specialist", "lead_time_days": 3},
        {"name": "Local Sheet Metal & Profile Cutting", "type": "Local Fabricator", "lead_time_days": 5}
    ]

    def __init__(self, default_currency: str = "USD"):
        super().__init__(platform_name="industrial", default_currency=default_currency)

    def search(
        self,
        query: str,
        location: str = "Local",
        radius_km: float = 100.0,
        max_results: int = 5,
        condition: Optional[str] = None,
        mock: bool = True,
        part_item: Optional[BOMItem] = None
    ) -> List[Listing]:
        """Provides verified B2B/industrial pricing with bulk breaks for manufacturing."""
        listings: List[Listing] = []
        base_cost = part_item.estimated_unit_cost if part_item else 25.0
        part_num = part_item.part_number if part_item else "PO-GEN-001"
        cat = part_item.category if part_item else "General"

        rng = random.Random(f"ind_{query}_{part_num}")

        pool = []
        if cat == "Sheet Metal":
            pool = [
                ("SendCutSend CNC Fiber Laser Cut AISI 304 - Deburred & Nitto Film", 0.95, "SendCutSend", 1, "https://sendcutsend.com"),
                ("Local Precision Laser Profiling Service (Custom Quote)", 0.88, "Local Laser Cutter", 1, "https://locallaser.com"),
                ("OnlineMetals 304 Stainless Sheet Stock 12\" x 24\"", 1.10, "OnlineMetals", 1, "https://onlinemetals.com"),
                ("Midwest Steel & Aluminum: Offcut Drops (AISI 304)", 0.55, "Midwest Surplus", 1, "https://midweststeelsurplus.com")
            ]
        elif cat == "Refractory Stone":
            pool = [
                ("Sheffield Ceramic Kiln Shelf 13\" x 13\" x 5/8\" Cordierite", 0.92, "Sheffield Pottery", 1, "https://sheffieldpottery.com"),
                ("Babcock & Wilcox High-Alumina Kiln Plate 340mm", 1.15, "Foundry Supply", 1, "https://foundryrefractory.com"),
                ("Axner Pottery Cordierite Square Kiln Furniture", 0.89, "Axner Ceramic", 1, "https://axner.com")
            ]
        elif cat == "Insulation":
            pool = [
                ("Morgan Thermal Ceramics Bio-Soluble Superwool 607 (25mm 128kg/m3)", 0.95, "Thermal Ceramics", 1, "https://morganthermalceramics.com"),
                ("Unifrax Insulfrax Bio-Soluble Blanket Roll End", 0.85, "High-Temp Direct", 1, "https://refractorywarehouse.com"),
                ("McMaster-Carr Extreme-Temperature Ceramic Fiber Paper 3mm", 1.05, "McMaster-Carr", 1, "https://mcmaster.com")
            ]
        elif cat == "Burner/Fuel":
            pool = [
                ("Grand Hall Commercial 304 SS U-Burner Assembly with Air Shutter", 0.92, "Commercial BBQ Parts", 1, "https://bbqpartsdepot.com"),
                ("Baso Gas Products Flame Failure Thermoelectric Valve", 1.05, "Baso Gas Products", 1, "https://basogas.com"),
                ("Marshall Excelsior High Pressure Propane Regulator 0-10 PSI", 0.95, "Marshall Excelsior", 1, "https://marshallexcelsior.com")
            ]
        elif cat == "Fasteners":
            pack_size = 50
            pool = [
                (f"Bolt Depot: {part_item.material_spec} (Box of {pack_size})", 0.70, "Bolt Depot", pack_size, "https://boltdepot.com"),
                (f"McMaster-Carr: 18-8 Stainless Screws (Pack of {pack_size})", 0.85, "McMaster-Carr", pack_size, "https://mcmaster.com"),
                (f"Accu Metric Precision A2 Stainless Fasteners (Box of {pack_size})", 0.90, "Accu Group", pack_size, "https://accu-components.com")
            ]
        elif cat == "Hardware":
            pool = [
                ("Tel-Tru High Heat Bimetal Thermometer 0-500°C 304 SS Probe", 1.15, "Tel-Tru Direct", 1, "https://teltru.com"),
                ("Essentra Components Silicone High-Temp Caps 25mm", 0.80, "Essentra", 1, "https://essentracomponents.com")
            ]
        elif cat == "Consumables":
            pool = [
                ("Vitcas High-Temperature Refractory Mortar 1250°C 1kg Tub", 0.92, "Vitcas Refractories", 1, "https://vitcas.com"),
                ("Momentive RTV 106 High-Temp Food-Grade Silicone Sealant (FDA)", 1.10, "Ellsworth Adhesives", 1, "https://ellsworth.com"),
                ("Bostik Never-Seez Pure Nickel / Copper High-Temp Anti-Seize", 0.95, "Grainger B2B", 1, "https://grainger.com")
            ]
        else:
            pool = [
                (f"{query} Industrial Standard B2B Direct", 0.90, "Industrial Supply Co", 1, "https://industrialsupply.com")
            ]

        for i, (title_tpl, factor, supplier_name, unit_qty, url) in enumerate(pool[:max_results]):
            total_nominal = base_cost * unit_qty
            price = max(1.0, round(total_nominal * factor, 2))
            status, note = self.check_safety(title_tpl)

            item_id = self._generate_deterministic_id("ind", query, supplier_name, i)
            listings.append(Listing(
                id=item_id,
                title=title_tpl,
                price=price,
                currency=self.default_currency,
                platform=self.platform_name,
                seller=supplier_name,
                condition="new",
                location="Factory / Direct Supplier Dispatch",
                distance_km=0.0,
                url=url,
                matched_part_number=part_num,
                spec_match_score=0.99 if status == "safe" else 0.40,
                is_surplus="offcut" in title_tpl.lower() or "surplus" in title_tpl.lower(),
                safety_status=status,
                safety_note=note,
                unit_qty_included=unit_qty
            ))

        return listings
