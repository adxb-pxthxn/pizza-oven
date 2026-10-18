"""Comprehensive test suite for the material sourcing skill, scrapers, and automation."""

import json
import os
import sys
import tempfile
import unittest

# Ensure scripts dir is on sys.path
test_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(test_dir, "../scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from models import BOMItem, Listing, SourcingComparison
from bom_analyzer import BOMAnalyzer
from adapters.base import BaseAdapter
from adapters.gumtree_adapter import GumtreeAdapter
from adapters.facebook_marketplace_adapter import FacebookMarketplaceAdapter
from adapters.google_shopping_adapter import GoogleShoppingAdapter
from adapters.industrial_adapter import IndustrialSupplierAdapter
from sourcing_engine import SourcingEngine
from automation import SourcingAutomationWatcher


class TestBOMAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = BOMAnalyzer()

    def test_load_bom(self):
        items = self.analyzer.items
        self.assertGreaterEqual(len(items), 20)
        # Check first part
        sm001 = self.analyzer.get_item_by_part_number("PO-SM-001")
        self.assertIsNotNone(sm001)
        self.assertEqual(sm001.component_name, "Inner Dome Hot Chamber")
        self.assertEqual(sm001.category, "Sheet Metal")
        self.assertIn("304", sm001.material_spec)
        self.assertEqual(sm001.estimated_unit_cost, 28.50)

    def test_load_bom_with_missing_columns_and_aliases(self):
        """Tests that BOM analyzer gracefully handles non-standard headers and missing fields."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Part,Description,Material,Count,Price\n")
            f.write("PO-CUST-1,Custom Flange,304 SS,2,$14.50\n")
            f.write("PO-CUST-2,Unspecified Component,Cordierite,, \n")
            f.write(",,,,\n")  # Trailing empty comma row
            f.write("PO-CUST-3,Free Donated Scrap,304 SS,1,0.0\n")
            f.flush()
            custom_analyzer = BOMAnalyzer(f.name)
            items = custom_analyzer.items
            self.assertEqual(len(items), 3)
            self.assertEqual(items[0].part_number, "PO-CUST-1")
            self.assertEqual(items[0].qty, 2)
            self.assertEqual(items[0].estimated_unit_cost, 14.50)
            self.assertEqual(items[1].qty, 1)  # Defaulted
            self.assertEqual(items[1].estimated_unit_cost, 0.0)  # Defaulted
            self.assertEqual(items[2].estimated_unit_cost, 0.0)

    def test_get_item_by_part_number_edge_cases(self):
        """Verifies get_item_by_part_number handles None, whitespace, and case insensitivity."""
        self.assertIsNone(self.analyzer.get_item_by_part_number(None))
        self.assertIsNone(self.analyzer.get_item_by_part_number(""))
        self.assertIsNone(self.analyzer.get_item_by_part_number("NON-EXISTENT"))
        item = self.analyzer.get_item_by_part_number(" po-sm-001 ")
        self.assertIsNotNone(item)
        self.assertEqual(item.part_number, "PO-SM-001")


class TestSafetyAudit(unittest.TestCase):
    def setUp(self):
        self.adapter = GumtreeAdapter()

    def test_detect_galvanized_zinc_hazard(self):
        status, note = self.adapter.check_safety("Galvanized sheet metal offcut 1.5mm")
        self.assertEqual(status, "hazard")
        self.assertIn("Zinc", note)

        status, note = self.adapter.check_safety("Zinc plated steel bolts M5")
        self.assertEqual(status, "hazard")
        self.assertIn("Zinc", note)

    def test_detect_cadmium_lead_hazards(self):
        status, note = self.adapter.check_safety("Cadmium plated M6 fasteners")
        self.assertEqual(status, "hazard")
        self.assertIn("Cadmium", note)

        status, note = self.adapter.check_safety("Lead solder wire")
        self.assertEqual(status, "hazard")
        self.assertIn("lead", note.lower())

    def test_detect_stone_explosion_hazard(self):
        status, note = self.adapter.check_safety("Polished granite slab for oven base")
        self.assertEqual(status, "hazard")
        self.assertIn("thermal shock", note.lower())

        status, note = self.adapter.check_safety("Natural slate cooking stone")
        self.assertEqual(status, "hazard")

    def test_detect_fiberglass_and_asbestos_hazard(self):
        status, note = self.adapter.check_safety("Yellow fiberglass insulation remnant")
        self.assertEqual(status, "hazard")
        self.assertIn("binder", note.lower())

        status, note = self.adapter.check_safety("Asbestos blanket insulation piece")
        self.assertEqual(status, "hazard")
        self.assertIn("Asbestos", note)

    def test_detect_painted_steel_hazard(self):
        status, note = self.adapter.check_safety("Painted steel sheet panel for firebox")
        self.assertEqual(status, "hazard")
        self.assertIn("Paint", note)

    def test_safe_materials(self):
        status, _ = self.adapter.check_safety("304 Stainless steel sheet 1.5mm food grade")
        self.assertEqual(status, "safe")

        status, _ = self.adapter.check_safety("Cordierite kiln shelf 335mm square")
        self.assertEqual(status, "safe")

        status, _ = self.adapter.check_safety("Cerablanket bio-soluble ceramic fiber 1260C")
        self.assertEqual(status, "safe")


class TestScraperAdapters(unittest.TestCase):
    def setUp(self):
        self.analyzer = BOMAnalyzer()
        self.stone_item = self.analyzer.get_item_by_part_number("PO-ST-001")
        self.sm_item = self.analyzer.get_item_by_part_number("PO-SM-001")

    def test_gumtree_adapter(self):
        adapter = GumtreeAdapter(region="au")
        listings = adapter.search("cordierite pizza stone", location="Melbourne VIC", radius_km=30, mock=True, part_item=self.stone_item)
        self.assertTrue(len(listings) > 0)
        first = listings[0]
        self.assertEqual(first.platform, "gumtree")
        self.assertIn("Melbourne", first.location)
        self.assertGreater(first.price, 0)
        self.assertIn(first.safety_status, ["safe", "hazard", "warning"])

    def test_gumtree_html_parser_live_snippet(self):
        """Verifies GumtreeHTMLParser extracts listings from HTML markup."""
        from adapters.gumtree_adapter import GumtreeHTMLParser
        parser = GumtreeHTMLParser()
        sample_html = """
        <div class="user-ad-row" href="/s-ad/12345">
            <a class="user-ad-row__title" href="/s-ad/12345">304 Stainless Steel Sheet Drop</a>
            <span class="user-ad-price__price">$25.00</span>
            <span class="user-ad-row__location">Alexandria, NSW</span>
        </div>
        """
        parser.feed(sample_html)
        parser.close()
        self.assertEqual(len(parser.listings), 1)
        parsed = parser.listings[0]
        self.assertEqual(parsed["title"], "304 Stainless Steel Sheet Drop")
        self.assertEqual(parsed["price"], "$25.00")
        self.assertEqual(parsed["location"], "Alexandria, NSW")
        self.assertEqual(parsed["href"], "/s-ad/12345")

    def test_facebook_marketplace_adapter(self):
        adapter = FacebookMarketplaceAdapter()
        listings = adapter.search("stainless steel sheet offcut", location="Sydney NSW", radius_km=25, mock=True, part_item=self.sm_item)
        self.assertTrue(len(listings) > 0)
        first = listings[0]
        self.assertEqual(first.platform, "facebook_marketplace")
        self.assertIn("Sydney", first.location)
        self.assertTrue(first.url.startswith("https://www.facebook.com/marketplace"))

    def test_google_shopping_adapter(self):
        adapter = GoogleShoppingAdapter()
        listings = adapter.search("high temp pizza stone", location="National", mock=True, part_item=self.stone_item)
        self.assertTrue(len(listings) > 0)
        first = listings[0]
        self.assertEqual(first.platform, "google_shopping")
        self.assertEqual(first.condition, "new")
        self.assertFalse(first.is_surplus)

    def test_industrial_adapter(self):
        adapter = IndustrialSupplierAdapter()
        listings = adapter.search("SendCutSend 304 stainless", mock=True, part_item=self.sm_item)
        self.assertTrue(len(listings) > 0)
        first = listings[0]
        self.assertEqual(first.platform, "industrial")
        self.assertGreater(first.spec_match_score, 0.8)


class TestSourcingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SourcingEngine()

    def test_search_item_multi_platform(self):
        item = self.engine.analyzer.get_item_by_part_number("PO-ST-001")
        comparison = self.engine.search_item(
            item=item,
            platforms=["gumtree", "facebook", "google", "industrial"],
            location="Sydney NSW",
            mock=True
        )
        self.assertGreaterEqual(len(comparison.listings), 4)
        best = comparison.best_listing
        self.assertIsNotNone(best)
        self.assertNotEqual(best.safety_status, "hazard")
        self.assertGreater(best.unit_price, 0)

    def test_distance_radius_enforcement(self):
        """Verifies that local listings do not exceed user-specified radius_km."""
        item = self.engine.analyzer.get_item_by_part_number("PO-SM-001")
        comp = self.engine.search_item(
            item=item,
            platforms=["gumtree", "facebook"],
            location="Sydney NSW",
            radius_km=3.0,
            mock=True
        )
        for l in comp.listings:
            self.assertLessEqual(l.distance_km, 3.0)

    def test_multi_currency_normalization(self):
        """Verifies that economic comparison converts currencies accurately to USD."""
        item = BOMItem("PO-TEST", "Test Item", "Spec", 1, "Sheet Metal", "Ref", 20.00, "")
        # Listing 1: 15.00 AUD * 0.65 = 9.75 USD
        # Listing 2: 12.00 USD * 1.00 = 12.00 USD
        # Gumtree 15.00 AUD is CHEAPER in USD than Google 12.00 USD
        l1 = Listing("1", "Gumtree AUD Listing", 15.00, "AUD", "gumtree", "Seller", "surplus", "Loc", 5.0, "url", "PO-TEST")
        l2 = Listing("2", "Google USD Listing", 12.00, "USD", "google", "Seller", "new", "Loc", 0.0, "url", "PO-TEST")

        comp = SourcingComparison(bom_item=item, listings=[l1, l2])
        self.assertEqual(comp.best_listing.id, "1")  # Gumtree is cheaper in USD
        self.assertEqual(comp.best_listing.unit_price_in_usd(), 9.75)
        self.assertEqual(comp.unit_savings, 10.25)  # 20.00 - 9.75

    def test_search_all_bom_and_metrics(self):
        comparisons = self.engine.search_all_bom(location="Sydney NSW", mock=True, include_consumables=True)
        self.assertEqual(len(comparisons), 23)  # 20 BOM items + 3 consumables

        metrics = self.engine.compute_summary_metrics(comparisons)
        self.assertGreater(metrics["total_bom_cost_usd"], 250.0)
        self.assertLess(metrics["total_best_sourced_cost_usd"], metrics["total_bom_cost_usd"])
        self.assertGreater(metrics["total_potential_savings_usd"], 0.0)
        self.assertGreater(metrics["surplus_deals_count"], 0)
        self.assertIn("Sheet Metal", metrics["category_breakdown"])

    def test_markdown_report_generation(self):
        comparisons = self.engine.search_all_bom(location="Sydney NSW", mock=True, include_consumables=True)
        report = self.engine.generate_markdown_report(comparisons, location="Sydney NSW", radius_km=50)
        self.assertIn("# High-Temperature Pizza Oven: Material Sourcing", report)
        self.assertIn("Executive Summary & Economics", report)
        self.assertIn("Component Sourcing Matrix", report)
        self.assertIn("PO-SM-001", report)
        self.assertIn("PO-ST-001", report)
        self.assertIn("High-Temperature Safety Interceptions", report)


class TestAutomationPipeline(unittest.TestCase):
    def test_automation_pipeline_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "snapshot.json")
            engine = SourcingEngine()
            watcher = SourcingAutomationWatcher(engine=engine, state_file=state_file, alert_discount_threshold_pct=10.0)

            # First run
            res1 = watcher.run_pipeline(location="Sydney NSW", update_docs=False, live=False)
            self.assertTrue(os.path.exists(state_file))
            self.assertGreater(len(res1["new_surplus_deals"]), 0)
            self.assertGreater(res1["metrics"]["total_potential_savings_usd"], 0)

            # Second run with same state: deals are already seen, so new_surplus_deals should be empty
            res2 = watcher.run_pipeline(location="Sydney NSW", update_docs=False, live=False)
            self.assertEqual(len(res2["new_surplus_deals"]), 0)

    def test_automation_watcher_zero_cost_baseline(self):
        """Verifies watcher pipeline handles zero baseline cost without ZeroDivisionError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f_bom:
            f_bom.write("Part Number,Component Name,Material / Spec,Qty,Category,Vendor / Standard Reference,Estimated Unit Cost (USD),Sourcing Notes\n")
            f_bom.write("PO-ZERO-1,Free Recycled Core,304 SS,1,Sheet Metal,Local,0.00,Scrap\n")
            f_bom.flush()

            with tempfile.TemporaryDirectory() as tmpdir:
                state_file = os.path.join(tmpdir, "zero_snap.json")
                engine = SourcingEngine(bom_path=f_bom.name)
                watcher = SourcingAutomationWatcher(engine=engine, state_file=state_file)
                res = watcher.run_pipeline(location="Sydney NSW", update_docs=False, live=False)
                self.assertIsNotNone(res)
                self.assertEqual(res["metrics"]["total_bom_cost_usd"], 28.80)  # Consumables only since BOM item is 0


if __name__ == "__main__":
    unittest.main()

