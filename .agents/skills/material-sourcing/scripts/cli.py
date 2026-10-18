"""Command-line interface for the material-sourcing skill."""

import argparse
import json
import os
import sys
from typing import List

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from .bom_analyzer import BOMAnalyzer
    from .sourcing_engine import SourcingEngine
except ImportError:
    from bom_analyzer import BOMAnalyzer
    from sourcing_engine import SourcingEngine


def cmd_scan(args, engine: SourcingEngine):
    """Scans the BOM and prints generated query bundles and safety guidelines."""
    analyzer = engine.analyzer
    items = analyzer.get_all_items(include_consumables=not args.no_consumables)
    print(f"\n=======================================================")
    print(f"   BOM Material Analysis & Query Matrix Generator")
    print(f"   BOM Source: {analyzer.bom_path}")
    print(f"   Total Components & Consumables: {len(items)}")
    print(f"=======================================================\n")

    for item in items:
        bundle = analyzer.generate_query_bundle(item)
        print(f"[{item.part_number}] {item.component_name} ({item.category})")
        print(f"  Spec: {item.material_spec} | Qty: {item.qty} | Est. Unit Cost: ${item.estimated_unit_cost:.2f}")
        print(f"  Primary Retail Query: {bundle.retail_queries[0] if bundle.retail_queries else 'N/A'}")
        print(f"  Surplus/Classifieds Query: {bundle.surplus_queries[0] if bundle.surplus_queries else 'N/A'}")
        print(f"  Local Service Query: {bundle.local_service_queries[0] if bundle.local_service_queries else 'N/A'}")
        if bundle.danger_keywords:
            print(f"  ⚠️ Prohibited Substitutes: {', '.join(bundle.danger_keywords[:4])}")
        print("-" * 55)


def cmd_search(args, engine: SourcingEngine):
    """Searches for materials across platforms."""
    platforms = [p.strip() for p in args.platforms.split(",")] if args.platforms else None
    mock_mode = not args.live

    if args.part:
        item = engine.analyzer.get_item_by_part_number(args.part)
        if not item:
            print(f"Error: Part number '{args.part}' not found in BOM.")
            sys.exit(1)
        items_to_search = [item]
    else:
        items_to_search = engine.analyzer.get_all_items(include_consumables=not args.no_consumables)
        if args.category:
            items_to_search = [i for i in items_to_search if args.category.lower() in i.category.lower()]

    print(f"\n[Sourcing Search] Location: {args.location} | Radius: {args.radius}km | Mode: {'Mock/Simulated' if mock_mode else 'Live HTTP'}")
    print(f"Searching {len(items_to_search)} item(s) on platforms: {args.platforms or 'all'}...\n")

    for item in items_to_search:
        comp = engine.search_item(
            item=item,
            platforms=platforms,
            location=args.location,
            radius_km=args.radius,
            max_results_per_platform=args.max_results,
            mock=mock_mode
        )
        print(f"=== {item.part_number}: {item.component_name} (Target: ${item.estimated_unit_cost:.2f}) ===")
        for l in comp.listings:
            status_flag = "⚠️ HAZARD" if l.safety_status == "hazard" else ("⭐ SURPLUS" if l.is_surplus else "✓")
            price_label = f"${l.unit_price:.2f} {l.currency}" if l.currency.upper() != "USD" else f"${l.unit_price:.2f}"
            if l.currency.upper() != "USD":
                price_label += f" (~${l.unit_price_in_usd():.2f} USD)"
            print(f"  [{status_flag}] {price_label} ({l.platform.title()}) - {l.title}")
            print(f"      Seller: {l.seller} | Loc: {l.location} | Cond: {l.condition}")
            if l.safety_note:
                print(f"      SAFETY NOTICE: {l.safety_note}")
        best = comp.best_listing
        if best:
            best_label = f"${best.unit_price:.2f} {best.currency}" if best.currency.upper() != "USD" else f"${best.unit_price:.2f}"
            if best.currency.upper() != "USD":
                best_label += f" (~${best.unit_price_in_usd():.2f} USD)"
            print(f"  >> Best Deal: {best_label} via {best.platform.title()} (Savings: ${comp.unit_savings:.2f} USD/unit)")
        print()


def cmd_compare(args, engine: SourcingEngine):
    """Compares entire BOM against discovered prices and displays financial metrics."""
    mock_mode = not args.live
    comparisons = engine.search_all_bom(
        location=args.location,
        radius_km=args.radius,
        category=args.category,
        mock=mock_mode,
        include_consumables=not args.no_consumables
    )
    metrics = engine.compute_summary_metrics(comparisons)

    print(f"\n=======================================================")
    print(f"   BOM Material Sourcing & Cost Delta Analysis")
    print(f"   Location: {args.location} (radius {args.radius} km)")
    print(f"=======================================================")
    print(f"  Original Baseline BOM Cost : ${metrics['total_bom_cost_usd']:.2f} USD")
    print(f"  Optimized Sourced Cost      : ${metrics['total_best_sourced_cost_usd']:.2f} USD")
    print(f"  Projected Net Savings       : ${metrics['total_potential_savings_usd']:.2f} USD ({metrics['savings_percentage']}%)")
    print(f"  Surplus Deals Detected      : {metrics['surplus_deals_count']}")
    print(f"  Hazardous Items Screened    : {metrics['hazards_flagged']}")
    print(f"-------------------------------------------------------")
    print(f" Category Breakdown:")
    for cat, vals in metrics["category_breakdown"].items():
        print(f"   {cat:<18} : BOM ${vals['bom_cost']:>6.2f} | Sourced ${vals['best_cost']:>6.2f} | Save ${vals['savings']:>6.2f}")
    print(f"=======================================================\n")


