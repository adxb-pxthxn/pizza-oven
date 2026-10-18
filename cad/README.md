# Pizza Oven CAD Assets & Parametric Engine

This directory contains the parametric Code-CAD generator, 2D sheet metal flat patterns, 3D solids, and interchange files for the open-source Neapolitan pizza oven (certified under **CERN-OHL-P v2** open hardware standards).

---

## 1. Directory Structure

```
cad/
├── model_generator.py          # Master parametric Python CAD generator (zero dependencies)
├── README.md                   # CAD pipeline and manufacturing documentation (this file)
├── assemblies/                 # Assembly reference models and exploded views
├── parts/                      # Component CAD models and fabrication drawings
└── exports/                    # Auto-generated manufacturing deliverables
    ├── pizza_oven_12in_spec.json       # Master parametric specification (12")
    ├── pizza_oven_12in_assembly.stl    # 3D solid mesh for slicers / WebGL
    ├── pizza_oven_12in_assembly.obj    # 3D polygonal model
    ├── pizza_oven_12in.scad            # Live OpenSCAD CSG parametric model
    ├── inner_dome_12in.dxf / .svg      # Unfolded inner flame arch flat pattern
    ├── base_floor_12in.dxf / .svg      # Unfolded base floor & stone support plate
    ├── outer_shroud_12in.dxf / .svg    # Unfolded outer protective casing
    ├── folding_leg_12in.dxf / .svg     # CNC laser cut folding support leg
    └── (16in equivalent assets)        # Scaled 16" wide-deck variants
```

---

## 2. Parametric Hierarchy & Dimensions

All geometry is derived algorithmically from master variables in `cad/model_generator.py`. Switching between the portable 12" variant and the large 16" deck variant recalculates all clearances, draft ratios, and bend reliefs automatically.

| Parameter | 12" Portable Model | 16" Deck Model | Engineering Formula / Rationale |
|---|---|---|---|
| **Baking Stone Dimensions** | 330 × 330 × 15 mm | 406 × 406 × 15 mm | Standard cordierite refractory stone |
| **Inner Chamber Width** | 350.0 mm | 430.0 mm | `W_stone + 20mm` lateral clearance |
| **Inner Chamber Depth** | 440.0 mm | 531.0 mm | `D_stone + rear flame roller zone` |
| **Dome Apex Height ($H_{\text{apex}}$)** | 190.0 mm | 210.0 mm | Optimum radiant focal distance above floor |
| **Mouth Height ($H_{\text{mouth}}$)** | 119.7 mm | 132.3 mm | **Neapolitan 63% Rule**: $0.63 \times H_{\text{apex}}$ |
| **Mouth Width** | 308.0 mm | 378.4 mm | $88\%$ of inner chamber width |
| **Insulation Cavity** | 27.0 mm | 27.0 mm | 25 mm ceramic fiber blanket + 2 mm relief |
| **Inner Hot Chamber Material** | AISI 304 (1.5 mm) | AISI 304 (1.5 mm) | Food-safe high-temp stainless steel |
| **Outer Shroud Material** | AISI 304 / Galvannealed (1.2 mm) | Same (1.2 mm) | Weatherproof, safe-touch envelope |
| **Thermal Expansion ($\Delta L$ at 500°C)** | **3.80 mm** | **4.59 mm** | $\Delta L = \alpha \cdot L \cdot \Delta T$ ($\alpha = 18.0 \times 10^{-6}\text{ /K}$) |
| **Expansion Slot Travel** | **7.0 mm** | **8.5 mm** | $\ge \Delta L + 2.0\text{ mm}$ safety margin |
| **Flue Chimney Diameter** | 100.0 mm (4") | 125.0 mm (5") | Sized for volumetric draft velocity |

---

## 3. Engineering & DFM Design Rules

### A. Neapolitan 63% Mouth Ratio
Traditional Neapolitan wood and gas ovens require an exact opening ratio:
$$\frac{H_{\text{mouth}}}{H_{\text{apex}}} \approx 0.63 \pm 0.02$$
- **Below 0.58**: Chimney draft becomes starved, forcing hot smoke and soot to roll out the front mouth opening.
- **Above 0.68**: Excessive hot air escapes out the front, breaking the rolling flame ceiling and preventing 90-second Neapolitan bakes.

