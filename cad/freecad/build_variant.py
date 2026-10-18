"""Build one early Angas variant in FreeCAD and write FCStd, STEP, and drawings.

Run with freecadcmd, or through tools/freecad_mcp (the headless runner from
freecad-mcp). The cooking geometry is the Angas dome. Morning is the wood
body. Moondancer is the light shell.
"""

from __future__ import annotations

import json
import math
import os
import re
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

HARDWARE = {
    "handle_alpha": math.radians(50.0),
    "grip_d": 22.0,
    "grip_len": 130.0,
    "post_d": 6.0,
    "post_end_inset": 25.0,
    "post_seat_embed": 2.0,
    "washer_d": 16.0,
    "washer_t": 3.0,
    "ferrule_od": 26.0,
    "ferrule_len": 8.0,
    "ferrule_press": 0.2,
    "dowel_d": 5.0,
    "dowel_len": 14.0,
    "dowel_skin_depth": 2.0,
    "dowel_angles": (140.0, 220.0),
    "band_clearance": 2.0,
    "frame_t": 0.8,
    "frame_border": 12.0,
    "frame_inset": 2.0,
    "throat_t": 0.6,
    "landing_depth": 40.0,
    "lip_h": 12.0,
    "burner_clear": 4.0,
    "burner_h": 24.0,
    "burner_span_ratio": 220.0 / 420.0,
    "foot_pcd_ratio": 0.72,
    "foot_angles": (30.0, 150.0, 270.0),
    "foot_wood_d": 28.0,
    "foot_wood_h": 12.0,
    "foot_rubber_d": 30.0,
    "foot_rubber_h": 8.0,
    "rack_pcd": 120.0,
    "rack_boss_d": 12.0,
    "rack_boss_h": 6.0,
    "rack_angles": (45.0, 135.0, 225.0, 315.0),
    "stand_pitch": 220.0,
    "stand_boss_d": 14.0,
    "stand_boss_h": 8.0,
    "explode_lift": 80.0,
}

PARAMS = HARDWARE
HANDLE_ALPHA = PARAMS["handle_alpha"]
EXPLODE_LIFT = PARAMS["explode_lift"]


def _load(name: str, overrides: dict | None = None) -> Design:
    payload = json.loads((ROOT / "design" / "variants" / "optimizer.json").read_text(encoding="utf-8"))
    raw = dict(payload[name]["design"])
    # Insulation rounds up to 0.1 mm so a buildable figure stays inside the
    # temperature constraint the solver found. Gauges are already on a bound.
    raw["ins_t"] = math.ceil(raw["ins_t"] * 10.0 - 1e-9) / 10.0
    raw["floor_ins"] = math.ceil(raw["floor_ins"] * 10.0 - 1e-9) / 10.0
    for key in ("liner_t", "skin_t", "base_t", "pan_t", "stone_t", "stone_d", "band_t", "band_w", "standoff"):
        raw[key] = round(float(raw[key]), 2)
    if overrides:
        for key in ("standoff", "band_w", "band_t", "stone_d", "stone_t"):
            if key in overrides and overrides[key] is not None:
                raw[key] = float(overrides[key])
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


def _mouth_cutter(hearth: float, chamber_r: float, outer_r: float, stack: float) -> Part.Shape:
    y_inner = -math.sqrt(max(chamber_r * chamber_r - (MOUTH_W / 2.0) ** 2, 0.0))
    depth = (outer_r - (-y_inner)) + stack
    y_start = -(outer_r + 0.5 * stack)
    return Part.makeBox(
        MOUTH_W,
        depth,
        MOUTH_H,
        App.Vector(-MOUTH_W / 2.0, y_start, hearth),
    )


