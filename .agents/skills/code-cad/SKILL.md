---
name: code-cad
description: Parametric Code-CAD engineering and design for manufacturing (DFM). Covers programmatic CAD modeling in Python (build123d, CadQuery paradigms, pure Python geometric generators), OpenSCAD, and FreeCAD headless scripting; parametric hierarchy and mathematical dimension propagation; sheet metal unfolding and 2D DXF/SVG generation; 3D interchange formats (STEP AP214/AP242, STL/3MF); and precision laser-cut tab-and-slot joinery with thermal expansion relief slots.
license: CERN-OHL-P v2 / MIT
compatibility: Runs with Python 3.10+, OpenSCAD, FreeCAD CLI, and CadQuery/build123d.
metadata:
  opencode/slash: "true"
---

# Code-CAD & Parametric Design Skill

This skill guides the design, parametric modeling, DFM validation, and production export of precision mechanical hardware using code-first CAD paradigms.

Code-CAD replaces manual GUI point-and-click modeling with programmable, version-controlled scripts (Git diffs, parametric configs, automated test suites). It enables instant dimensional variations (e.g., switching a pizza oven from 12-inch to 16-inch baking stone with zero manual redrawing), automated sheet metal unfolding for CNC fiber laser cutting, and verifiable compliance with thermodynamic and structural constraints.

---

## 1. Supported Toolchains & Paradigms

| Toolchain | Paradigm | Primary Outputs | Best Used For |
|---|---|---|---|
| **build123d** | Fluent/Imperative Python 3 on OpenCASCADE | STEP (AP214/242), SVG, DXF, 3MF | Complex modern 3D parametric solids, assemblies, joints |
| **CadQuery 2** | Fluent Python on OpenCASCADE (CQGI) | STEP, STL, DXF, SVG | Stable production parametric solid modeling |
| **OpenSCAD** | Pure Declarative CSG Scripting | STL, 3MF, DXF, CSG | Quick geometric booleans, mathematical surfaces, universal CLI |
| **FreeCAD Headless** | Python Scripting (`Part`, `Draft`, `SheetMetal`) | STEP, IGES, FCStd, Flat DXF | Native sheet metal unfolding with K-factors, automated drawing generation |
| **Pure Python Generator** | Standard library vector math & raw DXF/SVG/STL | DXF R12, SVG, STL, OBJ, JSON | Zero-dependency environments, CI/CD pipelines, rapid file delivery |

---

## 2. Parametric Hierarchy & Master Dimension Propagation

In a well-engineered Code-CAD project, every dimensional feature derives from a strict acyclic dependency tree. No magic numbers or hardcoded coordinates exist in part definitions.

```
                  ┌───────────────────────────────┐
                  │ Master Parameters             │
                  │ - Stone Size (e.g. 12" / 16") │
                  │ - Insulation Cavity (25 mm)   │
                  │ - Target Apex Height          │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌───────────────────────────────┐         ┌───────────────────────────────┐
│ Hot Inner Chamber (304 SS)    │         │ Outer Shroud & Insulation     │
│ - Floor Width: W_stone + 20mm │         │ - Cavity Gap: 25mm + 1.25mm   │
│ - Depth: D_stone + 40mm       │         │ - Shroud Width: W_in + 2*C_ins│
│ - Apex Height: H_apex         │         │ - Shroud Length: L_in + C_ins │
│ - Mouth H = 0.63 * H_apex     │         │ - Air gap standoffs           │
└───────────────┬───────────────┘         └───────────────┬───────────────┘
                │                                         │
                ▼                                         ▼
┌───────────────────────────────┐         ┌───────────────────────────────┐
│ Thermal Expansion Relief      │         │ Structural & Mount Elements   │
│ - ΔL = α * L * ΔT             │         │ - Tab & Slot Interlocks       │
│ - Slotted mounting ears       │         │ - Leg folding pivot bracket   │
│ - Free floating stone tray    │         │ - Flue chimney collar (100mm) │
└───────────────────────────────┘         └───────────────────────────────┘
```