### B. Thermal Expansion Compensation (500°C Firebox)
At peak 500°C Neapolitan operating temperature, the inner stainless dome expands by nearly $4\text{ mm}$ axially ($\approx 4.59\text{ mm}$ on 16" models), while the outer shroud remains below $60^\circ\text{C}$ ($\Delta T \approx 35\text{ K}$, expanding $<0.3\text{ mm}$).
- **Rigid fastening between inner and outer shells is strictly forbidden.**
- The inner dome mounts to the base floor and front baffle using **longitudinal slotted holes** ($7.0\text{ mm}$ travel on 12", $8.5\text{ mm}$ travel on 16").
- Fasteners utilize shoulder bolts with Belleville spring washers to allow free sliding without rattling or binding.

### C. Laser Cutting & Press Brake DFM
- **Hole Diameters**: Minimum hole diameter is $4.2\text{ mm}$ ($2.8 \times t$), exceeding the $1.0 \times t$ fiber laser pierce limit to avoid slag and hardening.
- **Web Thickness**: Minimum distance between any cutout and edge is $\ge 4.0\text{ mm}$ ($2.6 \times t$), preventing laser heat warp.
- **Tab & Slot Joinery**: Tabs are $16.0\text{ mm}$ wide with $+0.25\text{ mm}$ clearance per side. Internal corners incorporate dogbone reliefs ($\varnothing 1.2\text{ mm}$) to ensure square tabs seat flush without interference from the laser beam radius.
- **DXF Layers**:
  - `CUT`: Outer boundary cut.
  - `CUT_INTERIOR`: Slotted holes, tab receivers, flue cutout.
  - `BEND_UP` / `BEND_DOWN`: Forming bend centerlines.
  - `ETCH`: Part numbering and alignment guides.

---

## 4. Usage & Asset Generation

### Prerequisites
The generator and validator run on standard **Python 3.8+** with **zero external package dependencies**.

### Generate All CAD Deliverables
```bash
# Generate 12-inch portable model (DXF, SVG, STL, OBJ, SCAD, JSON)
python3 cad/model_generator.py --stone 12 --format all --out-dir cad/exports

# Generate 16-inch wide deck model
python3 cad/model_generator.py --stone 16 --format all --out-dir cad/exports
```

### Selective Format Generation
```bash
# Generate only laser-cutting DXFs for 12"
python3 cad/model_generator.py --stone 12 --format dxf --out-dir cad/exports

# Generate 3D STL mesh for 3D printing / visualization
python3 cad/model_generator.py --stone 12 --format stl --out-dir cad/exports

# Generate OpenSCAD model
python3 cad/model_generator.py --stone 12 --format scad --out-dir cad/exports
```

---

## 5. Automated DFM & Parametric Validation

Run the automated engineering audit suite to verify all geometric and thermal constraints before ordering laser-cut parts:

```bash
# Validate generated 12" parametric specification
python3 .agents/skills/code-cad/scripts/cad_validate.py --spec cad/exports/pizza_oven_12in_spec.json

# Validate generated 16" parametric specification
python3 .agents/skills/code-cad/scripts/cad_validate.py --spec cad/exports/pizza_oven_16in_spec.json

# Validate DXF laser flat pattern directly
python3 .agents/skills/code-cad/scripts/cad_validate.py --dxf cad/exports/inner_dome_12in.dxf --thickness 1.5
python3 .agents/skills/code-cad/scripts/cad_validate.py --dxf cad/exports/outer_shroud_12in.dxf --thickness 1.2
```

---

## 6. Software & CAM Compatibility

| Format | Compatible Software | Purpose |
|---|---|---|
| `.dxf` | AutoCAD, LibreCAD, DraftSight, Radan, SigmaNEST, LightBurn | CNC laser/waterjet cutting and sheet metal nesting |
| `.svg` | Inkscape, Illustrator, Web browsers | 2D technical drawings, documentation, assembly guides |
| `.scad` | OpenSCAD (Desktop & CLI) | Interactive 3D parameter tuning and CSG inspection |
| `.stl` / `.obj` | Blender, FreeCAD, PrusaSlicer, Bambu Studio, MeshLab | 3D visualization, mockups, scale 3D printing |
| `.json` | Python, Node.js, CI/CD scripts | Machine-readable parametric specs and BOM pipelines |
