# Parametric CAD

Editable source is Python using [build123d](https://build123d.readthedocs.io/) (OpenCASCADE). The checked-in geometry is a **placeholder**: a square floor slab, a half-cylinder dome shell, and a concentric insulation layer. Dimensions live in `parameters.py` and are millimetres. They are round placeholder numbers, not a capacity, a material call, or a commercial product.

Generated STEP and STL go to `cad/output/`, which is gitignored. Do not commit them. `cad/exports/` stays empty until a real design is ready to publish.

## Layout

```
cad/
├── parameters.py          # named dimensions, millimetres
├── parts/                 # floor stone, dome shell, insulation
├── assemblies/
│   └── placeholder.py     # regenerates the assembly from parameters
├── build.py               # python3 -m cad.build
├── tests/
├── requirements.txt       # pinned kernel
├── requirements-preview.txt
├── output/                # gitignored STEP + STL
└── exports/               # curated releases only; the build does not write here
```

Pins also live in the repo-root `pyproject.toml`.

## Install

Python **3.11, 3.12, 3.13, or 3.14**. build123d 0.13 does not support 3.10 or 3.15.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r cad/requirements.txt
```

uv:

```bash
uv venv
source .venv/bin/activate
uv pip install -r cad/requirements.txt
```

Or install the project, including the optional viewer extra:

```bash
python3 -m pip install -e ".[preview]"
```

Pinned versions:

| Package | Version | Role |
|---|---|---|
| `build123d` | 0.13.0 | Modelling API |
| `cadquery-ocp-novtk` | 8.0.1.1.0 | OCCT 8.0 bindings, no VTK |
| `ocp-vscode` | 4.2.0 | Optional Cursor / VS Code preview |

## macOS Apple Silicon

`cadquery-ocp-novtk==8.0.1.1.0` publishes a native wheel:

`cadquery_ocp_novtk-8.0.1.1.0-cp312-cp312-macosx_11_0_arm64.whl`

(and the same tag for CPython 3.11, 3.13, and 3.14). pip and uv select it when the interpreter is arm64. macOS 11 or newer.

Check the interpreter before installing:

```bash
python3 -c "import platform; print(platform.python_version(), platform.machine())"
```

`arm64` is the native Apple Silicon build. `x86_64` means Rosetta or an Intel Homebrew Python; that interpreter gets the Intel wheel instead. Mixing the two in one virtualenv is the usual way the install picks the wrong wheel.

If pip tries to **build** `cadquery-ocp-novtk` from source, stop. A wheel was not selected. Do not compile OCCT locally. Fix the Python version (3.11–3.14) and the architecture, then install again.

Use `cadquery-ocp-novtk`, not the older `cadquery-ocp` 7.7 line. That older package often had no macOS arm64 wheel, so pip fell through to a source build and failed. The 7.7 and 8.x stacks also both ship a module named `OCP` and will clash if they land in the same environment. The novtk wheel has no VTK. STEP export, STL export, and `ocp_vscode` do not need VTK.

Prefer a fresh venv. A conda environment that already has OCCT or CadQuery loaded will collide with this wheel.

The cloud VM (Linux x86_64, Python 3.12) uses the matching `manylinux_2_28_x86_64` wheel from the same pin. The default Cloud Agent image does not preinstall it; install with the commands above when you are building or testing CAD.

## Build

From the repository root, with the venv activated:

```bash
python3 -m cad.build
```

That writes:

- `cad/output/placeholder_oven_assembly.step` — STEP AP214 (`AUTOMOTIVE_DESIGN`), millimetres, one assembly with three named solids
- `cad/output/placeholder_oven_assembly.stl` — binary STL of the same assembly (linear deflection 0.05 mm, angular deflection 0.08 rad)

Optional destination:

```bash
python3 -m cad.build --out-dir /tmp/oven-cad
```

## Test

```bash
python3 -m unittest cad.tests.test_placeholder_assembly
```

The geometry tests build the model, check volume and bounding box against the parameters, and check that a thickness edit moves the solid. They skip if build123d is not installed. Parameter validation and the gitignore check always run.

The existing stdlib test is unchanged:

```bash
python3 .agents/skills/material-sourcing/tests/test_material_sourcing.py
```

## Preview in Cursor or VS Code

1. Install the extension **OCP CAD Viewer** (`bernhard-42.ocp-cad-viewer`), 4.2.0 or the current 4.x release.
2. Select the venv as the Python interpreter. The viewer uses that interpreter.
3. Install the preview extra into that same venv: `python3 -m pip install -r cad/requirements-preview.txt`
4. Skip the extension's **Quickstart build123d** button. It installs an unpinned build123d and can drift off these pins.
5. Run a short script with **Run Without Debugging** (macOS `⌃F5`):

```python
from cad.assemblies.placeholder import build_placeholder_assembly
from ocp_vscode import show

show(build_placeholder_assembly())
```

`show` sends the shape to the viewer. It does not write a file.

## Open the STEP in FreeCAD and Fusion 360

The STEP file is AP214, millimetres, with three product names: `floor_stone`, `dome_shell`, `insulation_layer`.

**FreeCAD:** File → Open, or File → Import, and choose the `.step`. The assembly tree lists the three solids. FreeCAD reads AP214 and AP242; this export is AP214 so the unit block is explicit (`SI_UNIT(.MILLI.,.METRE.)`).

**Fusion 360:** File → Open (or Upload) the `.step`. Fusion imports it as a design with the three bodies. Confirm the document units are millimetres after import. Fusion reads this AP214 file; it does not need a Fusion archive (`.f3d`).

STL is a mesh for printing and quick preview. It is not the editable source. Edit `parameters.py`, then run the build again.
