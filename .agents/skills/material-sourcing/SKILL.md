---
name: material-sourcing
description: Scrapes, searches, and sources physical materials, surplus drops, laser-cut offcuts, classifieds (Facebook Marketplace, Gumtree), Google Shopping, and industrial suppliers for the high-temperature pizza oven Bill of Materials. Features automated query matrix generation, local classified scrapers, physical safety hazard filters (detecting toxic zinc/galvanized steel and exploding stones), price delta economics, and automated price-drop watchers.
license: CERN-OHL-P v2 / CC-BY-4.0
compatibility: Python 3.10+, zero external dependencies (pure standard library with urllib/html.parser and simulated/live adapters).
metadata:
  opencode/slash: "true"
---

# Material Sourcing, Classifieds Scraping & Surplus Recovery Skill

This skill provides comprehensive methodologies, search query generators, and automated scraping/intelligence pipelines to source raw materials, components, and hardware for high-temperature physical engineering projects (specifically the certified Neapolitan pizza oven).

It bridges the gap between digital CAD/BOM specifications and real-world physical procurement by scouring local classifieds (Gumtree, Facebook Marketplace), retail search engines (Google Shopping), and industrial metal/hardware suppliers (SendCutSend, McMaster-Carr, Bolt Depot, local laser profiling job shops, and pottery suppliers).

---

## 1. Sourcing Architecture & Modular Scrapers

The skill provides an extensible, modular scraping engine with simulation fallbacks for platforms with authentication walls or CAPTCHAs.

```
                    ┌───────────────────────────────┐
                    │      bom/bom.csv (20 Parts)   │
                    │   + Supplementary Consumables │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      BOMAnalyzer Engine       │
                    │ - Specs, Quantities, Costs    │
                    │ - Query Bundles Generation    │
                    │ - Prohibited Material Hazards │
                    └───────────────┬───────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│ Gumtree       │            │ Facebook      │            │ Google &      │
│ Classifieds   │            │ Marketplace   │            │ Industrial    │
│ Adapter       │            │ Adapter       │            │ Suppliers     │
└───────┬───────┘            └───────┬───────┘            └───────┬───────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                    ┌───────────────────────────────┐
                    │       SourcingEngine          │
                    │ - Multi-Platform Aggregation  │
                    │ - Distance & Location Filter  │
                    │ - Safety Hazard Screening     │
                    │ - BOM Cost Delta & Savings    │
                    └───────────────┬───────────────┘
                                    │
       ┌────────────────────────────┴────────────────────────────┐
       ▼                                                         ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│ Markdown Intelligence Report  │               │ Automated Watcher & Alerting  │
│ (`docs/sourcing-report.md`)   │               │ (`automation.py` + JSON cache)│
└───────────────────────────────┘               └───────────────────────────────┘
```

### Supported Platforms & Adapters

| Platform | Primary Target Materials | Adapter Implementation | Fallback Mode |
|---|---|---|---|
| **Gumtree** | Metal offcuts, pottery kiln furniture, BBQ parts, workshop liquidations | `GumtreeAdapter` | Localized suburb & classified simulator |
| **Facebook Marketplace** | Local fabricator scrap drops, garage sales, surplus hardware lots | `FacebookMarketplaceAdapter` | Realistic localized maker/surplus simulation |
| **Google Shopping** | Off-the-shelf retail, commercial replacement components, direct retail | `GoogleShoppingAdapter` | Merchant aggregator simulation |
| **Industrial Suppliers** | SendCutSend, McMaster-Carr, Bolt Depot, pottery supply, local laser cutting | `IndustrialSupplierAdapter` | Direct B2B volume pricing with bulk breaks |

---

## 2. Physical Material Guidelines & Critical Safety Hazards

High-temperature cooking appliances (450°C–500°C) impose non-negotiable physical constraints. Sourcing cheaper materials must **never** compromise food safety or thermal integrity.

### ⚠️ Prohibited Substitutions & Danger Rules