def cmd_report(args, engine: SourcingEngine):
    """Generates a complete markdown report and optionally writes to disk."""
    mock_mode = not args.live
    comparisons = engine.search_all_bom(
        location=args.location,
        radius_km=args.radius,
        category=args.category,
        mock=mock_mode,
        include_consumables=not args.no_consumables
    )
    report_md = engine.generate_markdown_report(comparisons, location=args.location, radius_km=args.radius)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"Report successfully saved to: {args.output}")
    else:
        print(report_md)


def cmd_export(args, engine: SourcingEngine):
    """Exports structured sourcing comparison data to JSON."""
    mock_mode = not args.live
    comparisons = engine.search_all_bom(
        location=args.location,
        radius_km=args.radius,
        category=args.category,
        mock=mock_mode,
        include_consumables=not args.no_consumables
    )

    data = {
        "location": args.location,
        "radius_km": args.radius,
        "summary": engine.compute_summary_metrics(comparisons),
        "items": []
    }

    for c in comparisons:
        data["items"].append({
            "part_number": c.bom_item.part_number,
            "component_name": c.bom_item.component_name,
            "material_spec": c.bom_item.material_spec,
            "qty": c.bom_item.qty,
            "category": c.bom_item.category,
            "estimated_unit_cost": c.bom_item.estimated_unit_cost,
            "best_unit_price": c.best_listing.unit_price if c.best_listing else c.bom_item.estimated_unit_cost,
            "unit_savings": c.unit_savings,
            "total_savings": c.total_savings,
            "listings": [l.to_dict() for l in c.listings]
        })

    out_json = json.dumps(data, indent=2)
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
        print(f"Data exported successfully to: {args.output}")
    else:
        print(out_json)


def main():
    parser = argparse.ArgumentParser(
        description="Material Sourcing, Classifieds Scraping & BOM Pricing CLI for High-Temp Pizza Oven"
    )
    parser.add_argument("--bom", help="Path to custom bom.csv", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scan subcommand
    p_scan = subparsers.add_parser("scan", help="Scan BOM and print query matrix & safety rules")
    p_scan.add_argument("--no-consumables", action="store_true", help="Exclude supplementary consumables")

    # search subcommand
    p_search = subparsers.add_parser("search", help="Search platforms for materials")
    p_search.add_argument("--part", help="Specific part number to search (e.g. PO-SM-001)")
    p_search.add_argument("--category", help="Filter by category (e.g. 'Sheet Metal', 'Insulation')")
    p_search.add_argument("--location", default="Sydney NSW", help="Search location / city")
    p_search.add_argument("--radius", type=float, default=50.0, help="Search radius in km")
    p_search.add_argument("--platforms", help="Comma-separated platforms: gumtree,facebook,google,industrial")
    p_search.add_argument("--max-results", type=int, default=3, help="Max results per platform")
    p_search.add_argument("--live", action="store_true", help="Enable live network requests instead of mock/simulation")
    p_search.add_argument("--no-consumables", action="store_true", help="Exclude supplementary consumables")

    # compare subcommand
    p_compare = subparsers.add_parser("compare", help="Compare full BOM against market listings and calculate savings")
    p_compare.add_argument("--location", default="Sydney NSW", help="Search location / city")
    p_compare.add_argument("--radius", type=float, default=50.0, help="Search radius in km")
    p_compare.add_argument("--category", help="Filter by category")
    p_compare.add_argument("--live", action="store_true", help="Enable live network requests")
    p_compare.add_argument("--no-consumables", action="store_true", help="Exclude supplementary consumables")

    # report subcommand
    p_report = subparsers.add_parser("report", help="Generate full markdown sourcing intelligence report")
    p_report.add_argument("--output", "-o", help="File path to save markdown report (e.g. docs/sourcing-report.md)")
    p_report.add_argument("--location", default="Sydney NSW", help="Search location / city")
    p_report.add_argument("--radius", type=float, default=50.0, help="Search radius in km")
    p_report.add_argument("--category", help="Filter by category")
    p_report.add_argument("--live", action="store_true", help="Enable live network requests")
    p_report.add_argument("--no-consumables", action="store_true", help="Exclude supplementary consumables")

    # export subcommand
    p_export = subparsers.add_parser("export", help="Export structured sourcing data to JSON")
    p_export.add_argument("--output", "-o", help="File path to save JSON export")
    p_export.add_argument("--location", default="Sydney NSW", help="Search location / city")
    p_export.add_argument("--radius", type=float, default=50.0, help="Search radius in km")
    p_export.add_argument("--category", help="Filter by category")
    p_export.add_argument("--live", action="store_true", help="Enable live network requests")
    p_export.add_argument("--no-consumables", action="store_true", help="Exclude supplementary consumables")

    args = parser.parse_args()
    try:
        engine = SourcingEngine(bom_path=args.bom)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if args.command == "scan":
        cmd_scan(args, engine)
    elif args.command == "search":
        cmd_search(args, engine)
    elif args.command == "compare":
        cmd_compare(args, engine)
    elif args.command == "report":
        cmd_report(args, engine)
    elif args.command == "export":
        cmd_export(args, engine)


if __name__ == "__main__":
    main()
