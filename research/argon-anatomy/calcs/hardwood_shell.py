#!/usr/bin/env python3
"""1D wall check for a hardwood outer shell.

The cases are the ones drafted by Gemini 4 Argon in
research/argon-anatomy/argon/materials.md. This script recomputes them and
adds the ventilated-cavity case as an explicit resistance network, so the
report quotes code rather than the draft's rounded prose.

    python3 research/argon-anatomy/calcs/hardwood_shell.py
"""

from __future__ import annotations

import json
from pathlib import Path


T_GAS_C = 500.0
T_AMB_C = 20.0
H_IN = 25.0
H_EXT = 10.0
WOOD_LIMIT_C = 80.0


def resistance(thickness_mm: float, k: float) -> float:
    return (thickness_mm / 1000.0) / k


def solve(layers: list[tuple[str, float]], t_gas: float = T_GAS_C, t_amb: float = T_AMB_C) -> dict:
    """layers are (name, R) from the hot gas outward, including both films.

    Returns heat flux and the temperature on the inner face of every layer.
    """
    r_total = sum(r for _, r in layers)
    flux = (t_gas - t_amb) / r_total
    # Walk from the outside in, so the wood inner face is easy to read.
    temperature = t_amb
    faces = []
    for name, r_value in reversed(layers):
        temperature = temperature + flux * r_value
        faces.append({"name": name, "R": r_value, "temp_inner_face_C": round(temperature, 2)})
    return {
        "R_total": round(r_total, 4),
        "flux_W_m2": round(flux, 2),
        "faces_from_outside": faces,
    }


def wood_inner(result: dict) -> float:
    for face in result["faces_from_outside"]:
        if face["name"] == "hardwood":
            return face["temp_inner_face_C"]
    raise KeyError("hardwood")


def main() -> None:
    film_in = ("gas film", 1 / H_IN)
    film_out = ("outside air", 1 / H_EXT)
    castable = ("castable 20 mm", resistance(20, 1.5))
    wood = ("hardwood", resistance(20, 0.16))

    case_a = solve([
        film_in,
        castable,
        ("AES 50 mm", resistance(50, 0.08)),
        ("calcium silicate 25 mm", resistance(25, 0.065)),
        wood,
        film_out,
    ])
    case_b = solve([
        film_in,
        castable,
        ("AES 75 mm", resistance(75, 0.08)),
        ("calcium silicate 25 mm", resistance(25, 0.065)),
        wood,
        film_out,
    ])
    case_c = solve([
        film_in,
        castable,
        ("AES 75 mm", resistance(75, 0.08)),
        ("calcium silicate 50 mm", resistance(50, 0.065)),
        wood,
        film_out,
    ])

    # Ventilated cavity. The insulation stack ends on moving air at 30 C
    # with h = 8 W/m^2K. The stave is then a separate object: cavity air on
    # the inside face, ambient air on the outside face.
    cavity_air_c = 30.0
    h_gap = 8.0
    insulation = solve(
        [
            film_in,
            castable,
            ("AES 50 mm", resistance(50, 0.08)),
            ("calcium silicate 25 mm", resistance(25, 0.065)),
            ("cavity air film", 1 / h_gap),
        ],
        t_amb=cavity_air_c,
    )
    # Wood between cavity air and ambient. Steady state, both films.
    r_wood = resistance(20, 0.16)
    r_cavity_film = 1 / h_gap
    r_out = 1 / H_EXT
    flux_wood = (cavity_air_c - T_AMB_C) / (r_cavity_film + r_wood + r_out)
    wood_inner_c = T_AMB_C + flux_wood * (r_out + r_wood)
    wood_outer_c = T_AMB_C + flux_wood * r_out

    report = {
        "case_a_sealed_50aes_25calsil": case_a,
        "case_a_wood_inner_C": wood_inner(case_a),
        "case_a_passes_80C": wood_inner(case_a) <= WOOD_LIMIT_C,
        "case_b_sealed_75aes_25calsil": case_b,
        "case_b_wood_inner_C": wood_inner(case_b),
        "case_b_passes_80C": wood_inner(case_b) <= WOOD_LIMIT_C,
        "case_c_sealed_75aes_50calsil": case_c,
        "case_c_wood_inner_C": wood_inner(case_c),
        "case_c_passes_80C": wood_inner(case_c) <= WOOD_LIMIT_C,
        "ventilated": {
            "assumption": "Cavity air fixed at 30 C, h=8. This is only true if the slots actually move air.",
            "calcium_silicate_outer_C": insulation["faces_from_outside"][0]["temp_inner_face_C"],
            "insulation_flux_W_m2": insulation["flux_W_m2"],
            "wood_inner_C": round(wood_inner_c, 2),
            "wood_outer_C": round(wood_outer_c, 2),
            "wood_flux_W_m2": round(flux_wood, 2),
        },
    }
    out = Path(__file__).with_name("hardwood_shell.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "A_wood_C": report["case_a_wood_inner_C"],
        "A_pass": report["case_a_passes_80C"],
        "B_wood_C": report["case_b_wood_inner_C"],
        "B_pass": report["case_b_passes_80C"],
        "C_wood_C": report["case_c_wood_inner_C"],
        "C_pass": report["case_c_passes_80C"],
        "vent_wood_inner_C": report["ventilated"]["wood_inner_C"],
        "vent_calsil_outer_C": report["ventilated"]["calcium_silicate_outer_C"],
    }, indent=2))


if __name__ == "__main__":
    main()