def _dome(inner: list[tuple[float, float]], outer: list[tuple[float, float]]) -> Part.Shape:
    pts_in = [App.Vector(r, 0.0, z) for r, z in reversed(inner)]
    pts_out = [App.Vector(r, 0.0, z) for r, z in outer]
    bs_in = Part.BSplineCurve()
    bs_in.interpolate(pts_in)
    bs_out = Part.BSplineCurve()
    bs_out.interpolate(pts_out)
    edges = [
        bs_in.toShape(),
        Part.LineSegment(pts_in[-1], pts_out[0]).toShape(),
        bs_out.toShape(),
        Part.LineSegment(pts_out[-1], pts_in[0]).toShape(),
    ]
    face = Part.Face(Part.Wire(edges))
    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
    if solid.Solids:
        return solid.Solids[0]
    return solid


def _dome_volume(outer: list[tuple[float, float]]) -> Part.Shape:
    pts = [App.Vector(r, 0.0, z) for r, z in outer]
    bs = Part.BSplineCurve()
    bs.interpolate(pts)
    p0, p1 = pts[0], pts[-1]
    c0, c1 = App.Vector(0.0, 0.0, p0.z), App.Vector(0.0, 0.0, p1.z)
    edges = [
        bs.toShape(),
        Part.LineSegment(p1, c1).toShape(),
        Part.LineSegment(c1, c0).toShape(),
        Part.LineSegment(c0, p0).toShape(),
    ]
    face = Part.Face(Part.Wire(edges))
    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
    if solid.Solids:
        return solid.Solids[0]
    return solid


def _add(doc, name: str, shape: Part.Shape, kind: str):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.Label = f"{name}|{kind}"
    return obj


def _profile_r_at_z(profile: list[tuple[float, float]], z: float) -> float:
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        if (z0 <= z <= z1) or (z1 <= z <= z0):
            if abs(z1 - z0) < 1e-9:
                return max(r0, r1)
            t = (z - z0) / (z1 - z0)
            return r0 + t * (r1 - r0)
    return min(profile, key=lambda point: abs(point[1] - z))[0]


def _profile_z_at_r(profile: list[tuple[float, float]], r: float) -> float:
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        if (r0 <= r <= r1) or (r1 <= r <= r0):
            if abs(r1 - r0) < 1e-9:
                return max(z0, z1)
            t = (r - r0) / (r1 - r0)
            return z0 + t * (z1 - z0)
    return min(profile, key=lambda point: abs(point[0] - r))[1]


def _handle_point(outer_profile: list[tuple[float, float]], spring: float, alpha: float = HANDLE_ALPHA) -> tuple[float, float]:
    hz = spring + DOME_RISE * math.sin(alpha)
    hr = _profile_r_at_z(outer_profile, hz)
    return hr, hz


