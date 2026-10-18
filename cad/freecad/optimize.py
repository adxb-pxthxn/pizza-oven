"""Minimise ready mass with scipy. Skin temperature is a constraint.

Morning (wood body) and Moondancer (light shell) are solved separately.
Gauges cannot fall through the floor a rolled and TIG'd shell can actually
hold, and the stone stays at least 15 mm so the deck does not dump its
heat on the first pizza. The 20 kg cap is a constraint, not the objective.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from cad.freecad.masslib import Design, evaluate, vector_keys

# Metal surfaces a person might lean on stay at or under 55°C, five degrees
# inside the 60°C short-touch ceiling. Wood inner face stays at or under 75°C,
# five degrees inside the 80°C char line. The grip stays at or under 40°C.
T_METAL = 55.0
T_WOOD_INNER = 75.0
T_WOOD_OUTER = 50.0
T_UNDER = 60.0
T_GRIP = 40.0
MASS_CAP = 20.0


def _design_from(x: np.ndarray, proto: Design) -> Design:
    values = {key: float(val) for key, val in zip(vector_keys(), x)}
    data = asdict(proto)
    data.update(values)
    return Design(**data)


def _penalties(result: dict, design: Design) -> list[float]:
    """Constraints in the form expected by SLSQP: g(x) >= 0."""
    cons = [
        MASS_CAP - result["ready_kg"],
        T_UNDER - result["under_C"],
        T_GRIP - result["grip_C"],
        result["pizza_clearance"] - 19.5,  # 420 mm stone, 381 mm pizza
    ]
    if design.skin == "blackwood":
        cons.append(T_WOOD_INNER - result["wall_inner_face_C"])
        cons.append(T_WOOD_OUTER - result["wall_outer_C"])
    else:
        cons.append(T_METAL - result["wall_outer_C"])
    return cons


def solve(proto: Design, bounds: list[tuple[float, float]], x0: list[float]) -> dict:
    keys = vector_keys()

    def objective(x: np.ndarray) -> float:
        return evaluate(_design_from(x, proto))["ready_kg"]

    sample = _penalties(evaluate(proto), proto)
    constraints = []
    for index in range(len(sample)):
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: _penalties(evaluate(_design_from(x, proto)), _design_from(x, proto))[i],
        })

    fit = minimize(
        objective,
        np.array(x0, dtype=float),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 80, "ftol": 1e-6, "disp": False},
    )
    design = _design_from(fit.x, proto)
    result = evaluate(design)
    return {
        "success": bool(fit.success),
        "message": str(fit.message),
        "nit": int(fit.nit),
        "design": design,
        "result": result,
        "x": {key: round(float(val), 3) for key, val in zip(keys, fit.x)},
        "bounds": {key: bound for key, bound in zip(keys, bounds)},
    }


def morning_problem() -> dict:
    proto = Design(
        name="morning",
        dragon="Morning",
        skin="blackwood",
        base="ss",
        band="brass",
        liner_t=0.7,
        skin_t=8.0,
        base_t=0.8,
        pan_t=0.6,
        ins_t=36.0,
        floor_ins=28.0,
        stone_t=15.0,
        stone_d=420.0,
        band_t=1.5,
        band_w=16.0,
        standoff=22.0,
        ferrules=True,
    )
    bounds = [
        (0.6, 1.0),   # liner
        (8.0, 12.0),  # wood stave
        (0.8, 1.2),   # base
        (0.6, 1.0),   # pan
        (24.0, 55.0),
        (18.0, 45.0),
        (15.0, 20.0),
        (420.0, 430.0),
        (1.2, 2.0),   # brass thickness, a real hoop
        (14.0, 22.0),
        (16.0, 40.0),
    ]
    x0 = [0.6, 8.0, 0.8, 0.6, 40.0, 30.0, 15.0, 420.0, 1.2, 14.0, 20.0]
    return solve(proto, bounds, x0)


def moondancer_problem(base: str, skin: str) -> dict:
    proto = Design(
        name="moondancer",
        dragon="Moondancer",
        skin=skin,
        base=base,
        band="ss",
        liner_t=0.6,
        skin_t=0.8,
        base_t=0.9,
        pan_t=0.6,
        ins_t=34.0,
        floor_ins=26.0,
        stone_t=15.0,
        stone_d=420.0,
        band_t=0.8,
        band_w=12.0,
        standoff=20.0,
        ferrules=False,
    )
    skin_bounds = (0.8, 1.2) if skin == "al" else (0.6, 1.0)
    base_bounds = (0.9, 1.4) if base == "al" else (0.8, 1.2)
    bounds = [
        (0.6, 1.0),
        skin_bounds,
        base_bounds,
        (0.6, 1.0),
        (24.0, 55.0),
        (18.0, 45.0),
        (15.0, 20.0),
        (420.0, 430.0),
        (0.8, 1.6),
        (12.0, 18.0),
        (16.0, 40.0),
    ]
    x0 = [0.6, skin_bounds[0], base_bounds[0], 0.6, 36.0, 28.0, 15.0, 420.0, 0.8, 12.0, 18.0]
    return solve(proto, bounds, x0)


def choose_moondancer() -> dict:
    candidates = [
        moondancer_problem("al", "al"),
        moondancer_problem("ss", "ss"),
        moondancer_problem("ss", "al"),
    ]
    feasible = [item for item in candidates if item["success"] and item["result"]["ready_kg"] <= MASS_CAP + 1e-6]
    pool = feasible or candidates
    return min(pool, key=lambda item: item["result"]["ready_kg"])


def _public(item: dict) -> dict:
    design = asdict(item["design"])
    result = dict(item["result"])
    result["parts"] = {key: round(value, 3) for key, value in result["parts"].items()}
    for key in ("ready_kg", "stone_kg", "wall_outer_C", "wall_inner_face_C", "under_C", "grip_C",
                "outer_diameter", "body_height", "hearth_z", "spring_z", "outer_r", "stack",
                "pizza_clearance", "wall_flux"):
        if key in result:
            result[key] = round(float(result[key]), 3)
    return {
        "success": item["success"],
        "message": item["message"],
        "nit": item["nit"],
        "x": item["x"],
        "bounds": {key: list(value) for key, value in item["bounds"].items()},
        "design": design,
        "result": result,
    }


def main() -> None:
    morning = _public(morning_problem())
    moondancer = _public(choose_moondancer())
    payload = {"morning": morning, "moondancer": moondancer}
    out = Path(__file__).resolve().parents[2] / "design" / "variants" / "optimizer.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for name, item in payload.items():
        result = item["result"]
        print(
            f"{name}: success={item['success']} ready={result['ready_kg']:.2f} kg "
            f"skin={result['wall_outer_C']:.1f} C inner={result['wall_inner_face_C']:.1f} C "
            f"under={result['under_C']:.1f} C grip={result['grip_C']:.1f} C "
            f"OD={result['outer_diameter']:.0f} nit={item['nit']} {item['message']}"
        )


if __name__ == "__main__":
    main()
