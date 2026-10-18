---
name: cad
description: Conventions for editing the pizza-oven build123d model. Use when changing cad/parameters.py, part builders, the placeholder assembly, STEP/STL export, or CAD tests.
license: CERN-OHL-P v2 / MIT
compatibility: Python 3.11–3.14, build123d 0.13, cadquery-ocp-novtk 8.0.1.1.0
---

# Parametric CAD conventions

The editable model is Python in `cad/`. build123d is the kernel. STEP and STL are generated into gitignored `cad/output/` and are not source.

The geometry checked in today is a placeholder (floor slab, half-cylinder shell, insulation layer). Do not treat its numbers as a chosen oven, and do not replace them with a commercial product's dimensions.

## Where numbers live

- All lengths are millimetres, named fields on `OvenParameters` in `cad/parameters.py`.
- Part modules take an `OvenParameters` and read fields from it. Do not hardcode a second copy of a dimension in a builder.
- Derived sizes (dome outer radius, insulation radii) are properties on `OvenParameters`. Add new derived sizes there.
- A new solid gets a stable `label` used as the STEP product name, set in the builder.
- Display `Color` values are viewer tints only. They do not select a material.
- Do not add a placeholder solid to `bom/bom.csv`. BOM rows start when a real part is specified.

## Axis

X across the floor, Y along the dome axis, Z up. The stone's top face is z = 0. Shells sit on that plane and rise in +Z.

`cad/parts/shell.py` builds the half-tube. `split(..., Plane.XZ, keep=Keep.TOP)` keeps the negative-Y half of a Z-axis cylinder; `Rot(-90, 0, 0)` lays it along Y. Do not "correct" that rotation without re-running the bounding-box test.

## Build, test, export

From the repo root, after `pip install -r cad/requirements.txt` (see `cad/README.md` for the macOS arm64 wheel notes):

```bash
python3 -m cad.build
python3 -m unittest cad.tests.test_placeholder_assembly
```

`python3 -m cad.build` writes AP214 STEP (millimetres) and binary STL. It must not write `cad/exports/` and must not leave STEP/STL in git. `cad/output/` is gitignored. The unanchored gitignore pattern `parts/` was narrowed to `/parts/` so `cad/parts/` stays tracked.

When a parameter changes, the geometry tests recompute the expected volume and bounding box from `OvenParameters`. Update those expectations only by changing the formulas, not by pasting a measured volume.

## Preview and interchange

- Cursor / VS Code: OCP CAD Viewer plus `ocp_vscode.show`. Install `cad/requirements-preview.txt`. Do not use the extension Quickstart; it upgrades build123d off the pin.
- FreeCAD and Fusion 360 open the STEP file. STL is a mesh, not the source.
- Kernel pin: `build123d==0.13.0` and `cadquery-ocp-novtk==8.0.1.1.0`. Do not add the VTK package `cadquery-ocp` to the same environment.

## What this skill does not decide

Fuel, materials, sheet thickness, stone product, mouth size, and manufacturing method stay unset until the user specifies them. The code-cad skill (`.agents/skills/code-cad/SKILL.md`) holds general DFM rules for when that work starts.