1. **Sheet Metal & Structural Panels**:
   - **Allowed**: AISI 304 food-grade stainless steel for inner hot chamber, flame baffles, and floor trays. AISI 430 brushed stainless steel or powder-coated steel for exterior shroud.
   - **FATAL HAZARD**: **Never use galvanized steel, zinc-coated steel, or cadmium plating**. At temperatures above 200°C, zinc vaporizes into toxic zinc oxide fumes, causing severe metal fume fever and contaminating food. The scraper automatically flags and excludes any listing mentioning `galvanized`, `galv`, `zinc`, or `cadmium`.

2. **Baking Stone & Refractory Floor**:
   - **Allowed**: Cordierite ceramic (thermal shock rated to >800°C) or artisanal Biscotto di Sorrento clay tiles.
   - **FATAL HAZARD**: **Never use granite, marble, slate, untreated architectural pavers, or tempered glass**. Natural stones contain microscopic trapped moisture and crystalline quartz. Under rapid 450°C heating, internal steam pressures fracture the stone violently, causing explosive shattering.

3. **Thermal Insulation**:
   - **Allowed**: Bio-soluble high-temperature ceramic fiber blanket (Superwool 607, Cerablanket, Kaowool 1260°C rated, 128 kg/m³ density).
   - **FATAL HAZARD**: **Never use yellow/pink residential fiberglass batts or standard rockwool with phenolic binders**. The organic binders smoke and off-gas toxic aldehydes and formaldehyde above 180°C.

4. **Fasteners & Rivets**:
   - **Allowed**: ISO Metric A2-70 (AISI 304) or A4-80 (AISI 316) stainless steel screws and serrated flange locknuts.
   - **HAZARD**: Zinc-plated carbon steel screws rust under condensation and scale/weld themselves permanently into sheet metal threads under heat cycling.

5. **Consumables & Sealants**:
   - **Allowed**: Sodium silicate refractory mortar / fireplace cement (rated 1250°C) and FDA food-contact approved red silicone RTV (rated 315°C continuous). Copper or nickel anti-seize paste for threads.
   - **HAZARD**: Bathroom or construction silicone emits acetic acid or organotin toxins at pizza baking temperatures.

---

## 3. High-Leverage Surplus & Bargain Sourcing Strategies

Builders can save over 50% of total oven build costs using the following classified and local workshop tactics:

### A. Laser Cutting Offcuts & Drops (Sheet Metal)
- **Retail Cost**: ~$110 USD for custom laser-cut inner dome, shroud, floor tray, and legs.
- **Surplus Strategy**: Local sheet metal and CNC fiber laser cutting workshops generate tons of 1.5mm and 2.0mm 304 stainless steel offcuts ("drops"). Search Gumtree and Facebook Marketplace for `stainless sheet offcut 304`, `laser cut scrap`, or visit a local fabricator's drop bin.
- **Projected Savings**: 50%–60% ($60+ saved).

### B. Cordierite Kiln Shelves vs "Pizza Stones"
- **Retail Cost**: Brand-name outdoor pizza stones often sell for $35–$50 USD.
- **Classified Strategy**: Pottery and ceramic craft studios use identical cordierite ceramic plates as kiln shelves (standard 13" x 13" or 335mm square, 15mm thick). Search for `cordierite kiln shelf`, `pottery furniture`, or check with local ceramic supply shops.
- **Projected Savings**: 40%–50% ($12+ saved).

### C. BBQ Teardown & Smoker Burner Assemblies
- **Retail Cost**: $34 USD for new stainless U-tube burner and $16 USD for propane regulator.
- **Classified Strategy**: Barbecue refurbishers and private sellers often liquidate unused replacement stainless U-burners, 0-10 PSI adjustable regulators, and piezo igniters.
- **Projected Savings**: 35%–45% ($25+ saved).

### D. Bulk Fastener Orders
- **Retail Cost**: Buying small blisters of 2-4 screws at big-box hardware stores costs ~$0.80/screw.
- **Industrial Strategy**: Buying a box of 50 A2-70 stainless M5 button head screws and DIN 6923 flange locknuts from Bolt Depot, Accu, or McMaster-Carr drops unit cost to $0.06–$0.12/screw.
- **Projected Savings**: 55% ($8+ saved).

---

## 4. CLI Tool Reference

The CLI tool is located at `.agents/skills/material-sourcing/scripts/cli.py`.

