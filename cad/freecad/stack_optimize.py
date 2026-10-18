"""Minimise the ready mass of the modular stack.

Skin, underside, grip, bow, sag, heat-up, and the bread window are
constraints. The planform stays put: a 15 inch pizza has to launch.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from cad.freecad.stacklib import BURNER_KG, Stack, evaluate, part_mass_kg, parts, vector_keys

ROOT = Path(__file__).resolve().parents[2]
T_SKIN = 55.0
T_UNDER = 60.0
T_GRIP = 40.0
BOW_MM = 0.30
SAG_MM = 0.40


def _from(x: np.ndarray, proto: Stack) -> Stack:
    values = {key: float(val) for key, val in zip(vector_keys(), x)}
    return Stack(
        dragon=proto.dragon,
        launch_y=proto.launch_y,
        stepped=proto.stepped,
        sloped=proto.sloped,
        **values,
    )


def _penalties(result: dict, design: Stack) -> list[float]:
    mouth = result["mouth_h"]
    return [
        T_SKIN - result["skin_C"],
        T_UNDER - result["under_C"],
        T_GRIP - result["grip_pit_C"],
        T_GRIP - result["grip_hood_C"],
        BOW_MM - result["bow_mm"],
        SAG_MM - result["sag_mm"],
        result["side_gap_mm"] - (result["growth_mm"] + 2.0),
        mouth - (180.0 if design.stepped else 160.0),
        design.front_h - design.soffit_h - 80.0,
        design.soffit_h - 105.0,
        mouth - design.soffit_h - 25.0,
        25.0 - result["heatup_min"],
        result["bread_window_min"] - 25.0,
        0.5 - result["aabb_hits"],
    ]


def solve(proto: Stack, bounds: list[tuple[float, float]], x0: list[float]) -> dict:
    def objective(x: np.ndarray) -> float:
        # Unrounded. evaluate() rounds to grams, which flattens the gradient.
        design = _from(x, proto)
        return BURNER_KG + sum(part_mass_kg(part) for part in parts(design))

    constraints = []
    width = len(_penalties(evaluate(proto), proto))
    for index in range(width):
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: _penalties(evaluate(_from(x, proto)), _from(x, proto))[i],
        })
    fit = minimize(
        objective,
        np.asarray(x0, dtype=float),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 60, "ftol": 1e-9, "eps": 0.05, "disp": False},
    )
    design = _from(fit.x, proto)
    result = evaluate(design)
    return {
        "success": bool(fit.success),
        "message": str(fit.message),
        "ready_kg": result["ready_kg"],
        "design": design.to_json() if hasattr(design, "to_json") else asdict(design),
        "metrics": {key: value for key, value in result.items() if key != "parts"},
        "penalties": [round(value, 4) for value in _penalties(result, design)],
    }


def main() -> None:
    proto = Stack(
        dragon="Vermax",
        deck_t=5.0, ins_t=26.0, floor_ins=18.0, belly_ins=22.0,
        liner_t=0.7, skin_t=0.7, pit_t=1.1, front_h=256.0,
        soffit_h=118.0, air_gap=12.0, standoff=55.0,
    )
    bounds = [
        (4.0, 7.0),    # deck_t
        (18.0, 45.0),  # ins_t
        (12.0, 32.0),  # floor_ins
        (12.0, 36.0),  # belly_ins
        (0.6, 1.2),    # liner_t
        (0.6, 1.2),    # skin_t
        (1.0, 1.6),    # pit_t
        (254.0, 290.0),  # front_h
        (105.0, 140.0),  # soffit_h
        (6.0, 16.0),   # air_gap
        (40.0, 75.0),  # standoff
    ]
    x0 = [getattr(proto, key) for key in vector_keys()]
    solved = solve(proto, bounds, x0)
    out = ROOT / "design" / "stream-2" / "vermax" / "optimizer.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(solved, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"success": solved["success"], "message": solved["message"], "ready_kg": solved["ready_kg"], "modules": solved["metrics"]["modules_kg"], "skin_C": solved["metrics"]["skin_C"], "penalties": solved["penalties"]}, indent=2))


if __name__ == "__main__":
    main()
