"""Export the placeholder assembly to STEP (AP214, millimetres) and STL.

    python3 -m cad.build
    python3 -m cad.build --out-dir /tmp/oven-cad

Writes into ``cad/output/`` unless ``--out-dir`` is set. That directory
is gitignored. This command does not write ``cad/exports/``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from OCP.Interface import Interface_Static
from build123d import Compound, Unit, export_step, export_stl

from cad.assemblies.placeholder import build_placeholder_assembly
from cad.parameters import ASSEMBLY_LABEL

# Chordal deviation stays under 0.05 mm. 0.08 rad is about 4.6 degrees.
STL_LINEAR_DEFLECTION_MM = 0.05
STL_ANGULAR_DEFLECTION_RAD = 0.08
STEP_SCHEMA = "AP214IS"

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def export_assembly(assembly: Compound, out_dir: Path) -> tuple[Path, Path]:
    """Write ``<label>.step`` and ``<label>.stl`` into ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = assembly.label or ASSEMBLY_LABEL
    step_path = out_dir / f"{stem}.step"
    stl_path = out_dir / f"{stem}.stl"

    Interface_Static.SetCVal_s("write.step.schema", STEP_SCHEMA)
    export_step(assembly, step_path, unit=Unit.MM)
    wrote_stl = export_stl(
        assembly,
        stl_path,
        tolerance=STL_LINEAR_DEFLECTION_MM,
        angular_tolerance=STL_ANGULAR_DEFLECTION_RAD,
    )
    if not wrote_stl:
        raise RuntimeError(f"Failed to write STL: {stl_path}")
    return step_path, stl_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export the placeholder oven assembly to STEP and STL.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Destination directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args(argv)
    step_path, stl_path = export_assembly(build_placeholder_assembly(), args.out_dir)
    print(step_path)
    print(stl_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
