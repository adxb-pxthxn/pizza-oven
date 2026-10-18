"""Export the Angas 430 to STEP AP214 and STL.

    python3 -m cad.tailgate.export_all
    python3 -m cad.tailgate.export_all --out-dir design/tailgate/models
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from OCP.Interface import Interface_Static
from build123d import Unit, export_step, export_stl

from cad.tailgate.model import build, mass_report
from cad.tailgate.spec import SPEC, skin_temperature

STL_LINEAR_MM = 0.55
STL_ANGULAR_RAD = 0.22
STEP_SCHEMA = "AP214IS"
DEFAULT_OUT = Path(__file__).resolve().parents[2] / "design" / "tailgate" / "models"


def _write(assembly, out_dir: Path, stem: str, stl: bool = True) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    step_path = out_dir / f"{stem}.step"
    Interface_Static.SetCVal_s("write.step.schema", STEP_SCHEMA)
    export_step(assembly, step_path, unit=Unit.MM)
    record = {"step": str(step_path)}
    if stl:
        stl_path = out_dir / f"{stem}.stl"
        wrote = export_stl(assembly, stl_path, tolerance=STL_LINEAR_MM, angular_tolerance=STL_ANGULAR_RAD)
        if not wrote:
            raise RuntimeError(f"STL export failed for {stem}")
        record["stl"] = str(stl_path)
    return record


def export_all(out_dir: Path) -> dict:
    table = build(deployed_legs=False)
    tripod = build(deployed_legs=True)
    exploded = build(explode=90, deployed_legs=False)
    cutaway = build(cutaway=True, deployed_legs=False)
    stowed = build(stowed=True, deployed_legs=False)
    manifest = {
        "name": SPEC.name,
        "units": "mm",
        "step_schema": "AP214",
        "envelope": {
            "outer_diameter_mm": round(SPEC.outer_diameter, 1),
            "body_height_mm": round(SPEC.body_height, 1),
            "handle_span_mm": round(SPEC.handle_span, 1),
            "floor_diameter_mm": SPEC.floor_d,
            "chamber_id_mm": SPEC.chamber_id,
            "apex_mm": SPEC.apex_h,
            "mouth_mm": [SPEC.mouth_w, SPEC.mouth_h],
            "mouth_over_apex": round(SPEC.mouth_over_apex, 3),
        },
        "skin_C": {
            "wall": skin_temperature(SPEC.wall_aes, SPEC.wall_casi),
            "crown": skin_temperature(SPEC.crown_aes),
        },
        "mass_kg": {key: value for key, value in mass_report(table).items() if key != "rows"},
        "files": {
            "table": _write(table, out_dir, "angas-430"),
            "tripod": _write(tripod, out_dir, "angas-430-tripod"),
            "exploded": _write(exploded, out_dir, "angas-430-exploded"),
            "cutaway": _write(cutaway, out_dir, "angas-430-cutaway"),
            "stowed": _write(stowed, out_dir, "angas-430-stowed", stl=True),
        },
    }
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["mass_kg"], indent=2))
    print("envelope", json.dumps(manifest["envelope"]))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    export_all(args.out_dir)


if __name__ == "__main__":
    main()