def build(name: str, hw: dict | None = None) -> dict:
    cfg = dict(HARDWARE)
    if hw:
        cfg.update(hw)
    design = _load(name, cfg)
    report = evaluate(design)
    r = CHAMBER_D / 2.0
    stack = design.liner_t + design.ins_t + design.skin_t
    outer_r = r + stack
    hearth = design.base_t + design.floor_ins + design.pan_t + design.stone_t
    spring = hearth + SKIRT_H
    stone_r = design.stone_d / 2.0
    stone_shift = (r - stone_r) - design.stone_t
    cutter = _mouth_cutter(hearth, r, outer_r, stack)

    if design.dragon in App.listDocuments():
        App.closeDocument(design.dragon)
    doc = App.newDocument(design.dragon)
    made = []

    def add(part_name: str, shape: Part.Shape, kind: str, crown: bool = False):
        obj = _add(doc, part_name, shape, kind)
        made.append((obj, kind, crown))
        return obj

    add("base-pan", _disc(outer_r, 0.0, design.base_t), design.base)
    add(
        "base-lip",
        _cyl(outer_r - design.base_t, outer_r, design.base_t, design.base_t + cfg["lip_h"]),
        design.base,
    )
    add("floor-insulation", _disc(r + design.liner_t, design.base_t, design.floor_ins), "micro")
    add("stone-pan", _disc(r, design.base_t + design.floor_ins, design.pan_t), "ss")
    stone_shape = Part.makeCylinder(
        stone_r,
        design.stone_t,
        App.Vector(stone_shift, 0.0, hearth - design.stone_t),
    )
    add("floor-cordierite", stone_shape, "cordierite")

    liner_skirt = _cyl(r, r + design.liner_t, hearth, spring).cut(cutter)
    ins_skirt = _cyl(r + design.liner_t, r + design.liner_t + design.ins_t, hearth, spring).cut(cutter)
    skin_r = r + design.liner_t + design.ins_t
    skin_skirt = _cyl(skin_r, outer_r, hearth, spring).cut(cutter)

    band_z = spring - design.band_w - cfg["band_clearance"]
    dowel_r = cfg["dowel_d"] / 2.0
    dowel_len = cfg["dowel_len"]
    dowel_x0 = outer_r - min(cfg["dowel_skin_depth"], design.skin_t)
    dowel_z = band_z + design.band_w / 2.0
    skin_inner_cyl = Part.makeCylinder(skin_r, spring + DOME_RISE, App.Vector(0, 0, 0))
    dowel_shapes = []
    for angle, dowel_name in zip(cfg["dowel_angles"], ("dowel-a", "dowel-b")):
        pin = Part.makeCylinder(
            dowel_r,
            dowel_len,
            App.Vector(dowel_x0, 0.0, dowel_z),
            App.Vector(1, 0, 0),
        )
        pin.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)
        pin = pin.cut(skin_inner_cyl)
        dowel_shapes.append((dowel_name, pin))

    add("liner-skirt", liner_skirt, "ss")
    add("wall-insulation", ins_skirt, "micro")
    add("outer-skirt", skin_skirt, design.skin)

    inner = ellipse_points(r, DOME_RISE, spring)
    liner_o = offset_open(inner, design.liner_t)
    ins_o = offset_open(inner, design.liner_t + design.ins_t)
    skin_o = offset_open(inner, stack)
    liner_dome_shape = _dome(inner, liner_o)
    ins_dome_shape = _dome(liner_o, ins_o)
    outer_dome_shape = _dome(ins_o, skin_o)
    dome_solid_envelope = _dome_volume(skin_o)

    cinch_band_shape = _cyl(outer_r, outer_r + design.band_t, band_z, band_z + design.band_w)
    add("cinch-band", cinch_band_shape, design.band)
    for dowel_name, pin in dowel_shapes:
        add(dowel_name, pin, "ss")

    outer_cyl = Part.makeCylinder(outer_r, spring + DOME_RISE + stack, App.Vector(0, 0, 0))
    landing_depth = cfg["landing_depth"]
    y_mouth_corner = -math.sqrt(max(outer_r * outer_r - (MOUTH_W / 2.0) ** 2, 0.0))
    landing_box = Part.makeBox(
        MOUTH_W,
        (outer_r + landing_depth) + y_mouth_corner,
        design.base_t,
        App.Vector(-MOUTH_W / 2.0, -(outer_r + landing_depth), hearth - design.base_t),
    )
    landing_shape = landing_box.cut(outer_cyl)

    frame_t = cfg["frame_t"]
    frame_border = cfg["frame_border"]
    frame_inset = cfg["frame_inset"]
    throat_t = cfg["throat_t"]
    frame_w = MOUTH_W + 2.0 * frame_border
    frame_h = MOUTH_H + 2.0 * frame_border
    frame_z0 = hearth - frame_border
    frame_cyl = _cyl(outer_r, outer_r + frame_t, frame_z0, frame_z0 + frame_h)
    frame_outer_box = Part.makeBox(
        frame_w,
        outer_r,
        frame_h,
        App.Vector(-frame_w / 2.0, -(outer_r + frame_t + frame_border), frame_z0),
    )
    frame_inner_box = Part.makeBox(
        MOUTH_W - 2.0 * frame_inset,
        outer_r,
        MOUTH_H - 2.0 * frame_inset,
        App.Vector(-(MOUTH_W - 2.0 * frame_inset) / 2.0, -(outer_r + frame_t + frame_border), hearth + frame_inset),
    )
    flange_shape = frame_cyl.common(frame_outer_box).cut(frame_inner_box).cut(landing_shape).cut(cinch_band_shape)

    throat_outer = Part.makeBox(MOUTH_W, outer_r, MOUTH_H, App.Vector(-MOUTH_W / 2.0, -outer_r, hearth))
    throat_inner = Part.makeBox(
        MOUTH_W - 2.0 * throat_t,
        outer_r + 2.0 * frame_border,
        MOUTH_H - 2.0 * throat_t,
        App.Vector(-(MOUTH_W - 2.0 * throat_t) / 2.0, -outer_r - frame_border, hearth + throat_t),
    )
    throat_sleeve = throat_outer.cut(throat_inner).common(_cyl(r, outer_r, hearth, spring))
    frame_shape = flange_shape.fuse(throat_sleeve)
    add("mouth-frame", frame_shape, "ss")
    add("peel-landing", landing_shape, design.base)

    # Burner envelope in the crescent on the port side. Mass is the allowance, not this solid.
    burner_clear = cfg["burner_clear"]
    burner_span = design.stone_d * cfg["burner_span_ratio"]
    burner_outer = Part.makeCylinder(r - burner_clear, cfg["burner_h"], App.Vector(0, 0, hearth + burner_clear))
    burner_inner = Part.makeCylinder(
        stone_r + burner_clear,
        cfg["burner_h"] + 2.0 * burner_clear,
        App.Vector(stone_shift, 0, hearth),
    )
    burner_clip = Part.makeBox(
        r,
        burner_span,
        cfg["burner_h"],
        App.Vector(-r, -burner_span / 2.0, hearth + burner_clear),
    )
    add("burner-envelope", burner_outer.cut(burner_inner).common(burner_clip), "allowance")

    hr, hz = _handle_point(skin_o, spring, cfg["handle_alpha"])
    grip_r = cfg["grip_d"] / 2.0
    grip_len = cfg["grip_len"]
    post_r = cfg["post_d"] / 2.0
    post_y = max(0.5 * grip_len - cfg["post_end_inset"], post_r)
    washer_r = cfg["washer_d"] / 2.0
    washer_t = cfg["washer_t"]
    ferrule_or = cfg["ferrule_od"] / 2.0
    ferrule_ir = grip_r - cfg["ferrule_press"]
    ferrule_len = cfg["ferrule_len"]
    surface_x_at_post = math.sqrt(max(hr * hr - post_y * post_y, 0.0))
    embed = cfg["post_seat_embed"]

    handle_items = []
    for sign, side in ((-1.0, "port"), (1.0, "starboard")):
        grip_x = sign * (hr + design.standoff + grip_r)
        grip = Part.makeCylinder(grip_r, grip_len, App.Vector(grip_x, -grip_len / 2.0, hz), App.Vector(0, 1, 0))
        handle_items.append((f"handle-{side}", grip, "jarrah", False))
        for end, y_pos in (("a", -post_y), ("b", post_y)):
            post_start_x = sign * (surface_x_at_post - embed)
            post_end_x = sign * (hr + design.standoff - washer_t)
            post_len = abs(post_end_x - post_start_x)
            post_raw = Part.makeCylinder(
                post_r,
                post_len,
                App.Vector(post_start_x, y_pos, hz),
                App.Vector(sign, 0, 0),
            )
            post = post_raw.cut(dome_solid_envelope)
            handle_items.append((f"post-{side}-{end}", post, "ss", False))
            washer = Part.makeCylinder(
                washer_r,
                washer_t,
                App.Vector(post_end_x, y_pos, hz),
                App.Vector(sign, 0, 0),
            )
            handle_items.append((f"washer-{side}-{end}", washer, "ptfe", False))
        if design.ferrules:
            for end, y0 in (("a", -grip_len / 2.0), ("b", grip_len / 2.0 - ferrule_len)):
                ferrule_outer = Part.makeCylinder(
                    ferrule_or,
                    ferrule_len,
                    App.Vector(grip_x, y0, hz),
                    App.Vector(0, 1, 0),
                )
                ferrule_bore = Part.makeCylinder(
                    ferrule_ir,
                    ferrule_len + 2.0,
                    App.Vector(grip_x, y0 - 1.0, hz),
                    App.Vector(0, 1, 0),
                )
                handle_items.append((f"ferrule-{side}-{end}", ferrule_outer.cut(ferrule_bore), "brass", False))

    # Future top rack: four M5 bosses on a 120 mm pitch circle. The rack is not modelled.
    rack_r = cfg["rack_pcd"] / 2.0
    rack_boss_r = cfg["rack_boss_d"] / 2.0
    rack_boss_h = cfg["rack_boss_h"]
    bz_seat = _profile_z_at_r(skin_o, rack_r + rack_boss_r) - 1.0
    bz_top = _profile_z_at_r(skin_o, rack_r) + rack_boss_h
    rack_items = []
    for index, angle in enumerate(cfg["rack_angles"]):
        rad = math.radians(angle)
        boss_raw = Part.makeCylinder(
            rack_boss_r,
            bz_top - bz_seat,
            App.Vector(rack_r * math.cos(rad), rack_r * math.sin(rad), bz_seat),
        )
        boss = boss_raw.cut(dome_solid_envelope)
        rack_items.append((f"rack-boss-{index}", boss, "ss", True))

    add("liner-dome", liner_dome_shape, "ss", crown=True)
    add("crown-insulation", ins_dome_shape, "micro", crown=True)
    add("outer-dome", outer_dome_shape, design.skin, crown=True)
    for part_name, shape, kind, crown in handle_items:
        add(part_name, shape, kind, crown=crown)

    foot_h = cfg["foot_wood_h"] if design.skin == "blackwood" else cfg["foot_rubber_h"]
    foot_r = (cfg["foot_wood_d"] if design.skin == "blackwood" else cfg["foot_rubber_d"]) / 2.0
    foot_kind = "jarrah" if design.skin == "blackwood" else "rubber"
    foot_pcd_r = outer_r * cfg["foot_pcd_ratio"]
    for index, angle in enumerate(cfg["foot_angles"]):
        rad = math.radians(angle)
        fx = math.cos(rad) * foot_pcd_r
        fy = math.sin(rad) * foot_pcd_r
        add(f"foot-{index}", Part.makeCylinder(foot_r, foot_h, App.Vector(fx, fy, -foot_h)), foot_kind)

    for part_name, shape, kind, crown in rack_items:
        add(part_name, shape, kind, crown=crown)

    # Future stand: four M6 bosses on a 220 mm square under the pan. The stand is not modelled.
    stand_half = cfg["stand_pitch"] / 2.0
    stand_boss_r = cfg["stand_boss_d"] / 2.0
    stand_boss_h = cfg["stand_boss_h"]
    stand_coords = (
        (stand_half, stand_half),
        (stand_half, -stand_half),
        (-stand_half, stand_half),
        (-stand_half, -stand_half),
    )
    for index, (sx, sy) in enumerate(stand_coords):
        add(
            f"stand-boss-{index}",
            Part.makeCylinder(stand_boss_r, stand_boss_h, App.Vector(sx, sy, -stand_boss_h)),
            "ss",
        )

    doc.recompute()

    out_dir = ROOT / "design" / "variants" / design.name
    out_dir.mkdir(parents=True, exist_ok=True)
    fcstd = out_dir / f"{design.name}.FCStd"
    doc.saveAs(str(fcstd))

    solids = []
    exploded = []
    masses = []
    lift = cfg["explode_lift"]
    for obj, kind, crown in made:
        if kind == "allowance":
            continue
        density = DENS[kind]
        masses.append({
            "name": obj.Name,
            "kind": kind,
            "kg": round(obj.Shape.Volume * 1e-9 * density, 3),
            "crown": crown,
        })
        solids.append(obj.Shape)
        exploded.append(obj.Shape.copy().translate(App.Vector(0, 0, lift)) if crown else obj.Shape)

    compound = Part.makeCompound(solids)
    exploded_shape = Part.makeCompound(exploded)
    step = out_dir / f"{design.name}.step"
    exploded_step = out_dir / f"{design.name}-exploded.step"
    compound.exportStep(str(step))
    exploded_shape.exportStep(str(exploded_step))

    cut_extent = outer_r + design.standoff + cfg["grip_d"] + cfg["landing_depth"] + 40.0
    half_box = Part.makeBox(
        cut_extent,
        2.0 * cut_extent,
        report["body_height"] + 100.0,
        App.Vector(-cut_extent, -cut_extent, -50.0),
    )
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


