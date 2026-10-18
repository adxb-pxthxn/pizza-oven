"""Automated material sourcing watcher and price alert pipeline."""

import argparse
import datetime
import json
import os
import sys
from typing import Dict, List, Any, Optional

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from .sourcing_engine import SourcingEngine
    from .models import SourcingComparison, Listing
except ImportError:
    from sourcing_engine import SourcingEngine
    from models import SourcingComparison, Listing


class SourcingAutomationWatcher:
    """Monitors materials, surplus offcuts, and price drops; tracks historical snapshots."""

    def __init__(
        self,
        engine: SourcingEngine,
        state_file: Optional[str] = None,
        alert_discount_threshold_pct: float = 15.0
    ):
        self.engine = engine
        if state_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            state_file = os.path.abspath(os.path.join(base_dir, "../data/sourcing_snapshot.json"))
        self.state_file = state_file
        self.alert_threshold = alert_discount_threshold_pct

    def load_previous_state(self) -> Dict[str, Any]:
        """Loads previous snapshot from disk if it exists."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_state(self, current_data: Dict[str, Any]):
        """Saves current run snapshot to disk."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2)

    def run_pipeline(
        self,
        location: str = "Sydney NSW",
        radius_km: float = 50.0,
        update_docs: bool = True,
        live: bool = False
    ) -> Dict[str, Any]:
        """Runs the automated sourcing cycle, checks for alerts, and updates docs."""
        previous_state = self.load_previous_state()
        prev_listings_map = {}
        for item in previous_state.get("items", []):
            for l in item.get("listings", []):
                prev_listings_map[l["id"]] = l

        # Perform sourcing search
        comparisons = self.engine.search_all_bom(
            location=location,
            radius_km=radius_km,
            mock=not live,
            include_consumables=True
        )

        metrics = self.engine.compute_summary_metrics(comparisons)

        # Detect new deals and price drops
        new_surplus_deals: List[Dict[str, Any]] = []
        price_drops: List[Dict[str, Any]] = []

        current_items_payload = []
        for c in comparisons:
            item_listings = [l.to_dict() for l in c.listings]
            current_items_payload.append({
                "part_number": c.bom_item.part_number,
                "component_name": c.bom_item.component_name,
                "material_spec": c.bom_item.material_spec,
                "qty": c.bom_item.qty,
                "category": c.bom_item.category,
                "estimated_unit_cost": c.bom_item.estimated_unit_cost,
                "best_unit_price": c.best_listing.unit_price if c.best_listing else c.bom_item.estimated_unit_cost,
                "listings": item_listings
            })

            # Check each listing
            for l in c.listings:
                if l.safety_status == "hazard":
                    continue

                usd_price = l.unit_price_in_usd()
                baseline = c.bom_item.estimated_unit_cost
                if baseline > 0.0:
                    savings_pct = ((baseline - usd_price) / baseline) * 100.0
                else:
                    savings_pct = 0.0

                # Is it a new surplus offcut?
                if l.is_surplus and l.id not in prev_listings_map:
                    new_surplus_deals.append({
                        "part": c.bom_item.part_number,
                        "name": c.bom_item.component_name,
                        "title": l.title,
                        "platform": l.platform,
                        "price": l.price,
                        "currency": l.currency,
                        "savings_pct": round(savings_pct, 1),
                        "url": l.url
                    })

                # Check for significant price drop vs BOM baseline
                if savings_pct >= self.alert_threshold and l.id not in prev_listings_map:
                    price_drops.append({
                        "part": c.bom_item.part_number,
                        "name": c.bom_item.component_name,
                        "title": l.title,
                        "price": l.unit_price,
                        "currency": l.currency,
                        "price_usd": usd_price,
                        "baseline": baseline,
                        "discount_pct": round(savings_pct, 1)
                    })

        # Save snapshot
        snapshot_data = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "location": location,
            "radius_km": radius_km,
            "summary": metrics,
            "items": current_items_payload
        }
        self.save_state(snapshot_data)

        # Update docs/sourcing-report.md
        if update_docs:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
            docs_path = os.path.join(repo_root, "docs/sourcing-report.md")
            report_md = self.engine.generate_markdown_report(comparisons, location=location, radius_km=radius_km)
            os.makedirs(os.path.dirname(docs_path), exist_ok=True)
            with open(docs_path, "w", encoding="utf-8") as f:
                f.write(report_md)

        return {
            "metrics": metrics,
            "new_surplus_deals": new_surplus_deals,
            "price_drops": price_drops,
            "snapshot_path": self.state_file
        }


def main():
    parser = argparse.ArgumentParser(description="Automated Material Sourcing Pipeline Runner")
    parser.add_argument("--location", default="Sydney NSW", help="Location for local classifieds scraping")
    parser.add_argument("--radius", type=float, default=50.0, help="Search radius in km")
    parser.add_argument("--threshold", type=float, default=15.0, help="Alert threshold discount percentage (default: 15.0)")
    parser.add_argument("--live", action="store_true", help="Run live HTTP network queries")
    parser.add_argument("--no-docs", action="store_true", help="Skip updating docs/sourcing-report.md")
    parser.add_argument("--state-file", help="Custom path for state cache JSON")
    args = parser.parse_args()

    engine = SourcingEngine()
    watcher = SourcingAutomationWatcher(
        engine=engine,
        state_file=args.state_file,
        alert_discount_threshold_pct=args.threshold
    )

    print(f"Running automated sourcing pipeline for: {args.location}...")
    res = watcher.run_pipeline(
        location=args.location,
        radius_km=args.radius,
        update_docs=not args.no_docs,
        live=args.live
    )

    metrics = res["metrics"]
    print(f"\n=======================================================")
    print(f"   Automated Pipeline Run Complete")
    print(f"=======================================================")
    print(f"  BOM Total Baseline       : ${metrics['total_bom_cost_usd']:.2f}")
    print(f"  Best Sourced Total       : ${metrics['total_best_sourced_cost_usd']:.2f}")
    print(f"  Net Savings Identified   : ${metrics['total_potential_savings_usd']:.2f} ({metrics['savings_percentage']}%)")
    print(f"  New Surplus Opportunities: {len(res['new_surplus_deals'])}")
    print(f"  Significant Price Drops  : {len(res['price_drops'])}")
    print(f"  State Cached At          : {res['snapshot_path']}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    main()
