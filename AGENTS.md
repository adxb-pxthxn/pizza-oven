# Pizza Oven: Open-Source Physical Development Guidelines

## Project Mission
This repository is an open-source, certified-grade physical engineering project to develop a high-performance, portable Neapolitan pizza oven (capable of sustained 450°C–500°C floor & dome temperatures with sub-90s bake cycles) under open hardware standards.

## Engineering Standards & Methodologies

1. **Open Source Hardware Association (OSHWA) Compliance**:
   - All physical parts must have editable CAD source files (code-CAD or parametric native formats) as well as open interchange formats (STEP AP214/242 for 3D solids, DXF for 2D CNC laser cutting/waterjet).
   - Complete Bill of Materials (BOM) in `bom/bom.csv` with standard part numbering, supplier references, and estimated costs.
   - Dual-licensing: CERN-OHL-P v2 for hardware designs, CC-BY-4.0 for documentation.

2. **Mechanical Design & DFM (Design For Manufacturing)**:
   - Primary construction: Sheet metal laser cutting and press brake bending (AISI 304 food-grade stainless steel for inner hot chamber, 430/304 or powder-coated steel for outer shroud).
   - Standard bend deductions, K-factors (~0.42 for stainless), minimum flange lengths >= 4x sheet thickness.
   - Self-aligning tab-and-slot joinery with thermal expansion relief slots to eliminate welding requirements for consumer self-assembly.
   - Fasteners: ISO metric A2/A4 stainless steel (M4, M5, M6), avoiding carbon steel in thermal zones.

3. **Thermodynamics & Heat Transfer**:
   - Heat Retention: Thick cordierite stone or biscotto floor (>15mm) for high thermal mass.
   - Thermal Barrier: Bio-soluble high-temperature ceramic fiber blanket (minimum 25mm thickness, 128 kg/m³ density) encapsulated so no fibers enter food chamber.
   - Neapolitan 63% Rule: Mouth opening height should be ~63% of the dome interior apex height to maximize radiant heat reflection onto the pizza top while maintaining optimal chimney draft.
   - Exterior Shell: Safe-touch design (<60°C on outer handles/controls at 500°C internal bake temp).

4. **Available Skills**:
   - `anatomy`: Isometric technical explainer diagrams, cutaways, interactive SVG machine figures.
   - `mechanical-engineering`: Sheet metal DFM, bend calculations, thermal expansion joint sizing, GD&T.
   - `code-cad`: Parametric CAD generation, tab-slot alignment, STEP/DXF/STL pipeline.
   - `oshwa-hardware`: Open-source hardware audit, BOM validation, OSHWA checklist.
   - `oven-thermodynamics`: High-temp thermal modeling, heat loss, refractory sizing, burner BTU requirements.
