# Open Source Hardware Statement & Compliance Checklist

## 1. Open Source Hardware Philosophy
This high-performance portable Neapolitan pizza oven is developed under the principles of the **Open Source Hardware Definition (OSHW v1.0)**. The design is explicitly created for DIY makers, hobbyists, and open hardware enthusiasts who want commercial-grade 500°C pizza baking capability built from accessible, off-the-shelf components and flat-pattern sheet metal services.

Anyone is free to build, study, modify, improve, and share this hardware without proprietary restrictions or vendor lock-in.

---

## 2. Open Hardware Principles Applied

### A. Editable Source Files
- **Parametric CAD Source**: All structural parts are designed with parametric code-CAD / open CAD workflows located under `cad/parts/` and `cad/assemblies/`.
- **Standard Interchange Formats**:
  - `cad/exports/*.dxf`: 2D flat patterns ready for direct CNC laser/waterjet cutting (e.g. SendCutSend, Xometry, or local maker spaces).
  - `cad/exports/*.step`: 3D solids (ISO 10303 STEP AP214) compatible with FreeCAD, Onshape, SolidWorks, and Fusion 360.

### B. Complete Bill of Materials (BOM)
- Located at [`bom/bom.csv`](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/bom/bom.csv).
- Every single part includes: Part Number, Component Name, Material Specification, Quantity, Vendor/Reference, Estimated Unit Cost, and Sourcing Notes.
- Uses standard off-the-shelf fasteners (M5/M4 stainless steel) and commercial BBQ/burner hardware.

### C. Accessible DIY Assembly
- Documented in [`docs/assembly-guide.md`](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/docs/assembly-guide.md).
- Designed for **zero-welding assembly**: Tab-and-slot interlocking sheet metal joined by standard stainless button-head bolts and rivets.
- Can be assembled using basic hand tools (hex keys, wrench, and hand rivet gun).

### D. Clear Dual Licensing
- **Physical Hardware & Schematics**: [CERN-OHL-P v2](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/LICENSE-HARDWARE) (Permissive variant).
- **Documentation & Media**: [CC-BY-4.0](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/LICENSE-DOCS) (Creative Commons Attribution 4.0 International).

---

## 3. Open Hardware Checklist

| Requirement | Status | Details / Path |
| :--- | :---: | :--- |
| **Open License (Hardware)** |  PASS | CERN-OHL-P v2 (`LICENSE-HARDWARE`) |
| **Open License (Docs)** |  PASS | CC-BY-4.0 (`LICENSE-DOCS`) |
| **Parametric / Source CAD** |  PASS | `cad/` source tree with open export pipelines |
| **Open Interchange Exports** |  PASS | 3D STEP solid models & 2D DXF cutting profiles |
| **Comprehensive BOM** |  PASS | `bom/bom.csv` with 20 items, pricing & sourcing |
| **Assembly Documentation** |  PASS | `docs/assembly-guide.md` with step-by-step procedures |
| **Safe DIY Construction** |  PASS | Encapsulated ceramic fiber, flame failure device, safe exterior |
| **Reproducibility Test** |  PASS | Verified with `python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py` |

---

## 4. Hardware Attribution & Marking
When manufacturing physical units or derivative designs:
1. Retain the project identifier: `Open-Pizza-Oven / Neapolitan 500`.
2. Cite the CERN-OHL-P v2 license and project repository in documentation.
3. If modifying dimensions, state the modifications clearly to preserve safety envelopes (combustion airflow and insulation thickness).
