"""CalculiX check of the Vermax wall and the floor stack.

The slab is the same homogeneous board the dome variants used, so a miss
here is a film or a unit error and not a design result. Geometry is metres.
"""

from __future__ import annotations

import json
from pathlib import Path

from cad.freecad import thermal_fea as fea
from cad.freecad.stacklib import Stack, evaluate

fea.CCX = Path("/usr/bin/ccx")
ROOT = Path(__file__).resolve().parents[2]


def _vermax() -> Stack:
    return Stack(
        dragon="Vermax",
        deck_t=4.0, ins_t=26.4, floor_ins=18.0, belly_ins=22.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=256.0,
        soffit_h=118.0, air_gap=12.4, standoff=55.0,
    )


def _solve(layers: list[tuple[str, float, float]], films: list[tuple[str, float, float]], work: Path) -> float:
    sizes = {}
    for name, thick, _k in layers:
        sizes[name] = max(thick / 4.0, 0.0004)
    mesh = fea._mesh_layers(layers, sizes)
    materials = {name: k for name, _t, k in layers}
    temps = fea._write_and_solve(mesh, materials, films, work)
    return fea._face_mean(mesh, temps, mesh["z_top"])


def _arrax() -> Stack:
    return Stack(
        dragon="Arrax",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=110.0, air_gap=16.0, standoff=54.0,
        launch_y=260.0, stepped=True,
    )


def _shrykos() -> Stack:
    return Stack(
        dragon="Shrykos",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=110.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True,
    )


def _morghul() -> Stack:
    return Stack(
        dragon="Morghul",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=110.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
    )


def _seasmoke() -> Stack:
    return Stack(
        dragon="Seasmoke",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=110.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True,
    )


def _caraxes() -> Stack:
    return Stack(
        dragon="Caraxes",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True,
    )


def _meleys() -> Stack:
    return Stack(
        dragon="Meleys",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True, bail=True,
    )


def _vhagar() -> Stack:
    return Stack(
        dragon="Vhagar",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True, bail=True,
        damper_shut=True, gasket=True, slide=True, rod_rail=True, wind=True,
    )


def _silverwing() -> Stack:
    return Stack(
        dragon="Silverwing",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True, bail=True,
        damper_shut=True, gasket=True, slide=True, rod_rail=True,
    )


def _vermithor() -> Stack:
    return Stack(
        dragon="Vermithor",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True, bail=True,
        damper_shut=True, gasket=True, slide=True,
    )


def _sheepstealer() -> Stack:
    return Stack(
        dragon="Sheepstealer",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True, bail=True,
        damper_shut=True, gasket=True,
    )


def _syrax() -> Stack:
    return Stack(
        dragon="Syrax",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=150.0, air_gap=16.0, standoff=54.0,
        launch_y=150.0, stepped=True, sloped=True, split=True,
        seated=True, grill=True, broiler=True, bail=True, damper_shut=True,
    )


def main() -> None:
    import os
    name = os.environ.get("DRAGON", "vermax")
    design = {
        "arrax": _arrax,
        "shrykos": _shrykos,
        "morghul": _morghul,
        "seasmoke": _seasmoke,
        "caraxes": _caraxes,
        "meleys": _meleys,
        "syrax": _syrax,
        "sheepstealer": _sheepstealer,
        "vermithor": _vermithor,
        "silverwing": _silverwing,
        "vhagar": _vhagar,
    }.get(name, _vermax)()
    report = evaluate(design)
    out = ROOT / "design" / "stream-2" / design.dragon.lower() / "thermal"
    slab = fea.slab_check(out / "slab")
    print("SLAB", json.dumps(slab))
    if abs(slab["error_C"]) > 2.0:
        raise SystemExit(f"slab check off by {slab['error_C']} C")
    wall_layers = [
        ("liner", design.liner_t / 1000.0, 45.0),
        ("board", design.ins_t / 1000.0, 0.030),
        ("air", design.air_gap / 1000.0, 0.032),
        ("skin", design.skin_t / 1000.0, 160.0),
    ]
    wall_outer = _solve(
        wall_layers,
        [("bottom", fea.T_GAS, 25.0), ("top", fea.T_AMB, 10.0)],
        out / "wall",
    )
    floor_layers = [
        ("deck", design.deck_t / 1000.0, 45.0),
        ("board", design.floor_ins / 1000.0, 0.030),
        ("pit", design.pit_t / 1000.0, 45.0),
        ("belly", design.belly_ins / 1000.0, 0.030),
        ("skin", 0.0008, 160.0),
    ]
    floor_outer = _solve(
        floor_layers,
        [("bottom", 300.0, 800.0), ("top", fea.T_AMB, 10.0)],
        out / "floor",
    )
    payload = {
        "dragon": design.dragon,
        "slab": slab,
        "wall_outer_C": round(wall_outer, 2),
        "wall_oned_C": report["skin_C"],
        "wall_error_C": round(wall_outer - report["skin_C"], 2),
        "under_outer_C": round(floor_outer, 2),
        "under_oned_C": report["under_C"],
        "under_error_C": round(floor_outer - report["under_C"], 2),
    }
    dest = ROOT / "design" / "stream-2" / design.dragon.lower() / "thermal.json"
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("WROTE", json.dumps(payload))
    if abs(payload["wall_error_C"]) > 2.0 or abs(payload["under_error_C"]) > 3.0:
        raise SystemExit("CalculiX disagrees with the resistance sum")


if __name__ == "__main__":
    main()
