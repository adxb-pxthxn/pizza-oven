"""CalculiX check for one long-vault wall and the floor stack.

The homogeneous slab in thermal_fea is the film-and-element check. This
file then solves the Stormcloud stack and compares the outer face with the
1D sum. ccx is the distro binary, not the FreeCAD bundle.
"""

from __future__ import annotations

import json
from pathlib import Path

from cad.freecad import thermal_fea as fea
from cad.freecad.stream_physics import T_AMB, Vault, evaluate, floor_resistance

fea.CCX = Path("/usr/bin/ccx")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "design" / "stream-1" / "thermal"


def _shop() -> Vault:
    raw = json.loads((ROOT / "design" / "stream-1" / "optimizer.json").read_text(encoding="utf-8"))
    data = raw["stormcloud"]["design"]
    return Vault(**data)


def _gap_k(vault) -> float:
    """Conductivity that reproduces the button-and-air gap resistance."""
    total = floor_resistance(vault)
    r_fibre = (vault.floor_fibre / 1000.0) / 0.075
    r_base = (vault.base_t / 1000.0) / 160.0
    r_ext = 0.1
    r_gap = total - r_fibre - r_base - r_ext
    return (vault.button_h / 1000.0) / r_gap


def main() -> None:
    vault = _shop()
    report_1d = evaluate(vault)
    OUT.mkdir(parents=True, exist_ok=True)
    slab = fea.slab_check(OUT / "slab")
    print("SLAB", json.dumps(slab))
    if abs(slab["error_C"]) > 1.0:
        raise SystemExit(f"slab check off by {slab['error_C']} C")

    wall_layers = [
        ("liner", vault.liner_t / 1000.0, 16.0),
        ("fibre", vault.fibre_t / 1000.0, 0.075),
        ("air", vault.air_gap / 1000.0, 0.035),
        ("skin", vault.skin_t / 1000.0, 160.0),
    ]
    wall_mesh = fea._mesh_layers(
        wall_layers,
        {"liner": 0.0004, "fibre": 0.012, "air": 0.002, "skin": 0.0005},
    )
    wall_temps = fea._write_and_solve(
        wall_mesh,
        {item[0]: item[2] for item in wall_layers},
        [("bottom", vault.broil_gas, 25.0), ("top", T_AMB, 10.0)],
        OUT / "wall",
    )
    wall_outer = fea._face_mean(wall_mesh, wall_temps, wall_mesh["z_top"])

    gap_k = _gap_k(vault)
    floor_layers = [
        ("gap", vault.button_h / 1000.0, gap_k),
        ("fibre", vault.floor_fibre / 1000.0, 0.075),
        ("base", vault.base_t / 1000.0, 160.0),
    ]
    floor_mesh = fea._mesh_layers(
        floor_layers,
        {"gap": 0.0015, "fibre": 0.008, "base": 0.0005},
    )
    floor_temps = fea._write_and_solve(
        floor_mesh,
        {item[0]: item[2] for item in floor_layers},
        [("bottom", report_1d["floor_C"], 5000.0), ("top", T_AMB, 10.0)],
        OUT / "floor",
    )
    floor_outer = fea._face_mean(floor_mesh, floor_temps, floor_mesh["z_top"])
    payload = {
        "dragon": vault.dragon,
        "slab": slab,
        "wall": {
            "outer_C": round(wall_outer, 2),
            "oned_C": round(report_1d["skin_C"], 2),
            "error_C": round(wall_outer - report_1d["skin_C"], 2),
            "elements": len(wall_mesh["elements"]),
        },
        "floor": {
            "outer_C": round(floor_outer, 2),
            "oned_C": round(report_1d["under_C"], 2),
            "error_C": round(floor_outer - report_1d["under_C"], 2),
            "elements": len(floor_mesh["elements"]),
        },
    }
    dest = ROOT / "design" / "stream-1" / "thermal-fea.json"
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("WROTE", dest)
    print(json.dumps(payload, indent=2))
    if abs(payload["wall"]["error_C"]) > 1.5 or abs(payload["floor"]["error_C"]) > 1.5:
        raise SystemExit("CalculiX disagrees with the 1D sum")


if __name__ == "__main__":
    main()
