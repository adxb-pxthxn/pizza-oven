"""1D wall temperatures for the tailgate oven stacks.

Same resistance network as research/argon-anatomy/calcs/hardwood_shell.py.
Layers are (name, thickness_mm, k). Films are added by the solver.

    python3 design/tailgate/calcs/thermal.py
"""

from __future__ import annotations

import json
from pathlib import Path


T_GAS_C = 500.0
T_AMB_C = 20.0
H_IN = 25.0
H_EXT = 10.0


def solve(layers: list[tuple[str, float, float]], t_gas: float = T_GAS_C, t_amb: float = T_AMB_C,
          h_ext: float = H_EXT) -> dict:
    """layers: (name, thickness_mm, k) from the hot gas outward. Films included here."""
    named = [("gas film", 1.0 / H_IN)]
    for name, thickness_mm, k in layers:
        named.append((name, (thickness_mm / 1000.0) / k))
    named.append(("outside air", 1.0 / h_ext))
    r_total = sum(r for _, r in named)
    flux = (t_gas - t_amb) / r_total
    temperature = t_amb
    faces = []
    for name, r_value in reversed(named):
        temperature += flux * r_value
        faces.append({
            "name": name,
            "R": round(r_value, 4),
            "temp_inner_face_C": round(temperature, 2),
        })
    return {
        "R_total": round(r_total, 4),
        "flux_W_m2": round(flux, 2),
        "faces_hot_to_cold": list(reversed(faces)),
    }


STACKS = {
    "case_c_with_castable": [
        ("castable", 20, 1.5),
        ("AES", 75, 0.08),
        ("calcium silicate", 50, 0.065),
        ("hardwood", 20, 0.16),
    ],
    "liner_75aes_50casi_20wood": [
        ("304 liner", 1.5, 15.0),
        ("AES", 75, 0.08),
        ("calcium silicate", 50, 0.065),
        ("hardwood", 20, 0.16),
    ],
    "liner_75aes_50casi_14wood": [
        ("304 liner", 1.5, 15.0),
        ("AES", 75, 0.08),
        ("calcium silicate", 50, 0.065),
        ("hardwood", 14, 0.16),
    ],
    "metal_skin_75aes": [
        ("304 liner", 1.5, 15.0),
        ("AES", 75, 0.08),
        ("304 skin", 1.2, 15.0),
    ],
    "metal_skin_40aes": [
        ("304 liner", 1.2, 15.0),
        ("AES", 40, 0.08),
        ("304 skin", 1.2, 15.0),
    ],
    "metal_skin_25aes": [
        ("304 liner", 1.2, 15.0),
        ("AES", 25, 0.08),
        ("304 skin", 1.0, 15.0),
    ],
}


def main() -> None:
    report = {name: solve(layers) for name, layers in STACKS.items()}
    out = Path(__file__).with_name("thermal.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name, result in report.items():
        outer = result["faces_hot_to_cold"][-2]
        print(f"{name}: flux {result['flux_W_m2']} W/m2, skin/wood inner {outer['temp_inner_face_C']} C ({outer['name']})")


if __name__ == "__main__":
    main()
