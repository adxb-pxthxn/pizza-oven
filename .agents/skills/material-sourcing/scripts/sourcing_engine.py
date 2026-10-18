"""Sourcing engine orchestrating multi-platform scrapers, cost comparison, and safety audits."""

import json
import os
import sys
from typing import List, Dict, Optional, Any

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from .models import BOMItem, Listing, SourcingComparison
    from .bom_analyzer import BOMAnalyzer
    from .adapters import (
        GumtreeAdapter,
        FacebookMarketplaceAdapter,
        GoogleShoppingAdapter,
        IndustrialSupplierAdapter,
        BaseAdapter
    )
except ImportError:
    from models import BOMItem, Listing, SourcingComparison
    from bom_analyzer import BOMAnalyzer
    from adapters import (
        GumtreeAdapter,
        FacebookMarketplaceAdapter,
        GoogleShoppingAdapter,
        IndustrialSupplierAdapter,
        BaseAdapter
    )


class SourcingEngine:
    """Orchestrates multi-platform sourcing, classified scraping, and BOM economic optimization."""

    def __init__(self, bom_path: Optional[str] = None):
        self.analyzer = BOMAnalyzer(bom_path=bom_path)
        self.adapters: Dict[str, BaseAdapter] = {
            "gumtree": GumtreeAdapter(),
            "facebook": FacebookMarketplaceAdapter(),
            "google": GoogleShoppingAdapter(),
            "industrial": IndustrialSupplierAdapter()
        }

    def register_adapter(self, name: str, adapter: BaseAdapter):
        """Allows registering custom or updated adapters."""
        self.adapters[name] = adapter

    def search_item(
        self,
        item: BOMItem,
        platforms: Optional[List[str]] = None,
        location: str = "Sydney NSW",
        radius_km: float = 50.0,
        max_results_per_platform: int = 3,
        mock: bool = True
    ) -> SourcingComparison:
        """Searches across selected platforms for a specific BOM item."""
        active_platforms = platforms if platforms else list(self.adapters.keys())
        query_bundle = self.analyzer.generate_query_bundle(item)

        all_listings: List[Listing] = []

        for p_name in active_platforms:
            if p_name not in self.adapters:
                continue
            adapter = self.adapters[p_name]

            # Choose appropriate query for the platform type
            if p_name in ["gumtree", "facebook"]:
                # Prefer surplus / classifieds queries
                queries = query_bundle.surplus_queries or [f"{item.component_name} surplus"]
            elif p_name == "google":
                # Prefer retail queries
                queries = query_bundle.retail_queries or [f"{item.component_name} {item.material_spec}"]
            else:  # industrial
                # Prefer exact specs or local service
                queries = query_bundle.retail_queries[:1] or [f"{item.component_name} {item.material_spec}"]

            query_to_run = queries[0] if queries else item.component_name

            listings = adapter.search(
                query=query_to_run,
                location=location,
                radius_km=radius_km,
                max_results=max_results_per_platform,
                mock=mock,
                part_item=item
            )
            # Filter local listings exceeding requested radius
            filtered = [
                l for l in listings
                if l.distance_km <= 0.0 or l.distance_km <= radius_km
            ]
            all_listings.extend(filtered)

        return SourcingComparison(bom_item=item, listings=all_listings)

    def search_all_bom(
        self,
        platforms: Optional[List[str]] = None,
        location: str = "Sydney NSW",
        radius_km: float = 50.0,
        category: Optional[str] = None,
        max_results_per_item: int = 3,
        mock: bool = True,
        include_consumables: bool = True
    ) -> List[SourcingComparison]:
        """Runs complete sourcing analysis for all BOM components."""
        items = self.analyzer.get_all_items(include_consumables=include_consumables)
        if category:
            items = [i for i in items if category.lower() in i.category.lower()]

        comparisons: List[SourcingComparison] = []
        for item in items:
            comp = self.search_item(
                item=item,
                platforms=platforms,
                location=location,
                radius_km=radius_km,
                max_results_per_platform=max_results_per_item,
                mock=mock
            )
            comparisons.append(comp)

        return comparisons

    def compute_summary_metrics(self, comparisons: List[SourcingComparison]) -> Dict[str, Any]:
        """Calculates total BOM cost, best sourced cost, and potential savings."""
        total_bom_cost = sum(c.bom_item.total_estimated_cost for c in comparisons)

        total_best_sourced_cost = 0.0
        total_surplus_cost = 0.0
        total_retail_sourced_cost = 0.0
        hazard_count = 0
        surplus_deals_count = 0

        breakdown_by_category: Dict[str, Dict[str, float]] = {}

        for c in comparisons:
            cat = c.bom_item.category
            if cat not in breakdown_by_category:
                breakdown_by_category[cat] = {"bom_cost": 0.0, "best_cost": 0.0, "savings": 0.0}

            item_bom_cost = c.bom_item.total_estimated_cost
            breakdown_by_category[cat]["bom_cost"] += item_bom_cost

            # Best safe listing
            best = c.best_listing
            best_unit_price = best.unit_price_in_usd() if best else c.bom_item.estimated_unit_cost
            item_best_cost = round(best_unit_price * c.bom_item.qty, 2)
            total_best_sourced_cost += item_best_cost
            breakdown_by_category[cat]["best_cost"] += item_best_cost

            # Surplus listing
            best_surplus = c.best_surplus_listing
            if best_surplus:
                total_surplus_cost += round(best_surplus.unit_price_in_usd() * c.bom_item.qty, 2)
                surplus_deals_count += 1
            else:
                total_surplus_cost += item_best_cost

            # Hazards count
            for l in c.listings:
                if l.safety_status == "hazard":
                    hazard_count += 1


        for cat, vals in breakdown_by_category.items():
            vals["bom_cost"] = round(vals["bom_cost"], 2)
            vals["best_cost"] = round(vals["best_cost"], 2)
            vals["savings"] = round(vals["bom_cost"] - vals["best_cost"], 2)

        total_savings = round(total_bom_cost - total_best_sourced_cost, 2)
        savings_pct = round((total_savings / total_bom_cost * 100) if total_bom_cost > 0 else 0, 1)

        return {
            "total_items": len(comparisons),
            "total_bom_cost_usd": round(total_bom_cost, 2),
            "total_best_sourced_cost_usd": round(total_best_sourced_cost, 2),
            "total_potential_savings_usd": total_savings,
            "savings_percentage": savings_pct,
            "surplus_deals_count": surplus_deals_count,
            "hazards_flagged": hazard_count,
            "category_breakdown": breakdown_by_category
        }

    def generate_markdown_report(
        self,
        comparisons: List[SourcingComparison],
        location: str = "Local Area",
        radius_km: float = 50.0
    ) -> str:
        """Generates a detailed, human-readable markdown sourcing report with tables and savings."""
        metrics = self.compute_summary_metrics(comparisons)

        lines = [
            "# High-Temperature Pizza Oven: Material Sourcing & Classifieds Intelligence Report",
            "",
            f"**Search Location:** {location} | **Search Radius:** {radius_km} km | **Components Analyzed:** {metrics['total_items']}",
            "",
            "## 1. Executive Summary & Economics",
            "",
            f"- **Estimated Baseline BOM Cost:** `${metrics['total_bom_cost_usd']:.2f} USD`",
            f"- **Optimized Sourced Cost (Local + Surplus + Direct):** `${metrics['total_best_sourced_cost_usd']:.2f} USD`",
            f"- **Total Projected Savings:** `${metrics['total_potential_savings_usd']:.2f} USD` ({metrics['savings_percentage']}%)",
            f"- **Surplus / Offcut Deals Identified:** {metrics['surplus_deals_count']}",
            f"- **Hazardous Materials Intercepted:** {metrics['hazards_flagged']} flagged",
            "",
            "### Category Financial Breakdown",
            "",
            "| Category | Baseline BOM Cost | Best Sourced Cost | Potential Savings |",
            "|---|---|---|---|"
        ]

        for cat, vals in metrics["category_breakdown"].items():
            lines.append(f"| {cat} | ${vals['bom_cost']:.2f} | ${vals['best_cost']:.2f} | ${vals['savings']:.2f} |")

        lines.extend([
            "",
            "## 2. Component Sourcing Matrix",
            "",
            "| Part # | Component | Qty | Est. Unit | Best Found | Platform | Seller / Notes | Status |",
            "|---|---|---|---|---|---|---|---|"
        ])

        for c in comparisons:
            best = c.best_listing
            if best:
                if best.currency.upper() != "USD":
                    price_str = f"${best.unit_price:.2f} {best.currency} (~${best.unit_price_in_usd():.2f} USD)"
                else:
                    price_str = f"${best.unit_price:.2f}"
                plat_str = best.platform.capitalize()
                seller_str = f"{best.seller} ({best.condition})"
                status_str = f"✅ Save ${c.unit_savings:.2f}/ea" if c.unit_savings > 0 else "✓ Fair Price"
            else:
                price_str = f"${c.bom_item.estimated_unit_cost:.2f}"
                plat_str = "BOM Default"
                seller_str = c.bom_item.vendor_ref
                status_str = "No Listings"

            lines.append(
                f"| `{c.bom_item.part_number}` | {c.bom_item.component_name} | {c.bom_item.qty} | "
                f"${c.bom_item.estimated_unit_cost:.2f} | {price_str} | {plat_str} | {seller_str} | {status_str} |"
            )

        # Highlight Top Surplus Deals
        lines.extend([
            "",
            "## 3. Top Classifieds & Surplus Deals (Facebook Marketplace / Gumtree)",
            ""
        ])

        surplus_listings = []
        for c in comparisons:
            for l in c.listings:
                if l.is_surplus and l.safety_status == "safe":
                    surplus_listings.append((c.bom_item, l))

        surplus_listings.sort(key=lambda pair: (pair[0].estimated_unit_cost - pair[1].unit_price_in_usd()), reverse=True)

        if surplus_listings:
            for item, l in surplus_listings[:6]:
                unit_save = round(item.estimated_unit_cost - l.unit_price_in_usd(), 2)
                price_disp = f"${l.price:.2f} {l.currency}" if l.currency.upper() != "USD" else f"${l.price:.2f}"
                lines.append(
                    f"- **{l.title}** ([Link]({l.url}))\n"
                    f"  - **Platform:** {l.platform.title()} | **Location:** {l.location} ({l.distance_km} km away)\n"
                    f"  - **Seller:** {l.seller} | **Condition:** {l.condition}\n"
                    f"  - **Price:** {price_disp} (Saves ~${unit_save:.2f} USD vs baseline unit cost)\n"
                )

        else:
            lines.append("No active surplus listings discovered.")

        # Safety Audit Warnings
        hazards = []
        for c in comparisons:
            for l in c.listings:
                if l.safety_status == "hazard":
                    hazards.append((c.bom_item, l))

        if hazards:
            lines.extend([
                "",
                "## 4. ⚠️ High-Temperature Safety Interceptions",
                "",
                "The scraper intercepted potentially hazardous materials masquerading as pizza oven parts:",
                ""
            ])
            for item, l in hazards[:5]:
                lines.append(
                    f"- **FLAGGED:** `{l.title}` ({l.platform})\n"
                    f"  - **Target BOM Part:** `{item.part_number}` - {item.component_name}\n"
                    f"  - **Hazard Assessment:** {l.safety_note}\n"
                    f"  - **Action Taken:** Excluded from sourcing recommendations.\n"
                )

        return "\n".join(lines)