### Master Dimension Variables
1. **Baking Floor Dimensions**:
   - `floor_width`: Stone width plus lateral clearance ($+15\text{ to }20\text{ mm}$ for stone thermal growth and insertion ease).
   - `floor_depth`: Stone depth plus rear combustion gas turn-around clearance ($+40\text{ to }60\text{ mm}$).
   - `stone_thickness`: $15.0\text{ mm}$ (standard cordierite) up to $25.0\text{ mm}$ (Biscotto di Sorrento).
2. **Combustion & Dome Geometry**:
   - `dome_height_apex`: Interior arch apex above baking floor (typically $180 - 220\text{ mm}$).
   - `mouth_height`: Governed by the **Neapolitan 63% Rule**:
     $$H_{\text{mouth}} = 0.63 \times H_{\text{apex}} \pm 5\%$$
     *Rationale*: A mouth opening lower than $0.63 \times H_{\text{apex}}$ restricts flue intake and induces front flame rollout. A mouth higher than $0.63$ lets radiant heat escape directly instead of reflecting downward onto the pizza surface.
   - `mouth_width`: Typically $80 - 85\%$ of inner chamber width.
   - `flue_diameter`: Sized to exhaust chamber volume. For a 12" oven: $100\text{ mm}$ ($4\text{"}$); for a 16" oven: $125\text{ mm}$ ($5\text{"}$).
3. **Thermal Boundary Layers**:
   - `insulation_cavity`: $25.0\text{ mm}$ nominal space for bio-soluble ceramic fiber blanket (128 kg/m³ density), compressed to $\approx 23\text{ mm}$ at assembly for snug thermal contact without thermal bridging.
   - `sheet_thickness_inner`: $1.5\text{ mm}$ or $2.0\text{ mm}$ AISI 304 food-grade stainless steel.
   - `sheet_thickness_outer`: $1.2\text{ mm}$ or $1.5\text{ mm}$ AISI 304 or powder-coated galvannealed steel.

---

## 3. Sheet Metal DFM & Laser Cutting Design Rules

Designing for CNC fiber laser cutting and CNC press brake bending requires strict geometric rules:

### Laser Cutting Design Rules
1. **Minimum Hole Diameter ($d_{\min}$)**:
   - For stainless steel: $d \ge 1.0 \times t$ (sheet thickness), ideally $d \ge 1.2 \times t$.
   - Holes smaller than $1.0t$ overheat during laser piercing, causing thermal blowouts, localized hardening, and nozzle slag.
2. **Minimum Web / Bridge Thickness ($w_{\min}$)**:
   - The solid metal distance between any two cutouts or between a cutout and an edge must be $\ge 2.0 \times t$.
   - Narrow bridges warp under the concentrated thermal stress of the laser beam.
3. **Tab and Slot Construction**:
   - **Tab Width**: $12.0 - 25.0\text{ mm}$.
   - **Tab Height**: Equal to receiver sheet thickness $t + 0.2\text{ mm}$ (flush sanding or spot TIG tack) or $t + 2.0\text{ mm}$ with a locking cotter pin/twist slot.
   - **Slot Width (Receiver)**: $t + 2 \times \text{clearance}$.
     - Laser mill-finish stainless: clearance $= +0.15\text{ to }+0.20\text{ mm}$ per side.
     - Powder-coated parts: clearance $= +0.30\text{ to }+0.40\text{ mm}$ per side.
   - **Corner Reliefs (Dogbone / T-Bone)**:
     - Laser beams leave a minimum inside corner radius equal to beam radius ($r_{\text{beam}} \approx 0.10 - 0.15\text{ mm}$).
     - For square tabs to seat fully flush against the base without rocking on corner radii, place circular or oval reliefs ($\varnothing \ge 1.0\text{ mm}$) at internal corners.
4. **Thermal Relief Expansion Slots**:
   - High-temperature components expand drastically compared to cool outer frames.
   - **Calculation**:
     $$\Delta L = \alpha \cdot L_0 \cdot \Delta T$$
     Where for AISI 304 stainless steel:
     - Thermal expansion coefficient $\alpha \approx 18.0 \times 10^{-6}\text{ K}^{-1}$
     - Length $L_0 = 500\text{ mm}$
     - $\Delta T = 500^\circ\text{C} - 20^\circ\text{C} = 480\text{ K}$
     $$\Delta L = 18.0 \times 10^{-6} \times 500 \times 480 \approx 4.32\text{ mm}$$
   - **Design Rule**: Inner dome mounting ears MUST NOT use round screw holes. Use longitudinal slotted holes with length $\ge \Delta L + 2.5\text{ mm}$ ($7.0\text{ mm}$ minimum travel) with shoulder bolts, spring disc washers (Belleville), or floating clip guides.

