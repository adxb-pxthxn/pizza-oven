"""Build one early Angas variant in FreeCAD and write FCStd, STEP, and drawings.

Run with freecadcmd, or through tools/freecad_mcp (the headless runner from
freecad-mcp). The cooking geometry is the Angas dome. Morning is the wood
body. Moondancer is the light shell.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import FreeCAD as App
import Part
import TechDraw

from cad.freecad.masslib import (
    APEX_H,
    CHAMBER_D,
    DENS,
    DOME_RISE,
    MOUTH_H,
    MOUTH_W,
    SKIRT_H,
    Design,
    ellipse_points,
    evaluate,
    offset_open,
)

ROOT = Path(__file__).resolve().parents[2]
HANDLE_ALPHA = math.radians(50.0)
STONE_SHIFT = 10.0


def _load(name: str) -> Design:
    payload = json.loads((ROOT / "design" / "variants" / "optimizer.json").read_text(encoding="utf-8"))
    raw = payload[name]["design"]
    # Insulation rounds up to 0.1 mm so a buildable figure stays inside the
    # temperature constraint the solver found. Gauges are already on a bound.
    raw["ins_t"] = math.ceil(raw["ins_t"] * 10.0 - 1e-9) / 10.0
    raw["floor_ins"] = math.ceil(raw["floor_ins"] * 10.0 - 1e-9) / 10.0
    for key in ("liner_t", "skin_t", "base_t", "pan_t", "stone_t", "stone_d", "band_t", "band_w", "standoff"):
        raw[key] = round(float(raw[key]), 2)
    return Design(**raw)


def _wire(points: list[tuple[float, float]]) -> Part.Wire:
    vectors = [App.Vector(r, 0.0, z) for r, z in points]
    edges = [Part.LineSegment(a, b).toShape() for a, b in zip(vectors, vectors[1:])]
    return Part.Wire(edges)


def _revolve(loop: list[tuple[float, float]]) -> Part.Shape:
    if loop[0] != loop[-1]:
        loop = list(loop) + [loop[0]]
    face = Part.Face(_wire(loop))
    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
    if solid.Solids:
        return solid.Solids[0]
    return solid


def _cyl(r_in: float, r_out: float, z0: float, z1: float) -> Part.Shape:
    outer = Part.makeCylinder(r_out, z1 - z0, App.Vector(0, 0, z0))
    inner = Part.makeCylinder(r_in, z1 - z0 + 2.0, App.Vector(0, 0, z0 - 1.0))
    return outer.cut(inner)


def _disc(radius: float, z0: float, thick: float) -> Part.Shape:
    return Part.makeCylinder(radius, thick, App.Vector(0, 0, z0))


def _mouth_cutter(hearth: float, outer_r: float, stack: float) -> Part.Shape:
    depth = stack + 24.0
    y = -(CHAMBER_D / 2.0 + outer_r) / 2.0
    return Part.makeBox(
        MOUTH_W,
        depth,
        MOUTH_H,
        App.Vector(-MOUTH_W / 2.0, y - depth / 2.0, hearth),
    )


def _dome(inner: list[tuple[float, float]], outer: list[tuple[float, float]]) -> Part.Shape:
    loop = list(reversed(inner)) + list(outer)
    return _revolve(loop)


def _add(doc, name: str, shape: Part.Shape, kind: str):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.Label = f"{name}|{kind}"
    return obj


def _handle_point(outer_profile: list[tuple[float, float]], spring: float) -> tuple[float, float]:
    target = spring + DOME_RISE * math.sin(HANDLE_ALPHA)
    return min(outer_profile, key=lambda point: abs(point[1] - target))


def build(name: str) -> dict:
    design = _load(name)
    report = evaluate(design)
    r = CHAMBER_D / 2.0
    stack = design.liner_t + design.ins_t + design.skin_t
    outer_r = r + stack
    hearth = design.base_t + design.floor_ins + design.pan_t + design.stone_t
    spring = hearth + SKIRT_H
    cutter = _mouth_cutter(hearth, outer_r, stack)

    doc = App.newDocument(design.dragon)
    made = []

    def add(part_name: str, shape: Part.Shape, kind: str, crown: bool = False):
        obj = _add(doc, part_name, shape, kind)
        made.append((obj, kind, crown))
        return obj

    add("base-pan", _disc(outer_r, 0.0, design.base_t), design.base)
    add("base-lip", _cyl(outer_r - design.base_t, outer_r, design.base_t, design.base_t + 12.0), design.base)
    add("floor-insulation", _disc(r + design.liner_t, design.base_t, design.floor_ins), "micro")
    add("stone-pan", _disc(r, design.base_t + design.floor_ins, design.pan_t), "ss")
    add(
        "floor-cordierite",
        Part.makeCylinder(design.stone_d / 2.0, design.stone_t, App.Vector(STONE_SHIFT, 0, hearth - design.stone_t)),
        "cordierite",
    )

    liner_skirt = _cyl(r, r + design.liner_t, hearth, spring).cut(cutter)
    ins_skirt = _cyl(r + design.liner_t, r + design.liner_t + design.ins_t, hearth, spring).cut(cutter)
    skin_r = r + design.liner_t + design.ins_t
    skin_skirt = _cyl(skin_r, outer_r, hearth, spring).cut(cutter)
    add("liner-skirt", liner_skirt, "ss")
    add("wall-insulation", ins_skirt, "micro")
    add("outer-skirt", skin_skirt, design.skin)

    inner = ellipse_points(r, DOME_RISE, spring)
    liner_o = offset_open(inner, design.liner_t)
    ins_o = offset_open(inner, design.liner_t + design.ins_t)
    skin_o = offset_open(inner, stack)
    add("liner-dome", _dome(inner, liner_o), "ss", crown=True)
    add("crown-insulation", _dome(liner_o, ins_o), "micro", crown=True)
    add("outer-dome", _dome(ins_o, skin_o), design.skin, crown=True)

    band_z = spring - design.band_w - 2.0
    add("cinch-band", _cyl(outer_r, outer_r + design.band_t, band_z, band_z + design.band_w), design.band)
    for angle, dowel_name in ((140.0, "dowel-a"), (220.0, "dowel-b")):
        pin = Part.makeCylinder(2.5, design.band_t + 8.0, App.Vector(outer_r - 2.0, 0, band_z + design.band_w / 2.0), App.Vector(1, 0, 0))
        pin.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)
        add(dowel_name, pin, "ss")

    frame_y = -(outer_r + 1.5)
    frame_z = hearth + MOUTH_H / 2.0
    outer_box = Part.makeBox(MOUTH_W + 24.0, 2.0, MOUTH_H + 16.0, App.Vector(-(MOUTH_W + 24.0) / 2.0, frame_y, frame_z - (MOUTH_H + 16.0) / 2.0))
    inner_box = Part.makeBox(MOUTH_W - 4.0, 6.0, MOUTH_H - 4.0, App.Vector(-(MOUTH_W - 4.0) / 2.0, frame_y - 2.0, frame_z - (MOUTH_H - 4.0) / 2.0))
    add("mouth-frame", outer_box.cut(inner_box), "ss")
    add(
        "peel-landing",
        Part.makeBox(MOUTH_W, 40.0, design.base_t, App.Vector(-MOUTH_W / 2.0, -(outer_r + 40.0), hearth - design.stone_t * 0.0 - design.base_t)),
        design.base,
    )

    # Burner envelope in the crescent on the port side. Mass is the allowance, not this box.
    add(
        "burner-envelope",
        Part.makeBox(36.0, 220.0, 24.0, App.Vector(-(r - 40.0), -80.0, hearth + 4.0)),
        "allowance",
    )

    hr, hz = _handle_point(skin_o, spring)
    for sign, side in ((-1.0, "port"), (1.0, "starboard")):
        surface_x = sign * hr
        grip_x = sign * (hr + design.standoff + 11.0)
        grip = Part.makeCylinder(11.0, 130.0, App.Vector(grip_x, -65.0, hz), App.Vector(0, 1, 0))
        add(f"handle-{side}", grip, "jarrah")
        for end, y in (("a", -40.0), ("b", 40.0)):
            post = Part.makeCylinder(3.0, design.standoff, App.Vector(surface_x, y, hz), App.Vector(sign, 0, 0))
            add(f"post-{side}-{end}", post, "ss")
            washer = Part.makeCylinder(8.0, 3.0, App.Vector(sign * (hr + design.standoff - 3.0), y, hz), App.Vector(sign, 0, 0))
            add(f"washer-{side}-{end}", washer, "ptfe")
        if design.ferrules:
            for end, y0 in (("a", -65.0), ("b", 57.0)):
                ferrule = Part.makeCylinder(13.0, 8.0, App.Vector(grip_x, y0, hz), App.Vector(0, 1, 0))
                ferrule = ferrule.cut(Part.makeCylinder(11.2, 10.0, App.Vector(grip_x, y0 - 1.0, hz), App.Vector(0, 1, 0)))
                add(f"ferrule-{side}-{end}", ferrule, "brass")

    foot_h = 12.0 if design.skin == "blackwood" else 8.0
    foot_r = 14.0 if design.skin == "blackwood" else 15.0
    foot_kind = "jarrah" if design.skin == "blackwood" else "rubber"
    for index, angle in enumerate((30.0, 150.0, 270.0)):
        rad = math.radians(angle)
        fx = math.cos(rad) * outer_r * 0.72
        fy = math.sin(rad) * outer_r * 0.72
        add(f"foot-{index}", Part.makeCylinder(foot_r, foot_h, App.Vector(fx, fy, -foot_h)), foot_kind)

    # Future top rack: four M5 bosses on a 120 mm pitch circle. The rack is not modelled.
    for index, angle in enumerate((45.0, 135.0, 225.0, 315.0)):
        rad = math.radians(angle)
        br = 60.0
        bz = min(skin_o, key=lambda point: abs(point[0] - br))[1]
        boss = Part.makeCylinder(6.0, 6.0, App.Vector(br * math.cos(rad), br * math.sin(rad), bz))
        add(f"rack-boss-{index}", boss, "ss", crown=True)

    # Future stand: four M6 bosses on a 220 mm square under the pan. The stand is not modelled.
    for index, (sx, sy) in enumerate(((110.0, 110.0), (110.0, -110.0), (-110.0, 110.0), (-110.0, -110.0))):
        add(f"stand-boss-{index}", Part.makeCylinder(7.0, 8.0, App.Vector(sx, sy, -8.0)), "ss")

    doc.recompute()

    out_dir = ROOT / "design" / "variants" / design.name
    out_dir.mkdir(parents=True, exist_ok=True)
    fcstd = out_dir / f"{design.name}.FCStd"
    doc.saveAs(str(fcstd))

    solids = []
    exploded = []
    masses = []
    for obj, kind, crown in made:
        if kind == "allowance":
            solids.append(obj.Shape)
            exploded.append(obj.Shape)
            continue
        density = DENS[kind]
        masses.append({"name": obj.Name, "kind": kind, "kg": round(obj.Shape.Volume * 1e-9 * density, 3), "crown": crown})
        solids.append(obj.Shape)
        exploded.append(obj.Shape.copy().translate(App.Vector(0, 0, 80.0)) if crown else obj.Shape)

    compound = Part.makeCompound(solids)
    exploded_shape = Part.makeCompound(exploded)
    step = out_dir / f"{design.name}.step"
    exploded_step = out_dir / f"{design.name}-exploded.step"
    compound.exportStep(str(step))
    exploded_shape.exportStep(str(exploded_step))

    half_box = Part.makeBox(outer_r + 80.0, outer_r * 2 + 200.0, report["body_height"] + 80.0, App.Vector(0, -(outer_r + 80.0), -40.0))
    section = compound.cut(half_box)
    _write_sheets(out_dir, design, report, compound, section, hr, hz)

    freecad_kg = round(sum(row["kg"] for row in masses), 3)
    summary = {
        "name": design.name,
        "dragon": design.dragon,
        "freecad_kg": freecad_kg,
        "analytical_kg": round(report["ready_kg"] - 1.85, 3),
        "ready_with_burner_kg": round(freecad_kg + 1.85, 3),
        "outer_diameter": round(report["outer_diameter"], 1),
        "body_height": round(report["body_height"], 1),
        "handle_r": round(hr, 1),
        "handle_z": round(hz, 1),
        "skin_C": round(report["wall_outer_C"], 2),
        "grip_C": round(report["grip_C"], 2),
        "parts": masses,
        "fcstd": str(fcstd),
        "step": str(step),
    }
    (out_dir / "freecad-mass.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("BUILT", design.dragon, "freecad_kg", freecad_kg, "analytical_without_burner", summary["analytical_kg"])
    return summary


def _svg_view(shape: Part.Shape, direction: App.Vector) -> str:
    raw = TechDraw.projectToSVG(shape, direction)
    # projectToSVG returns a full svg document. Keep the inner markup.
    start = raw.find("<g")
    end = raw.rfind("</svg>")
    if start == -1 or end == -1:
        return raw
    return raw[start:end]


def _write_sheets(out_dir: Path, design: Design, report: dict, compound, section, handle_r: float, handle_z: float) -> None:
    views = {
        "front": _svg_view(compound, App.Vector(0, 1, 0)),
        "side": _svg_view(section, App.Vector(1, 0, 0)),
        "top": _svg_view(compound, App.Vector(0, 0, -1)),
    }
    title = f"{design.dragon} — Angas dome, early prototype"
    note = (
        f"OD {report['outer_diameter']:.0f} mm · body {report['body_height']:.0f} mm · "
        f"mouth {MOUTH_W:.0f}×{MOUTH_H:.0f} · apex {APEX_H:.0f} · "
        f"stone Ø{design.stone_d:.0f}×{design.stone_t:.0f} · "
        f"handles on the dome shoulder r {handle_r:.0f} z {handle_z:.0f} · "
        f"rack 4×M5 PCD 120 · stand 4×M6 on a 220 square · "
        f"ready {report['ready_kg']:.2f} kg with the burner allowance"
    )
    sheet = _sheet(title, "General arrangement — front, section, top", views, note, scale=0.35)
    (out_dir / "ga-arrangement.svg").write_text(sheet, encoding="utf-8")
    print("SHEET", out_dir / "ga-arrangement.svg")


def _path_bbox(fragment: str) -> tuple[float, float, float, float]:
    import re
    xs: list[float] = []
    ys: list[float] = []
    for path in re.findall(r'd="([^"]*)"', fragment):
        nums = [float(value) for value in re.findall(r"[-+]?(?:\d+\.\d+|\d+)(?:[eE][-+]?\d+)?", path)]
        xs.extend(nums[0::2])
        ys.extend(nums[1::2])
    if not xs:
        return -1.0, -1.0, 1.0, 1.0
    # The projected group flips Y. The box below is in that flipped space.
    flipped = [-value for value in ys]
    pad = 8.0
    return min(xs) - pad, min(flipped) - pad, max(xs) + pad, max(flipped) + pad


def _view_svg(fragment: str, x: float, y: float, width: float, height: float) -> str:
    minx, miny, maxx, maxy = _path_bbox(fragment)
    return (
        f'<svg x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'viewBox="{minx:.2f} {miny:.2f} {maxx - minx:.2f} {maxy - miny:.2f}" preserveAspectRatio="xMidYMid meet">'
        f'{fragment}</svg>'
    )


def _sheet(title: str, sheet_name: str, views: dict[str, str], note: str, scale: float) -> str:
    del scale  # each view is fitted to its own window on the sheet
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
<rect width="420" height="297" fill="#f7f4ee"/>
<rect x="8" y="8" width="404" height="281" fill="none" stroke="#1c1a17" stroke-width="0.6"/>
<text x="14" y="18" font-family="Georgia, serif" font-size="5.2" fill="#1c1a17">{title}</text>
<text x="14" y="24" font-family="Georgia, serif" font-size="3.2" fill="#5c5348">{sheet_name}. Projected from the FreeCAD solid. Each view is fitted to its window.</text>
{_view_svg(views["front"], 14, 30, 124, 188)}
{_view_svg(views["side"], 146, 30, 124, 188)}
{_view_svg(views["top"], 278, 30, 124, 188)}
<text x="48" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Front, mouth</text>
<text x="168" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Section, dome and handles</text>
<text x="322" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Top</text>
<rect x="8" y="232" width="404" height="57" fill="#f7f4ee" stroke="#1c1a17" stroke-width="0.4"/>
<text x="14" y="248" font-family="Georgia, serif" font-size="3.0" fill="#1c1a17">{note}</text>
<text x="14" y="260" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Dimensions mm. Do not scale the drawing. Certified burner, valve, regulator and hose are bought. No jet is drawn.</text>
<text x="14" y="272" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Crown objects lift at the cinch. The top rack and the stand are interfaces only and are not in the mass.</text>
<text x="14" y="282" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Angas is the baseline. Morning and Moondancer are the early prototypes. Neither plan sits on the lowered tailgate.</text>
</svg>
'''


if __name__ == "__main__":
    build(os.environ.get("VARIANT", "morning"))
