"""BOM analyzer and search query matrix generator for high-temperature pizza oven materials."""

import csv
import os
import re
import sys
from typing import Any, Dict, List, Optional

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from .models import BOMItem, QueryBundle
except ImportError:
    from models import BOMItem, QueryBundle


class BOMAnalyzer:
    """Parses BOM and generates optimized query bundles across retail, classifieds, and scrap channels."""

    # Safety rules and prohibited materials for high-temperature food equipment
    SAFETY_RULES = {
        "Sheet Metal": {
            "danger_keywords": ["galvanized", "galv", "zinc", "cadmium", "painted steel", "mild steel uncoated"],
            "warning": "CRITICAL HAZARD: Never use galvanized, zinc-plated, or painted steel inside or near the hot chamber. "
                       "Zinc vaporizes above 200°C producing toxic zinc oxide fumes (metal fume fever). AISI 304 stainless is strictly required for food contact."
        },
        "Refractory Stone": {
            "danger_keywords": ["granite", "marble", "slate", "glass", "concrete", "terracotta unrated", "wet stone"],
            "warning": "CRITICAL HAZARD: Granite, marble, slate, and architectural stones contain trapped moisture and crystalline silica. "
                       "They violently fracture/explode under rapid 450°C heating. Use only thermal shock-resistant cordierite ceramic or Biscotto clay."
        },
        "Insulation": {
            "danger_keywords": ["yellow fiberglass", "pink fiberglass", "rockwool with binder", "polystyrene", "polyurethane", "asbestos"],
            "warning": "CRITICAL HAZARD: Common residential fiberglass or mineral wool uses phenolic/resin binders that off-gas "
                       "toxic aldehydes and smoke above 180°C. Must use high-purity refractory ceramic fiber (RCF) or bio-soluble blanket (1260°C rated)."
        },
        "Burner/Fuel": {
            "danger_keywords": ["natural gas orifice", "unregulated", "indoor unvented", "acetylene"],
            "warning": "SAFETY NOTICE: Propane (LPG) requires appropriate jet orifice sizing (~0.8-1.0mm) and high-temp Flame Failure Devices (FFD). "
                       "Regulator must match burner design pressure (0-10 PSI or fixed 37 mbar)."
        },
        "Fasteners": {
            "danger_keywords": ["zinc plated", "grade 5 zinc", "galvanized bolts", "black oxide dry"],
            "warning": "CORROSION & FUME HAZARD: Zinc coatings burn off releasing fumes. Zinc-free A2-70 (304) or A4-80 (316) "
                       "stainless fasteners prevent thread seizure and thermal scaling."
        },
        "Consumables": {
            "danger_keywords": ["acrylic caulk", "bathroom silicone", "polyurethane sealant", "epoxy non-heat"],
            "warning": "TOXIC VAPOR HAZARD: Standard silicone emits acetic acid or organotin toxins at pizza baking temperatures. "
                       "Use only FDA food-contact approved high-temp silicone (up to 315°C) or sodium silicate refractory cement (up to 1250°C)."
        }
    }

    # Supplementary consumables required for building & maintaining the pizza oven
    SUPPLEMENTARY_CONSUMABLES = [
        BOMItem(
            part_number="PO-CN-001",
            component_name="High-Temp Refractory Mortar / Fireplace Cement",
            material_spec="Sodium silicate / refractory ceramic blend 1250°C rated, 300ml cartridge or tub",
            qty=1,
            category="Consumables",
            vendor_ref="Rutland / Meeco / Vitcas / Local Stove Supplier",
            estimated_unit_cost=11.50,
            sourcing_notes="Used for sealing perimeter joints and burner baffle mounting. Food-safe after full heat cure."
        ),
        BOMItem(
            part_number="PO-CN-002",
            component_name="Food-Grade High-Temp Silicone RTV Sealant",
            material_spec="Red high-temp silicone, 315°C (600°F) continuous, FDA 21 CFR 177.2600 compliant",
            qty=1,
            category="Consumables",
            vendor_ref="Permatex / J-B Weld / Loctite / McMaster",
            estimated_unit_cost=9.80,
            sourcing_notes="Used on external shroud joints and probe pass-throughs. Must be food contact safe."
        ),
        BOMItem(
            part_number="PO-CN-003",
            component_name="High-Temp Anti-Seize Thread Lubricant",
            material_spec="Copper / nickel based anti-seize paste, 1000°C rated, 50g tube",
            qty=1,
            category="Consumables",
            vendor_ref="Permatex / Loctite / Auto Parts Store",
            estimated_unit_cost=7.50,
            sourcing_notes="Prevents stainless screw galling and thread welding during high-temp cyclic expansion."
        )
    ]

    def __init__(self, bom_path: Optional[str] = None):
        if bom_path is None:
            # Default to repo root bom/bom.csv
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bom_path = os.path.abspath(os.path.join(current_dir, "../../../../bom/bom.csv"))
        self.bom_path = bom_path
        self.items: List[BOMItem] = []
        self._load_bom()

    @staticmethod
    def _extract_field(row: Dict[str, Any], candidate_keys: List[str], default: str = "") -> str:
        """Extracts field value matching any of the candidate header keys."""
        for k in candidate_keys:
            if k in row and row[k] is not None:
                val = str(row[k]).strip()
                if val:
                    return val
            # Case-insensitive header match
            for rk in row.keys():
                if rk and rk.strip().lower() == k.strip().lower() and row[rk] is not None:
                    val = str(row[rk]).strip()
                    if val:
                        return val
        return default

    def _load_bom(self):
        """Loads and parses the BOM CSV file with flexible column alias matching."""
        if not os.path.exists(self.bom_path):
            raise FileNotFoundError(f"BOM file not found at: {self.bom_path}")

        self.items = []
        with open(self.bom_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                if not row or not any(row.values()):
                    continue

                part_number = self._extract_field(row, ["Part Number", "PartNumber", "Part #", "Part", "ID"])
                component_name = self._extract_field(row, ["Component Name", "Component", "Name", "Description", "Item"])

                # Skip completely blank lines
                if not part_number and not component_name:
                    continue

                if not part_number:
                    part_number = f"PO-GEN-{idx:03d}"

                material_spec = self._extract_field(row, ["Material / Spec", "Material", "Spec", "Specification"])
                category = self._extract_field(row, ["Category", "Type", "Group"], default="Hardware")
                vendor_ref = self._extract_field(row, ["Vendor / Standard Reference", "Vendor", "Supplier", "Reference", "Source"])
                sourcing_notes = self._extract_field(row, ["Sourcing Notes", "Notes", "Comment", "Remarks"])

                qty_str = self._extract_field(row, ["Qty", "Quantity", "QTY", "count", "Count"], default="1")
                try:
                    qty = max(1, int(float(qty_str)))
                except (ValueError, TypeError):
                    qty = 1

                cost_str = self._extract_field(row, ["Estimated Unit Cost (USD)", "Unit Cost", "Cost", "Price", "Estimated Cost", "Est Unit Cost"], default="0.0")
                cost_clean = cost_str.replace("$", "").replace(",", "").strip()
                try:
                    cost = max(0.0, float(cost_clean))
                except (ValueError, TypeError):
                    cost = 0.0

                item = BOMItem(
                    part_number=part_number,
                    component_name=component_name,
                    material_spec=material_spec,
                    qty=qty,
                    category=category,
                    vendor_ref=vendor_ref,
                    estimated_unit_cost=cost,
                    sourcing_notes=sourcing_notes
                )
                self.items.append(item)

    def get_all_items(self, include_consumables: bool = True) -> List[BOMItem]:
        """Returns all BOM items, optionally including physical assembly consumables."""
        if include_consumables:
            return self.items + self.SUPPLEMENTARY_CONSUMABLES
        return list(self.items)

    def get_item_by_part_number(self, part_num: Optional[str]) -> Optional[BOMItem]:
        """Finds item by part number (e.g. PO-SM-001 or PO-ST-001)."""
        if not part_num:
            return None
        for item in self.get_all_items(include_consumables=True):
            if item.part_number.lower() == part_num.strip().lower():
                return item
        return None

    def get_items_by_category(self, category: str) -> List[BOMItem]:
        """Filters items by category."""
        return [i for i in self.get_all_items(include_consumables=True)
                if category.lower() in i.category.lower()]

    def generate_query_bundle(self, item: BOMItem) -> QueryBundle:
        """Generates tailored search queries across retail, classifieds, and local services."""
        part_num = item.part_number
        name = item.component_name
        spec = item.material_spec
        cat = item.category

        retail_queries = []
        surplus_queries = []
        local_service_queries = []
        danger_keywords = self.SAFETY_RULES.get(cat, {}).get("danger_keywords", [])

        # Categorical query generation logic
        if cat == "Sheet Metal":
            is_304 = "304" in spec
            is_430 = "430" in spec
            thickness_match = re.search(r"(\d+(?:\.\d+)?)\s*mm", spec)
            thickness = thickness_match.group(1) + "mm" if thickness_match else "1.5mm"
            grade = "304" if is_304 else ("430" if is_430 else "stainless")

            retail_queries = [
                f"{grade} stainless steel sheet {thickness}",
                f"{grade} stainless steel sheet plate cut to size",
                f"SendCutSend custom laser cutting {grade} stainless"
            ]
            surplus_queries = [
                f"stainless steel sheet offcut {grade}",
                f"{grade} stainless steel offcuts scrap",
                f"sheet metal drops {grade} stainless",
                f"scrap stainless steel sheet {thickness}",
                f"laser cut offcut stainless {grade}"
            ]
            local_service_queries = [
                "sheet metal laser cutting service near me",
                "custom fiber laser cutting stainless steel",
                "metal fabrication workshop drops offcuts",
                "scrap metal recycling stainless 304 clean sheet"
            ]

        elif cat == "Refractory Stone":
            retail_queries = [
                "cordierite pizza baking stone 335mm x 335mm",
                "cordierite kiln shelf 13 inch square",
                "biscotto di sorrento pizza stone tile 340mm",
                "high temperature pizza stone replacement 15mm"
            ]
            surplus_queries = [
                "cordierite kiln shelf used pottery",
                "pizza stone square 13 inch",
                "refractory firebrick baking stone",
                "pottery kiln furniture ceramic plate shelf"
            ]
            local_service_queries = [
                "pottery supply ceramic kiln shelf cordierite",
                "refractory supply firebrick pizza oven stone",
                "BBQ replacement parts ceramic pizza stone"
            ]

        elif cat == "Insulation":
            if "Blanket" in name:
                retail_queries = [
                    "ceramic fiber blanket 25mm 128kg 1260C",
                    "Kaowool insulation roll 1 inch 8#",
                    "Cerablanket bio soluble ceramic wool 1260C",
                    "forge insulation ceramic blanket 1 inch"
                ]
                surplus_queries = [
                    "ceramic fiber blanket offcut",
                    "kaowool roll leftover scrap",
                    "forge wool insulation roll surplus",
                    "high temp ceramic wool piece"
                ]
                local_service_queries = [
                    "refractory materials supplier ceramic insulation",
                    "foundry supplies ceramic blanket kaowool",
                    "wood stove insulation supply"
                ]
            else:  # Gasket / paper
                retail_queries = [
                    "high temp ceramic fiber paper 3mm 1200C",
                    "ceramic paper gasket roll 1/8 inch high temp",
                    "exhaust flange high temp gasket sheet 1200C"
                ]
                surplus_queries = [
                    "ceramic paper gasket scrap offcut",
                    "high temperature gasket sheet leftover"
                ]
                local_service_queries = [
                    "industrial gasket manufacturer ceramic paper",
                    "boiler gasket supply high temperature"
                ]

        elif cat == "Burner/Fuel":
            if "Burner" in name:
                retail_queries = [
                    "stainless steel U-burner propane 25000 BTU",
                    "propane gas burner tube assembly 7.5kW",
                    "pizza oven gas burner replacement BBQ"
                ]
                surplus_queries = [
                    "BBQ propane burner stainless steel U-tube",
                    "gas smoker burner tube assembly",
                    "outdoor pizza oven burner kit"
                ]
                local_service_queries = [
                    "gas appliance spare parts outdoor burner",
                    "BBQ repair service gas burner tubes"
                ]
            elif "Safety" in name or "Valve" in name or "FFD" in name:
                retail_queries = [
                    "gas flame failure safety valve thermocouple M8",
                    "gas safety valve FFD thermocouple BBQ",
                    "thermoelectric gas control valve propane"
                ]
                surplus_queries = [
                    "gas heater safety valve thermocouple",
                    "patio heater gas valve spare parts"
                ]
                local_service_queries = [
                    "commercial catering spares gas safety valve",
                    "gas appliance parts thermocouple valve"
                ]
            elif "Regulator" in name:
                retail_queries = [
                    "adjustable propane regulator 0-10 PSI braided hose",
                    "propane regulator hose QCC1 high pressure",
                    "fixed 37mbar propane gas regulator hose"
                ]
                surplus_queries = [
                    "propane regulator hose BBQ gas bottle",
                    "adjustable gas regulator high output"
                ]
                local_service_queries = [
                    "gas bottle equipment camping regulator hose",
                    "hardware store BBQ gas regulator"
                ]
            else:  # Igniter
                retail_queries = [
                    "piezo spark igniter push button ceramic electrode lead",
                    "BBQ push button piezo spark generator kit"
                ]
                surplus_queries = [
                    "BBQ igniter kit push button",
                    "gas heater piezo replacement"
                ]
                local_service_queries = [
                    "hardware store BBQ spare parts igniter"
                ]

        elif cat == "Fasteners":
            # Extract thread and length
            m_match = re.search(r"M\d+", spec)
            thread = m_match.group(0) if m_match else "M5"
            retail_queries = [
                f"{spec} pack of 50",
                f"{thread} stainless steel A2 button head screws DIN 7380",
                f"{thread} serrated flange locknuts DIN 6923 A2 stainless",
                f"McMaster-Carr {thread} stainless steel fasteners"
            ]
            surplus_queries = [
                f"stainless steel bolts nuts {thread} assortment",
                f"A2 stainless fasteners bulk lot workshop",
                f"stainless screws box surplus {thread}"
            ]
            local_service_queries = [
                "industrial fastener supplier stainless steel",
                "specialty bolt and nut distributor near me"
            ]

        elif cat == "Hardware":
            if "Thermometer" in name:
                retail_queries = [
                    "bimetal pizza oven thermometer 500C 900F stainless probe",
                    "BBQ smoker temperature gauge dial 0-500C"
                ]
                surplus_queries = [
                    "smoker thermometer dial high heat",
                    "wood oven temperature gauge probe"
                ]
                local_service_queries = [
                    "BBQ store thermometer replacement dial"
                ]
            else:
                retail_queries = [
                    f"{name} {spec}",
                    f"silicone foot caps 25mm high temp",
                    "knurled thumb screw M6 stainless steel"
                ]
                surplus_queries = [
                    f"{name} spare parts hardware surplus"
                ]
                local_service_queries = [
                    "hardware store specialty rubber silicone caps"
                ]

        elif cat == "Consumables":
            if "Mortar" in name or "Cement" in name:
                retail_queries = [
                    "refractory mortar 1250C fire cement high temperature",
                    "Rutland fireplace mortar refractory cement",
                    "Vitcas fire cement high temp sealant"
                ]
                surplus_queries = [
                    "fire cement refractory mortar leftover tub",
                    "kiln mortar refractory clay"
                ]
                local_service_queries = [
                    "wood stove fireplace supply refractory cement",
                    "pottery store high temperature kiln mortar"
                ]
            elif "Silicone" in name or "RTV" in name:
                retail_queries = [
                    "food grade high temp silicone RTV red 300C",
                    "FDA food contact high heat silicone sealant",
                    "Permatex high temp red silicone gasket maker"
                ]
                surplus_queries = [
                    "high temp red silicone RTV tube"
                ]
                local_service_queries = [
                    "auto parts food safe high temp silicone sealant",
                    "commercial kitchen equipment sealants"
                ]
            else:  # Anti-seize
                retail_queries = [
                    "copper anti seize paste high temp 1000C",
                    "stainless steel thread anti-seize lubricant"
                ]
                surplus_queries = [
                    "anti seize copper paste tube"
                ]
                local_service_queries = [
                    "auto parts store copper anti seize lubricant"
                ]

        else:
            retail_queries = [f"{name} {spec}"]
            surplus_queries = [f"{name} offcut scrap surplus"]
            local_service_queries = [f"{name} supplier near me"]

        return QueryBundle(
            part_number=part_num,
            component_name=name,
            category=cat,
            material_spec=spec,
            retail_queries=retail_queries,
            surplus_queries=surplus_queries,
            local_service_queries=local_service_queries,
            danger_keywords=danger_keywords
        )

    def generate_all_query_bundles(self) -> Dict[str, QueryBundle]:
        """Generates query bundles for every BOM component and consumable."""
        bundles = {}
        for item in self.get_all_items(include_consumables=True):
            bundles[item.part_number] = self.generate_query_bundle(item)
        return bundles