### 1. Scan BOM & Display Query Matrix
Scans `bom/bom.csv` and outputs tailored queries across retail, classifieds, and scrap channels:
```bash
python3 .agents/skills/material-sourcing/scripts/cli.py scan
```

### 2. Search Specific Part or Category Across Platforms
Search Gumtree, Facebook Marketplace, Google Shopping, and industrial suppliers:
```bash
# Search a specific component in Melbourne
python3 .agents/skills/material-sourcing/scripts/cli.py search --part PO-ST-001 --location "Melbourne VIC" --radius 30

# Search all sheet metal parts in Sydney
python3 .agents/skills/material-sourcing/scripts/cli.py search --category "Sheet Metal" --location "Sydney NSW"

# Run live web scraping requests (instead of simulated mode)
python3 .agents/skills/material-sourcing/scripts/cli.py search --part PO-BN-001 --live
```

### 3. Compare Market Prices with BOM Baseline
Calculates full financial comparison, category breakdowns, and net build savings:
```bash
python3 .agents/skills/material-sourcing/scripts/cli.py compare --location "Sydney NSW"
```

### 4. Generate Sourcing Intelligence Report
Generates full Markdown report with active deal links, seller details, and safety audit:
```bash
python3 .agents/skills/material-sourcing/scripts/cli.py report -o docs/sourcing-report.md --location "Sydney NSW"
```

### 5. Export Structured Data to JSON
Exports full comparison data and raw listing objects for downstream automations:
```bash
python3 .agents/skills/material-sourcing/scripts/cli.py export -o .agents/skills/material-sourcing/data/inventory.json
```

---

## 5. Automated Sourcing Pipeline & Watcher

The watcher script `.agents/skills/material-sourcing/scripts/automation.py` enables autonomous price monitoring and deal detection:

### Running the Automation
```bash
python3 .agents/skills/material-sourcing/scripts/automation.py --location "Sydney NSW" --radius 50
```

### What the Automation Does:
1. Performs full multi-channel scan for all BOM components.
2. Compares discovered listings with previous snapshot cached at `.agents/skills/material-sourcing/data/sourcing_snapshot.json`.
3. Detects newly posted surplus offcut deals and price drops exceeding the alert threshold (default 15%).
4. Updates the repository documentation at `docs/sourcing-report.md`.
5. Emits summary metrics and alerts.

### Scheduling via Cron / CI
To run periodic monitoring (e.g. daily at 8:00 AM):
```bash
0 8 * * * cd /Users/adib/.gemini/antigravity/scratch/pizza-oven && python3 .agents/skills/material-sourcing/scripts/automation.py --location "Sydney NSW"
```

---

## 6. Python API Integration

Other agents or Python scripts can import and drive the sourcing engine directly:

```python
from scripts.sourcing_engine import SourcingEngine
from scripts.automation import SourcingAutomationWatcher

# Initialize engine
engine = SourcingEngine()

# Search a single BOM component
stone_item = engine.analyzer.get_item_by_part_number("PO-ST-001")
comparison = engine.search_item(stone_item, location="Sydney NSW", radius_km=40)

print(f"BOM Cost: ${stone_item.estimated_unit_cost}")
print(f"Best Sourced: ${comparison.best_listing.unit_price} via {comparison.best_listing.platform}")
print(f"Unit Savings: ${comparison.unit_savings}")

# Run automated watcher
watcher = SourcingAutomationWatcher(engine)
result = watcher.run_pipeline(location="Sydney NSW", update_docs=True)
print(f"Net Project Savings: ${result['metrics']['total_potential_savings_usd']}")
```

---

## 7. Testing & Quality Verification

Run the comprehensive unit test suite:
```bash
python3 .agents/skills/material-sourcing/tests/test_material_sourcing.py
```
This runs 21 comprehensive unit tests covering BOM parsing with header aliases, query bundle generation, multi-currency normalization (USD, AUD, EUR, GBP), physical safety filters (galvanized/zinc, exploding stones, cadmium/lead, asbestos/polymers, painted steel), all four platform adapters, cost delta math, markdown generation, radius distance filtering, zero baseline cost resilience, and the automation snapshot state engine.
