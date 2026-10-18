"""Export reconstructed ovens to STEP AP214 and STL, plus a mass report.

    python3 -m cad.reconstructed.export_all
    python3 -m cad.reconstructed.export_all --out-dir research/argon-anatomy/models
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from OCP.Interface import Interface_Static
from build123d import Unit, export_step, export_stl

from cad.reconstructed.model import build_oven, mass_report
from cad.reconstructed.spec import OVENS

# Coarser than a machining mesh. These are study models, and 0.15 mm on a
# metre-long shell makes a needlessly large STL. Linear deflection is still
# well under a millimetre.
STL_LINEAR_MM = 0.35
STL_ANGULAR_RAD = 0.25
STEP_SCHEMA = "AP214IS"

DEFAULT_OUT = Path(__file__).resolve().parents[2] / "research" / "argon-anatomy" / "models"


def _write(assembly, out_dir: Path, stem: str) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    step_path = out_dir / f"{stem}.step"
    stl_path = out_dir / f"{stem}.stl"
    Interface_Static.SetCVal_s("write.step.schema", STEP_SCHEMA)
    export_step(assembly, step_path, unit=Unit.MM)
    wrote = export_stl(
        assembly,
        stl_path,
        tolerance=STL_LINEAR_MM,
        angular_tolerance=STL_ANGULAR_RAD,
    )
    if not wrote:
        raise RuntimeError(f"STL export failed for {stem}")
    return {"step": str(step_path), "stl": str(stl_path)}


def export_all(out_dir: Path) -> dict:
    """Write assembled, cutaway, and (Dome XL) exploded solids."""
    manifest: dict = {"units": "mm", "step_schema": "AP214", "ovens": {}}
    for spec in OVENS:
        assembled = build_oven(spec)
        cutaway = build_oven(spec, cutaway=True)
        record = {
            "model_no": spec.model_no,
            "published_mm": {
                "external": [spec.ext_w, spec.ext_d, spec.ext_h_published],
                "internal": [spec.int_w, spec.int_d, spec.int_h],
                "mouth": [spec.mouth_w, spec.mouth_h],
            },
            "inferred": {
                "body_h_mm": spec.body_h,
                "hearth_z_mm": spec.hearth_z,
                "side_wall_mm": spec.side_wall,
                "air_gap_mm": round(spec.air_gap, 2),
                "roof_space_mm": spec.roof_space,
                "mouth_over_apex": round(spec.mouth_over_apex, 4),
                "insulation_mm": list(spec.insulation_mm),
            },
            "notes": spec.notes,
            "mass_kg": mass_report(spec, assembled),
            "files": {
                "assembled": _write(assembled, out_dir, spec.oven_id),
                "cutaway": _write(cutaway, out_dir, f"{spec.oven_id}-cutaway"),
            },
        }
        if spec.flue:
            exploded = build_oven(spec, explode=80)
            record["files"]["exploded"] = _write(exploded, out_dir, f"{spec.oven_id}-exploded")
        manifest["ovens"][spec.oven_id] = record
        print(spec.oven_id, record["mass_kg"]["total_kg"], "kg modelled vs", spec.mass_kg, "published")
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export reconstructed Gozney envelopes.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    export_all(args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