def _oriented_view(shape: Part.Shape, view_kind: str) -> str:
    copy = shape.copy()
    if view_kind == "front":
        copy.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90.0)
    elif view_kind in ("side", "section"):
        copy.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90.0)
        copy.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90.0)
    elif view_kind == "top":
        pass
    raw = TechDraw.projectToSVG(copy, App.Vector(0, 0, 1))
    start = raw.find("<g")
    end = raw.rfind("</svg>")
    if start != -1 and end != -1:
        raw = raw[start:end]
    return re.sub(r'stroke-width="[^"]*"', 'stroke-width="0.7"', raw)


def _render_png(fragment: str, title: str, subtitle: str, out_path: Path, width: int = 480, height: int = 360) -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6 import QtCore, QtGui, QtSvg

    if QtGui.QGuiApplication.instance() is None:
        _qt_app = QtGui.QGuiApplication([])
    minx, miny, maxx, maxy = _path_bbox(fragment)
    vw = max(maxx - minx, 1.0)
    vh = max(maxy - miny, 1.0)
    svg_doc = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="{minx:.2f} {miny:.2f} {vw:.2f} {vh:.2f}">'
        f"{fragment}</svg>"
    )
    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg_doc.encode("utf-8")))
    image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
    image.fill(QtGui.QColor("#f7f4ee"))
    painter = QtGui.QPainter(image)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

    margin_x = 24.0
    header_h = 42.0
    footer_h = 16.0
    avail_w = width - 2.0 * margin_x
    avail_h = height - header_h - footer_h
    scale = min(avail_w / vw, avail_h / vh)
    draw_w = vw * scale
    draw_h = vh * scale
    target_rect = QtCore.QRectF(
        margin_x + (avail_w - draw_w) / 2.0,
        header_h + (avail_h - draw_h) / 2.0,
        draw_w,
        draw_h,
    )
    renderer.render(painter, target_rect)

    pen = QtGui.QPen(QtGui.QColor("#1c1a17"))
    pen.setWidthF(1.0)
    painter.setPen(pen)
    painter.drawRect(QtCore.QRectF(6.0, 6.0, width - 12.0, height - 12.0))

    title_font = QtGui.QFont("DejaVu Serif", 10, QtGui.QFont.Bold)
    painter.setFont(title_font)
    painter.drawText(QtCore.QPointF(14.0, 22.0), title)

    sub_font = QtGui.QFont("DejaVu Sans", 6)
    painter.setFont(sub_font)
    painter.setPen(QtGui.QColor("#5c5348"))
    painter.drawText(QtCore.QPointF(14.0, 35.0), subtitle)

    painter.end()
    palette = [
        QtGui.qRgb(28, 26, 23),
        QtGui.qRgb(64, 59, 53),
        QtGui.qRgb(100, 93, 83),
        QtGui.qRgb(136, 128, 115),
        QtGui.qRgb(172, 164, 150),
        QtGui.qRgb(208, 200, 188),
        QtGui.qRgb(230, 224, 215),
        QtGui.qRgb(247, 244, 238),
    ]
    indexed = image.convertToFormat(QtGui.QImage.Format_Indexed8, palette)
    indexed.save(str(out_path), "PNG", 0)



