# CAD Assets & Models

This directory contains the physical CAD assets, source scripts, and manufacturing exports for the open-source pizza oven project.

## Directory Structure

```
cad/
├── parts/          # Component models and part source files
├── assemblies/     # Master assembly models and sub-assemblies
└── exports/        # Interchange and fabrication deliverables (STEP, DXF, STL, 3MF)
```

## Recommended File Conventions

- **Source Formats:** Code-CAD scripts (Python/build123d/CadQuery/OpenSCAD) or native parametric files.
- **2D Laser / CNC Cutting:** DXF (AutoCAD R12/2000 format) with separated layers (`CUT`, `BEND`, `ETCH`).
- **3D Interchange:** STEP (AP214 or AP242) for solids.
- **Meshes:** STL / 3MF / OBJ for visualization and 3D printing/casting.

All specific design models will be added here once design requirements and parameters are defined.
