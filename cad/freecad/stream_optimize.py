"""Minimise ready mass of one long-vault prototype.

Skin temperature, underside, grip, floor equilibrium, scorch time, thermal
camber, expansion gap, and broil flux are constraints. Cool-down is reported
against the Tread and is a constraint when the ratio can be held.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from cad.freecad.stream_physics import Vault, evaluate, vector_keys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "design" / "stream-1"

T_SKIN = 55.0
T_UNDER = 60.0
T_GRIP = 40.0
T_FLOOR = 315.0
SCORCH_S = 110.0
CAMBER_MM = 0.30
BROIL_MIN = 8000.0
# Open-mouth steel cool-down may run longer than the Tread. 1.35 is the aim.
COOL_RATIO = 1.35


def _from_vector(proto: Vault, x: np.ndarray) -> Vault:
    values = {key: float(val) for key, val in zip(vector_keys(), x)}
    return replace(proto, **values)


def _penalties(v: Vault) -> list[float]:
    result = evaluate(v)
    return [
        T_SKIN - result["skin_C"],
        T_UNDER - result["under_C"],
        T_GRIP - result["grip_C"],
        T_FLOOR - result["floor_C"],
        result["scorch_s"] - SCORCH_S,
        CAMBER_MM - result["camber_mm"],
        result["side_gap_mm"] - result["growth_mm"] - 1.0,
        result["broil_W_m2"] - BROIL_MIN,
        result["pizza_clearance"] - 25.0,
        0.64 - result["mouth_over_crown"],
        result["mouth_over_crown"] - 0.62,
        COOL_RATIO - result["cooldown_ratio"],
        result["body_height"] - 320.0,
        result["outer_length"] - 750.0,
    ]


def solve(proto: Vault, bounds: list[tuple[float, float]], x0: list[float]) -> dict:
    def objective(x: np.ndarray) -> float:
        return evaluate(_from_vector(proto, x))["ready_kg"]

    constraints = []
    sample = _penalties(proto)
    for index in range(len(sample)):
        constraints.append({
            "type": "ineq",
            "fun": lambda x, i=index: _penalties(_from_vector(proto, x))[i],
        })
    fit = minimize(
        objective,
        np.array(x0, dtype=float),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 60, "ftol": 1e-5, "disp": False},
    )
    design = _from_vector(proto, fit.x)
    result = evaluate(design)
    return {
        "success": bool(fit.success),
        "message": str(fit.message),
        "nit": int(fit.nit),
        "design": design,
        "result": result,
        "x": {key: round(float(val), 3) for key, val in zip(vector_keys(), fit.x)},
        "bounds": {key: list(bound) for key, bound in zip(vector_keys(), bounds)},
    }


def stormcloud_problem() -> dict:
    proto = Vault(name="stormcloud", dragon="Stormcloud")
    bounds = [
        (6.0, 10.0),    # steel
        (40.0, 80.0),   # fibre arch
        (18.0, 45.0),   # floor fibre
        (0.9, 1.6),     # aluminium skin
        (0.8, 2.0),     # sky plate
        (16.0, 32.0),   # standoff
        (6.0, 8.0),     # air gap stays laminar; 12 mm starts to convect
    ]
    x0 = [6.0, 70.0, 40.0, 1.0, 1.2, 20.0, 8.0]
    return solve(proto, bounds, x0)


def _snap(design: Vault) -> Vault:
    """Blanket is sold in 25 mm layers. Sheet is 1.0 mm. Plate is 1.2 mm."""
    fibre = float(math_ceil_25(design.fibre_t))
    floor = float(math_ceil_25(design.floor_fibre))
    return replace(
        design,
        fibre_t=fibre,
        floor_fibre=floor,
        skin_t=1.0,
        steel_t=6.0,
        plate_t=1.2,
        air_gap=8.0,
        standoff=round(design.standoff),
    )


def math_ceil_25(value: float) -> int:
    """Next 25 mm blanket. Within 1 mm above a module, stay on that module."""
    module = 25.0
    down = math.floor(value / module) * module
    if down >= module and value - down <= 1.0:
        return int(down)
    return int(math.ceil((value - 1e-6) / module) * module)


def _public(item: dict) -> dict:
    result = dict(item["result"])
    result["parts"] = {key: round(value, 3) for key, value in result["parts"].items()}
    for key, value in list(result.items()):
        if isinstance(value, float):
            result[key] = round(value, 3)
    return {
        "success": item["success"],
        "message": item["message"],
        "nit": item["nit"],
        "x": item["x"],
        "bounds": item["bounds"],
        "design": asdict(item["design"]),
        "result": result,
    }


def _line(name: str, item: dict) -> str:
    result = item["result"]
    return (
        f"{name} success={item['success']} ready={result['ready_kg']:.2f} kg "
        f"skin={result['skin_C']:.1f} C floor={result['floor_C']:.1f} C "
        f"plate={result['plate_C']:.1f} C under={result['under_C']:.1f} C "
        f"grip={result['grip_C']:.1f} C scorch={result['scorch_s']:.0f} s "
        f"camber={result['camber_mm']:.3f} mm cool={result['cooldown_ratio']:.2f}x "
        f"heat={result['heatup_min']:.1f} min "
        f"size={result['outer_length']:.0f}x{result['outer_width']:.0f}x{result['body_height']:.0f} "
        f"fibre={item['design']['fibre_t']:.1f} floor_fibre={item['design']['floor_fibre']:.1f}"
    )


def main() -> None:
    solved = stormcloud_problem()
    snapped = _snap(solved["design"])
    snapped_result = evaluate(snapped)
    penalties = _penalties(snapped)
    item = _public(solved)
    shop = _public({
        "success": all(value >= -0.2 for value in penalties),
        "message": "25 mm blanket modules, 1.0 mm skin, 8 mm air gap",
        "nit": solved["nit"],
        "design": snapped,
        "result": snapped_result,
        "x": {key: getattr(snapped, key) for key in vector_keys()},
        "bounds": solved["bounds"],
    })
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "optimizer.json"
    payload = {}
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    payload["stormcloud"] = shop
    payload["stormcloud-continuous"] = item
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(_line("continuous", item))
    print(_line("stormcloud", shop))


if __name__ == "__main__":
    main()