def _write_sheets(out_dir: Path, design: Design, report: dict, compound, section, handle_r: float, handle_z: float) -> None:
    views = {
        "front": _oriented_view(compound, "front"),
        "side": _oriented_view(compound, "side"),
        "top": _oriented_view(compound, "top"),
        "section": _oriented_view(section, "section"),
    }
    title = f"{design.dragon} — Angas dome, early prototype"
    note = (
        f"OD {report['outer_diameter']:.0f} mm · body {report['body_height']:.0f} mm · "
        f"mouth {MOUTH_W:.0f}×{MOUTH_H:.0f} · apex {APEX_H:.0f} · "
        f"stone Ø{design.stone_d:.0f}×{design.stone_t:.0f} · "
        f"handles on the dome shoulder r {handle_r:.0f} z {handle_z:.0f} · "
        f"rack 4×M5 PCD {HARDWARE['rack_pcd']:.0f} · stand 4×M6 on a {HARDWARE['stand_pitch']:.0f} square · "
        f"ready {report['ready_kg']:.2f} kg with the burner allowance"
    )
    sheet = _sheet(title, "General arrangement — front, side, section, top", views, note, scale=0.35)
    (out_dir / "ga-arrangement.svg").write_text(sheet, encoding="utf-8")
    print("SHEET", out_dir / "ga-arrangement.svg")

    subtitles = {
        "front": f"Front elevation (looking into mouth {MOUTH_W:.0f}×{MOUTH_H:.0f} mm along +Y, handles symmetric at r={handle_r:.1f}, z={handle_z:.1f} mm)",
        "side": f"Port side elevation (looking along hearth from -X, mouth and peel landing on right)",
        "top": f"Top plan (looking down -Z onto Ø{report['outer_diameter']:.1f} mm shell, 4×M5 rack bosses on PCD {HARDWARE['rack_pcd']:.0f} mm)",
        "section": f"Centreline section X=0 (floor stack, Ø{design.stone_d:.0f}×{design.stone_t:.0f} mm stone, Ø{CHAMBER_D:.0f} mm dome, {MOUTH_H:.0f} mm mouth)",
    }
    for view_name, fragment in views.items():
        png_path = out_dir / f"{view_name}.png"
        _render_png(fragment, f"{design.dragon} — {view_name.capitalize()} View", subtitles[view_name], png_path)
        print("PNG", png_path)


