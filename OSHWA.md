# Open Source Hardware Statement & Compliance Checklist

## 1. Open Source Hardware Philosophy
This pizza oven hardware project is developed under the principles of the **Open Source Hardware Definition (OSHW v1.0)**. The repository is explicitly created for open physical development, enabling anyone to study, build, modify, and improve the design without proprietary restrictions or vendor lock-in.

---

## 2. Open Hardware Principles Applied

### A. Editable Source Files
- **CAD Source**: Physical parts and assemblies are organized under `cad/parts/` and `cad/assemblies/`.
- **Standard Interchange Formats**:
  - `cad/exports/*.dxf`: 2D cutting profiles for CNC / laser / waterjet fabrication.
  - `cad/exports/*.step`: 3D solid models (ISO 10303 STEP AP214/242) compatible across FreeCAD, Onshape, SolidWorks, and Fusion 360.
  - `cad/exports/*.stl` / `*.3mf`: Meshes for rapid prototyping or additive/casting processes.

### B. Bill of Materials (BOM)
- Located at [`bom/bom.csv`](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/bom/bom.csv).
- Uses the standard OSHWA schema: Part Number, Component Name, Material / Spec, Qty, Category, Vendor / Reference, Estimated Unit Cost, Sourcing Notes.

### C. Licensing
- **Physical Hardware**: [CERN-OHL-P v2](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/LICENSE-HARDWARE) (Permissive open hardware license).
- **Documentation & Media**: [CC-BY-4.0](file:///Users/adib/.gemini/antigravity/scratch/pizza-oven/LICENSE-DOCS) (Creative Commons Attribution 4.0 International).

---

## 3. Open Hardware Checklist

| Requirement | Status | Details / Path |
| :--- | :---: | :--- |
| **Open License (Hardware)** | PASS | CERN-OHL-P v2 (`LICENSE-HARDWARE`) |
| **Open License (Docs)** | PASS | CC-BY-4.0 (`LICENSE-DOCS`) |
| **Parametric / Source CAD** | PASS | `cad/` source tree with open export pipelines |
| **Open Interchange Exports** | PASS | 3D STEP solid models & 2D DXF cutting profiles |
| **BOM Schema** | PASS | `bom/bom.csv` template ready for design items |
| **Audit Verification** | PASS | Verified with `python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py` |
