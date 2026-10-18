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

## Parametric CAD

Editable source is build123d Python. Generated STEP/STL are not committed.

- Dimensions: `cad/parameters.py` (millimetres). The checked-in values are a generic placeholder shell, not a product specification.
- Install (only when building or testing CAD): `python3 -m pip install -r cad/requirements.txt` inside a venv. Pins are build123d 0.13.0 and cadquery-ocp-novtk 8.0.1.1.0. Python 3.11–3.14. macOS arm64 wheel notes are in `cad/README.md`.
- Build: `python3 -m cad.build` writes `cad/output/placeholder_oven_assembly.step` (AP214, millimetres) and `.stl`. `cad/output/` is gitignored.
- Test: `python3 -m unittest cad.tests.test_placeholder_assembly`
- Preview and opening STEP in FreeCAD or Fusion 360: `cad/README.md`
- Agent conventions: `.agents/skills/cad/SKILL.md` (the `.cursor/skills` symlink exposes the same file)

## Cursor Cloud specific instructions

- The default image has Python 3.12 (standard library), Node.js 22, and Google Chrome. Routine non-CAD work stays offline. Do not start a web process.
- CAD dependencies are optional and are not preinstalled. Install `cad/requirements.txt` when a task builds or tests models. The Linux x86_64 wheel for the pinned `cadquery-ocp-novtk` installs with pip on this image.
- Product commands are listed in `README.md`. The stdlib test is `python3 .agents/skills/material-sourcing/tests/test_material_sourcing.py` (offline). The CAD test needs the install above.
- Anatomy figures are plain Node ESM. `node .agents/skills/anatomy/examples/dial-indicator/build.mjs` rewrites the HTML next to that script; a correct rebuild leaves git clean. Anatomy's own `scripts/*.test.mjs` need a temporary `NODE_PATH` with `react`, `react-dom`, `typescript`, and `esbuild`, as in `.agents/skills/anatomy/.github/workflows/ci.yml`.

## Available Skills
- `anatomy`: Isometric technical figures, cutaways, and interactive visual explainers.
- `mechanical-engineering`: General sheet metal DFM, bend allowance calculator, thermal expansion calculator, GD&T, food safety standards.
- `code-cad`: Parametric code-CAD modeling guidelines, layer conventions, interchange export pipelines.
- `cad`: build123d conventions for the in-repo model (`cad/parameters.py`, `python3 -m cad.build`).
- `oshwa-hardware`: Open-source hardware audit, BOM validation, OSHWA checklist.
- `oven-thermodynamics`: High-temp thermal modeling, heat transfer formulas, multi-layer insulation calculations.
- `material-sourcing`: Local vendor search, classifieds scraping (Gumtree, Facebook Marketplace, Google), and BOM price comparison.
- `cross-agent-coordination`: Handover protocol, situational awareness briefings, and file locking.
- `cursor-sync`: Rules synchronization between Antigravity, Cursor (`.cursor/rules/*.mdc`), and Claude Code.
- `multi-agent-review`: Maker/Critic peer review protocol and automated validation harness.