def _path_bbox(fragment: str) -> tuple[float, float, float, float]:
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
        f"{fragment}</svg>"
    )


def _sheet(title: str, sheet_name: str, views: dict[str, str], note: str, scale: float) -> str:
    del scale  # each view is fitted to its own window on the sheet
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
<rect width="420" height="297" fill="#f7f4ee"/>
<rect x="8" y="8" width="404" height="281" fill="none" stroke="#1c1a17" stroke-width="0.6"/>
<text x="14" y="18" font-family="Georgia, serif" font-size="5.2" fill="#1c1a17">{title}</text>
<text x="14" y="24" font-family="Georgia, serif" font-size="3.2" fill="#5c5348">{sheet_name}. Projected from the FreeCAD solid. Each view is fitted to its window.</text>
{_view_svg(views["front"], 14, 30, 96, 188)}
{_view_svg(views["side"], 114, 30, 96, 188)}
{_view_svg(views["section"], 214, 30, 96, 188)}
{_view_svg(views["top"], 314, 30, 96, 188)}
<text x="42" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Front, mouth</text>
<text x="142" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Side, port</text>
<text x="236" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Section, centreline</text>
<text x="352" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Top, plan</text>
<rect x="8" y="232" width="404" height="57" fill="#f7f4ee" stroke="#1c1a17" stroke-width="0.4"/>
<text x="14" y="248" font-family="Georgia, serif" font-size="3.0" fill="#1c1a17">{note}</text>
<text x="14" y="260" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Dimensions mm. Do not scale the drawing. Certified burner, valve, regulator and hose are bought. No jet is drawn.</text>
<text x="14" y="272" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Crown objects lift at the cinch. The top rack and the stand are interfaces only and are not in the mass.</text>
<text x="14" y="282" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Angas is the baseline. Morning and Moondancer are the early prototypes. Neither plan sits on the lowered tailgate.</text>
</svg>
'''


if __name__ == "__main__":
    build(os.environ.get("VARIANT", "morning"))