### Press Brake Bending Rules
1. **Bend Allowance & K-Factor**:
   $$\text{Bend Deduction} = 2(R_b + t)\tan(\theta/2) - BA$$
   $$BA = \frac{\pi}{180} \cdot (R_b + K \cdot t) \cdot \theta$$
   - Standard K-factor for AISI 304 cold air bending: $K \approx 0.42$.
   - Minimum internal bend radius: $R_b \ge 1.0 \times t$ for 304 austenitic stainless.
2. **Minimum Flange Length ($b_{\min}$)**:
   - Must be $\ge 4.0 \times t$ to bridge the press brake V-die opening without slipping.
   - For $t = 1.5\text{ mm}$, minimum flange is $6.0\text{ mm}$ (standard practice: $\ge 10.0\text{ mm}$).
3. **Bend Relief Cutouts**:
   - Any flange not spanning the full sheet width requires rectangular or tear-drop relief notches at the bend ends.
   - Relief depth: $\ge R_b + t$. Relief width: $\ge t$ (minimum $1.5\text{ mm}$).

---

## 4. Multi-Layer DXF & Interchange Conventions

When exporting flat sheet metal patterns to laser cutting nesting software (e.g. Radan, TruTops, SigmaNEST):

### Standard DXF Layer Table
| Layer Name | Color Index | Linetype | Purpose |
|---|---|---|---|
| `CUT` | 7 (White/Black) | Continuous | Outer boundary silhouette cut |
| `CUT_INTERIOR` | 4 (Cyan) | Continuous | Holes, slots, tab receivers, internal drops |
| `BEND_UP` | 3 (Green) | Dashed (`DASHED2`) | 90° upward bend centerline |
| `BEND_DOWN` | 2 (Yellow) | Center (`CENTER2`) | 90° downward bend centerline |
| `ETCH` / `MARK` | 1 (Red) | Continuous | Surface laser etching (part number, bend angle) |
| `STOCK_BORDER` | 8 (Dark Gray) | Continuous | Blank stock boundary / nesting margin |

### 3D CAD Interchange Formats
- **STEP AP242 / AP214**: The authoritative standard for 3D solid geometry with Product and Manufacturing Information (PMI), GD&T, and assembly hierarchies.
- **STL / 3MF**: Tessellated meshes for 3D printing and WebGL viewing. Ensure chordal deviation $< 0.05\text{ mm}$ and angular deflection $< 5^\circ$ to prevent faceted curves on circular chimney collars.

---

## 5. Workflow for Parametric Modeling

When generating or modifying CAD models in this repository:

1. **Inspect / Update Master Parameters**:
   - Edit named millimetre fields on `OvenParameters` in `cad/parameters.py`. Part builders take that object and do not keep a second copy of a dimension.
   - The values checked in with the toolchain are a generic placeholder. Do not replace them with a commercial product's dimensions.
2. **Run Geometric & DFM Validation**:
   - Execute `python3 -m unittest cad.tests.test_placeholder_assembly` after installing `cad/requirements.txt`.
   - Execute `.agents/skills/code-cad/scripts/cad_validate.py` against a specification once one exists.
   - Verify minimum hole diameters, bridge thicknesses, and thermal expansion slot travel when those features exist.
3. **Generate Assets**:
   - Run `python3 -m cad.build`
   - That writes STEP AP214 and STL to gitignored `cad/output/`. Do not commit those files. `cad/exports/` is for a published release, not for this command.
4. **Verify Assembly Clearances**:
   - Check that insulation blanket cavity has $>25\text{ mm}$ clearance everywhere between hot dome and outer shroud.
   - Check that stone slides freely with $5\text{ mm}$ clearance on all sides.
