# Open-Source Pizza Oven: Physical Development Guidelines

## Project Mission
This repository is an open-source physical engineering and mechanical development workspace for a pizza oven.

> [!IMPORTANT]
> **No Premature Design Assumptions:**
> Do NOT assume any specific dimensions, fuel sources (wood, gas, pellet, charcoal, electric), materials (sheet metal, refractory brick, cast refractory, masonry), forms, capacity, or manufacturing methods until explicitly provided or requested by the user. Keep all engineering foundations neutral and waiting for user direction.

## Standards & Methodologies

1. **Open Source Hardware Association (OSHWA) Compliance**:
   - Provide editable source CAD files alongside open interchange formats (STEP AP214/242 for 3D, DXF for 2D CNC/laser cutting).
   - Maintain the Bill of Materials (BOM) in `bom/bom.csv` with standard part numbering, supplier references, and estimated costs once parts are decided.
   - Dual-licensing: CERN-OHL-P v2 for hardware designs, CC-BY-4.0 for documentation.

2. **Mechanical Engineering & DFM Rigor**:
   - Apply standard DFM (Design for Manufacturing) guidelines for the chosen fabrication processes.
   - Respect thermal expansion differentials, food contact safety standards (FDA/EU 1935/2004), and high-temperature material properties.
   - Ensure tolerance stack-up analysis and appropriate fastener selection.

3. **Multi-Agent & Cross-Agent Coordination**:
   - Support concurrent and handover-driven pair programming between Antigravity, Cursor, and Claude Code.
   - Keep `docs/HANDOVER.md` and `.agents/state/TASK_BOARD.md` updated between agent sessions.
   - Practice atomic commits with agent signatures (e.g. `[agent:antigrav]` or `[agent:cursor]`).

## Available Skills
- `anatomy`: Isometric technical figures, cutaways, and interactive visual explainers.
- `mechanical-engineering`: General sheet metal DFM, bend allowance calculator, thermal expansion calculator, GD&T, food safety standards.
- `code-cad`: Parametric code-CAD modeling guidelines, layer conventions, interchange export pipelines.
- `oshwa-hardware`: Open-source hardware audit, BOM validation, OSHWA checklist.
- `oven-thermodynamics`: High-temp thermal modeling, heat transfer formulas, multi-layer insulation calculations.
- `material-sourcing`: Local vendor search, classifieds scraping (Gumtree, Facebook Marketplace, Google), and BOM price comparison.
- `cross-agent-coordination`: Handover protocol, situational awareness briefings, and file locking.
- `cursor-sync`: Rules synchronization between Antigravity, Cursor (`.cursor/rules/*.mdc`), and Claude Code.
- `multi-agent-review`: Maker/Critic peer review protocol and automated validation harness.
