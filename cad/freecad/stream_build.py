"""FreeCAD solid for one long-vault prototype.

Placements come from the shop Vault plus HARDWARE. The mouth is a half-ellipse,
because a 430 mm rectangle does not fit inside the barrel end at 158 mm rise.
The sky plate width comes from plate_span(), the same limit as the mass model.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import FreeCAD as App
import Part

from cad.freecad.stream_physics import Vault, evaluate, plate_span, stack_thickness

ROOT = Path(__file__).resolve().parents[2]

HARDWARE = {
    "grip_len": 140.0,
    "grip_depth": 28.0,
    "grip_height": 36.0,
    "groove_r": 8.0,
    "post_d": 6.0,
    "post_inset": 28.0,
    "washer_d": 16.0,
    "washer_t": 3.0,
    "ferrule_press": 0.2,
    "ferrule_len": 8.0,
    "ferrule_wall": 2.0,
    "button_r": 5.0,
    "float_gap": 0.4,
    "seam": 0.3,
    "door_gap": 2.0,
    "door_border": 18.0,
    "door_fibre": 12.0,
    "door_skin": 0.8,
    "hood_depth": 36.0,
    "hood_t": 0.8,
    "hood_drop": 14.0,
    "box_w": 160.0,
    "box_h": 70.0,
    "box_d": 80.0,
    "box_gap": 0.8,
    "slot_w": 120.0,
    "slot_h": 22.0,
    "foot_d": 32.0,
    "foot_h": 10.0,
    "foot_inset": 50.0,
    "rack_d": 12.0,
    "rack_h": 6.0,
    "rack_dx": 40.0,
    "rack_dy": 80.0,
    "stand_d": 14.0,
    "stand_h": 8.0,
    "stand_dx": 160.0,
    "stand_dy": 220.0,
    "peel_standoff": 16.0,
    "pull_len": 90.0,
    "pull_h": 22.0,
    "pull_d": 16.0,
    "pull_gap": 12.0,
}


def _load(name: str) -> Vault:
    raw = json.loads((ROOT / "design" / "stream-1" / "optimizer.json").read_text(encoding="utf-8"))
    if name not in raw:
        raise KeyError(name)
    return Vault(**raw[name]["design"])


def _box(x0: float, y0: float, z0: float, dx: float, dy: float, dz: float) -> Part.Shape:
    return Part.makeBox(dx, dy, dz, App.Vector(x0, y0, z0))


def _half_tube(r_in: float, r_out: float, y0: float, y1: float, z_axis: float) -> Part.Shape:
    length = y1 - y0
    outer = Part.makeCylinder(r_out, length, App.Vector(0.0, y0, z_axis), App.Vector(0, 1, 0))
    inner = Part.makeCylinder(max(r_in, 0.1), length + 2.0, App.Vector(0.0, y0 - 1.0, z_axis), App.Vector(0, 1, 0))
    tube = outer if r_in <= 0.0 else outer.cut(inner)
    upper = _box(-r_out - 2.0, y0 - 1.0, z_axis, 2.0 * r_out + 4.0, length + 2.0, r_out + 4.0)
    return tube.common(upper)


def _half_disc(radius: float, thick: float, y0: float, z_axis: float) -> Part.Shape:
    disc = Part.makeCylinder(radius, thick, App.Vector(0.0, y0, z_axis), App.Vector(0, 1, 0))
    upper = _box(-radius - 2.0, y0 - 0.5, z_axis, 2.0 * radius + 4.0, thick + 1.0, radius + 4.0)
    return disc.common(upper)


def _arch_slab_x(width: float, rise: float, x0: float, depth: float, z_sill: float, y_c: float) -> Part.Shape:
    """Half-ellipse in the YZ plane, extruded along +X. Used for the parked door."""
    points = []
    steps = 28
    for index in range(steps + 1):
        theta = math.pi * index / steps
        y = y_c + (width / 2.0) * math.cos(theta)
        z = z_sill + rise * math.sin(theta)
        points.append(App.Vector(x0, y, z))
    points.append(App.Vector(x0, y_c - width / 2.0, z_sill - 1.0))
    points.append(App.Vector(x0, y_c + width / 2.0, z_sill - 1.0))
    points.append(points[0])
    face = Part.Face(Part.makePolygon(points))
    return face.extrude(App.Vector(depth, 0.0, 0.0))


def _arch_cutter(width: float, rise: float, y0: float, depth: float, z_sill: float) -> Part.Shape:
    """Half-ellipse mouth. The top corners of a rectangle would leave the barrel."""
    points = []
    steps = 28
    for index in range(steps + 1):
        theta = math.pi * index / steps
        x = (width / 2.0) * math.cos(theta)
        z = z_sill + rise * math.sin(theta)
        points.append(App.Vector(x, y0, z))
    points.append(App.Vector(-width / 2.0, y0, z_sill - 1.0))
    points.append(App.Vector(width / 2.0, y0, z_sill - 1.0))
    points.append(points[0])
    face = Part.Face(Part.makePolygon(points))
    return face.extrude(App.Vector(0.0, depth, 0.0))


def _overlap(a: Part.Shape, b: Part.Shape) -> bool:
    ab, bb = a.BoundBox, b.BoundBox
    pad = 0.2
    return not (
        ab.XMax < bb.XMin - pad or bb.XMax < ab.XMin - pad
        or ab.YMax < bb.YMin - pad or bb.YMax < ab.YMin - pad
        or ab.ZMax < bb.ZMin - pad or bb.ZMax < ab.ZMin - pad
    )


def _interfere(solids: list[tuple[str, Part.Shape]]) -> list[dict]:
    hits = []
    for i, (name_a, shape_a) in enumerate(solids):
        for name_b, shape_b in solids[i + 1:]:
            if not _overlap(shape_a, shape_b):
                continue
            common = shape_a.common(shape_b)
            volume = float(common.Volume) if common.Volume else 0.0
            if volume >= 1.0:
                hits.append({"a": name_a, "b": name_b, "mm3": round(volume, 2)})
    return hits


def _render_png_pyside2(fragment: str, title: str, subtitle: str, out_path: Path) -> None:
    """FreeCAD 1.0 ships PySide2. The Morning renderer asks for PySide6."""
    import os
    import re

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide2 import QtCore, QtGui, QtSvg

    from cad.freecad.build_variant import _path_bbox

    if QtGui.QGuiApplication.instance() is None:
        QtGui.QGuiApplication([])
    minx, miny, maxx, maxy = _path_bbox(fragment)
    width, height = 480, 360
    vw = max(maxx - minx, 1.0)
    vh = max(maxy - miny, 1.0)
    svg_doc = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="{minx:.2f} {miny:.2f} {vw:.2f} {vh:.2f}">{fragment}</svg>'
    )
    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg_doc.encode("utf-8")))
    image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
    image.fill(QtGui.QColor("#f7f4ee"))
    painter = QtGui.QPainter(image)
    margin_x, header_h, footer_h = 24.0, 42.0, 16.0
    avail_w = width - 2.0 * margin_x
    avail_h = height - header_h - footer_h
    scale = min(avail_w / vw, avail_h / vh)
    painter_rect = QtCore.QRectF(
        margin_x + (avail_w - vw * scale) / 2.0,
        header_h + (avail_h - vh * scale) / 2.0,
        vw * scale,
        vh * scale,
    )
    renderer.render(painter, painter_rect)
    painter.setPen(QtGui.QColor("#1c1a17"))
    painter.setFont(QtGui.QFont("DejaVu Serif", 10, QtGui.QFont.Bold))
    painter.drawText(QtCore.QPointF(14.0, 22.0), title)
    painter.setFont(QtGui.QFont("DejaVu Sans", 6))
    painter.setPen(QtGui.QColor("#5c5348"))
    short = subtitle if len(subtitle) < 90 else subtitle[:88] + "…"
    painter.drawText(QtCore.QPointF(14.0, 35.0), short)
    painter.end()
    image.save(str(out_path), "PNG")
    del re


def build(name: str = "stormcloud") -> dict:
    hw = HARDWARE
    design = _load(name)
    report = evaluate(design)
    gap = hw["float_gap"]
    deck = design.base_t + design.floor_fibre + design.button_h + gap + design.steel_t
    radius = design.radius
    length = design.length
    liner_r = radius + design.liner_t
    fibre_r = liner_r + design.fibre_t
    skin_r0 = fibre_r + design.air_gap
    skin_r = skin_r0 + design.skin_t
    seam = hw["seam"]
    plate_w, plate_l = plate_span(design)

    if design.dragon in App.listDocuments():
        App.closeDocument(design.dragon)
    doc = App.newDocument(design.dragon)
    made: list[tuple[str, Part.Shape, str]] = []

    def add(part: str, shape: Part.Shape, kind: str) -> Part.Shape:
        if shape.isNull() or not shape.isValid() or shape.Volume <= 1.0:
            raise RuntimeError(f"{part} is not a solid (vol={getattr(shape, 'Volume', None)})")
        obj = doc.addObject("Part::Feature", part)
        obj.Shape = shape
        made.append((part, shape, kind))
        return shape

    # Base tub. The barrel sits on the rim. Stand bosses are welded to the plate.
    plan_w = 2.0 * skin_r
    y_back = length + stack_thickness(design)
    y_front = -stack_thickness(design)
    plan_l = y_back - y_front
    base = _box(-plan_w / 2.0, y_front, 0.0, plan_w, plan_l, design.base_t)
    wall_h = deck - design.base_t - seam
    side_t = design.skin_t
    for sign in (-1.0, 1.0):
        x0 = sign * (plan_w / 2.0 - side_t) if sign > 0 else -plan_w / 2.0
        base = base.fuse(_box(x0, y_front, design.base_t, side_t, plan_l, wall_h))
    base = base.fuse(_box(-plan_w / 2.0, y_front, design.base_t, plan_w, side_t, wall_h))
    base = base.fuse(_box(-plan_w / 2.0, y_back - side_t, design.base_t, plan_w, side_t, wall_h))
    for sx in (-1.0, 1.0):
        for sy, yb in ((-1.0, y_front + hw["foot_inset"]), (1.0, y_back - hw["foot_inset"] - hw["stand_d"])):
            del sy
            boss = Part.makeCylinder(
                hw["stand_d"] / 2.0,
                hw["stand_h"],
                App.Vector(sx * hw["stand_dx"], yb, -hw["stand_h"]),
                App.Vector(0, 0, 1),
            )
            base = base.fuse(boss)
    add("base-tub", base, "al")

    add(
        "floor-fibre",
        _box(-design.steel_w / 2.0, design.landing, design.base_t, design.steel_w, design.steel_l, design.floor_fibre),
        "fibre",
    )

    button_z = design.base_t + design.floor_fibre
    xs = (-design.steel_w / 2.0 + 40.0, 0.0, design.steel_w / 2.0 - 40.0)
    ys = (design.landing + 40.0, design.landing + design.steel_l - 40.0)
    for index, (bx, by) in enumerate((x, y) for y in ys for x in xs):
        add(
            f"button-{index}",
            Part.makeCylinder(hw["button_r"], design.button_h, App.Vector(bx, by, button_z), App.Vector(0, 0, 1)),
            "ss",
        )

    add(
        "pizza-steel",
        _box(
            -design.steel_w / 2.0,
            design.landing,
            button_z + design.button_h + gap,
            design.steel_w,
            design.steel_l,
            design.steel_t,
        ),
        "mild",
    )

    if design.stop_gap > 0.0:
        # Fences overlap the plate in height and stay below the deck.
        # The gap is the growth allowance. They are not fasteners.
        stop_t, stop_h = 2.0, 3.0
        z_plate = button_z + design.button_h + gap
        y0 = design.landing
        y1 = design.landing + design.steel_l
        x0 = -design.steel_w / 2.0
        x1 = design.steel_w / 2.0
        g = design.stop_gap
        add("stop-front", _box(x0, y0 - g - stop_t, z_plate, design.steel_w, stop_t, stop_h), "ss")
        add("stop-rear", _box(x0, y1 + g, z_plate, design.steel_w, stop_t, stop_h), "ss")
        side_y = y0 + g + stop_t
        side_l = design.steel_l - 2.0 * (g + stop_t)
        add("stop-port", _box(x0 - g - stop_t, side_y, z_plate, stop_t, side_l, stop_h), "ss")
        add("stop-starboard", _box(x1 + g, side_y, z_plate, stop_t, side_l, stop_h), "ss")

    mouth = _arch_cutter(design.mouth_w, design.mouth_h, y_front - 5.0, -y_front + 8.0, deck)
    slot_z = deck + 0.62 * radius
    slot = _box(-hw["slot_w"] / 2.0, length - 2.0, slot_z, hw["slot_w"], stack_thickness(design) + 6.0, hw["slot_h"])

    liner = _half_tube(radius, liner_r, seam, length - seam, deck)
    liner_front = _half_disc(liner_r, design.liner_t, -design.liner_t, deck)
    liner_rear = _half_disc(liner_r, design.liner_t, length, deck)
    liner = liner.fuse(liner_front).fuse(liner_rear).cut(mouth).cut(slot)
    add("liner", liner, "ss")

    fibre = _half_tube(liner_r + seam, fibre_r, seam, length - seam, deck)
    fibre_front = _half_disc(fibre_r, design.fibre_t, -design.fibre_t, deck).cut(
        _half_disc(liner_r, design.fibre_t + 2.0, -design.fibre_t - 1.0, deck)
    )
    fibre_rear = _half_disc(fibre_r, design.fibre_t, length, deck).cut(
        _half_disc(liner_r, design.fibre_t + 2.0, length - 1.0, deck)
    )
    fibre = fibre.fuse(fibre_front).fuse(fibre_rear).cut(mouth).cut(slot)
    add("fibre-arch", fibre, "fibre")

    skin = _half_tube(skin_r0 + seam, skin_r, seam, length - seam, deck)
    skin_front = _half_disc(skin_r, design.skin_t, -(design.fibre_t + design.air_gap + design.skin_t), deck).cut(
        _half_disc(skin_r0, design.skin_t + 2.0, -(design.fibre_t + design.air_gap + design.skin_t) - 1.0, deck)
    )
    skin_rear = _half_disc(skin_r, design.skin_t, length + design.fibre_t + design.air_gap, deck).cut(
        _half_disc(skin_r0, design.skin_t + 2.0, length + design.fibre_t + design.air_gap - 1.0, deck)
    )
    skin = skin.fuse(skin_front).fuse(skin_rear).cut(mouth).cut(slot)
    # Rack bosses, clear of the skin by the seam, along the crown normal.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bx = sx * hw["rack_dx"]
            by = length / 2.0 + sy * hw["rack_dy"]
            local_r = math.sqrt(max(skin_r * skin_r - bx * bx, 1.0))
            boss = Part.makeCylinder(
                hw["rack_d"] / 2.0,
                hw["rack_h"],
                App.Vector(bx, by, deck + local_r + seam),
                App.Vector(0, 0, 1),
            )
            skin = skin.fuse(boss)
    add("skin", skin, "al")

    plate_z = deck + radius - design.plate_drop
    plate_y_forward = design.landing + 30.0
    if design.plate_pose == "in":
        plate_y = plate_y_forward
    elif design.plate_pose == "rear":
        # Broil pose. The plate slides back and leaves a front bay under the crown.
        plate_y = design.length - 20.0 - plate_l
    else:
        raise RuntimeError(f"unknown plate_pose {design.plate_pose}")
    add(
        "sky-plate",
        _box(-plate_w / 2.0, plate_y, plate_z, plate_w, plate_l, design.plate_t),
        "ss",
    )
    rail_y = plate_y_forward
    rail_l = (plate_y + plate_l) - rail_y
    rail_z = plate_z - gap - 8.0
    for sign, label in ((-1.0, "port"), (1.0, "starboard")):
        add(
            f"rail-{label}",
            _box(sign * (plate_w / 2.0 - 10.0) - 4.0, rail_y, rail_z, 8.0, rail_l, 8.0 - gap),
            "ss",
        )
    if design.plate_pose == "rear":
        # In the mouth, so the front view shows the grate. Still under the crown.
        rod_z = deck + design.mouth_h - 20.0
        y_a = design.landing + 16.0
        y_b = plate_y - 12.0
        half = math.sqrt(max(radius * radius - (rod_z - deck) ** 2, 0.0)) - 8.0
        for index, rod_x in enumerate((-120.0, -60.0, 0.0, 60.0, 120.0)):
            if abs(rod_x) + 2.0 > half or y_b - y_a < 40.0:
                raise RuntimeError(f"broil rod {index} does not fit")
            add(
                f"broil-rod-{index}",
                Part.makeCylinder(2.0, y_b - y_a, App.Vector(rod_x, y_a, rod_z), App.Vector(0, 1, 0)),
                "ss",
            )

    hood_z = deck + design.mouth_h - hw["hood_drop"]
    # Width limited by the arch at that height.
    hood_half = math.sqrt(max(radius * radius - (design.mouth_h - hw["hood_drop"]) ** 2, 0.0)) - 8.0
    hood_w = min(design.mouth_w - 20.0, 2.0 * hood_half)
    add(
        "throat-hood",
        _box(-hood_w / 2.0, 6.0, hood_z, hood_w, hw["hood_depth"], hw["hood_t"]),
        "ss",
    )

    door_rise = design.mouth_h + hw["door_border"]
    door_w = design.mouth_w + 2.0 * hw["door_border"]
    door_t = 2.0 * hw["door_skin"] + hw["door_fibre"]
    z_sill = deck - hw["door_border"]
    if design.door_pose == "open":
        # Pizza pose. Thickness along X, arch in YZ, wholly port of the skin.
        # A 90 degree swing about the front jamb would cut the shell, so the
        # door is placed, not rotated.
        x_in = -(skin_r + 3.0)
        y_c = y_front + 12.0 + door_w / 2.0
        door_cut = _arch_slab_x(door_w, door_rise, x_in - door_t - 1.0, door_t + 2.0, z_sill, y_c)
        door_blank = _box(
            x_in - door_t,
            y_c - door_w / 2.0 - 4.0,
            z_sill - 4.0,
            door_t,
            door_w + 8.0,
            door_rise + hw["door_border"] + 8.0,
        )
        add("door", door_blank.common(door_cut), "ss")
        add(
            "door-pull",
            _box(
                x_in - door_t - hw["pull_gap"] - hw["pull_d"],
                y_c - hw["pull_len"] / 2.0,
                deck + 40.0,
                hw["pull_d"],
                hw["pull_len"],
                hw["pull_h"],
            ),
            "jarrah",
        )
    elif design.door_pose == "shut":
        door_y = y_front - hw["door_gap"] - door_t
        # The sill occupies the threshold. The door stops above it.
        if design.sill_d > 0.0:
            z_sill = deck + 3.0
            door_rise = design.mouth_h + 12.0 - 3.0
        door_cut = _arch_cutter(door_w, door_rise, door_y - 1.0, door_t + 2.0, z_sill)
        door_blank = _box(
            -door_w / 2.0 - 4.0,
            door_y,
            z_sill - 4.0,
            door_w + 8.0,
            door_t,
            door_rise + hw["door_border"] + 8.0,
        )
        add("door", door_blank.common(door_cut), "ss")
        pull_y = door_y - hw["pull_gap"] - hw["pull_d"]
        add(
            "door-pull",
            _box(-hw["pull_len"] / 2.0, pull_y, deck + 40.0, hw["pull_len"], hw["pull_d"], hw["pull_h"]),
            "jarrah",
        )
    else:
        raise RuntimeError(f"unknown door_pose {design.door_pose}")

    box_y = length + design.fibre_t + design.air_gap + design.skin_t + hw["box_gap"]
    add(
        "burner-box",
        _box(-hw["box_w"] / 2.0, box_y, slot_z - 10.0, hw["box_w"], design.box_d, hw["box_h"]),
        "ss",
    )

    # Handles. Local +X is out along the skin normal. Port needs the extra half-turn
    # so that +X lands on (-cos phi, 0, +sin phi), not on the starboard normal.
    phi = design.handle_phi
    for sign, label, angle in ((-1.0, "port", phi - 180.0), (1.0, "starboard", -phi)):
        outward = App.Vector(sign * math.cos(math.radians(phi)), 0.0, math.sin(math.radians(phi)))
        origin = App.Vector(sign * skin_r * math.cos(math.radians(phi)), length / 2.0, deck + skin_r * math.sin(math.radians(phi)))
        seat = origin + outward * (design.standoff + hw["washer_t"] + seam)

        def place(shape: Part.Shape, _angle: float = angle, _seat: App.Vector = seat) -> Part.Shape:
            shape.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), _angle)
            shape.translate(_seat)
            return shape

        grip_box = _box(0.0, -hw["grip_len"] / 2.0, -hw["grip_height"] / 2.0, hw["grip_depth"], hw["grip_len"], hw["grip_height"])
        groove = Part.makeCylinder(
            hw["groove_r"],
            hw["grip_len"] + 4.0,
            App.Vector(hw["groove_r"], -hw["grip_len"] / 2.0 - 2.0, -hw["grip_height"] / 2.0),
            App.Vector(0, 1, 0),
        )
        add(f"grip-{label}", place(grip_box.cut(groove)), "jarrah")
        press = hw["ferrule_press"]
        wall = hw["ferrule_wall"]
        for end, y0 in (
            ("a", -hw["grip_len"] / 2.0),
            ("b", hw["grip_len"] / 2.0 - hw["ferrule_len"]),
        ):
            outer = _box(-wall, y0, -hw["grip_height"] / 2.0 - wall, hw["grip_depth"] + 2.0 * wall, hw["ferrule_len"], hw["grip_height"] + 2.0 * wall)
            inner = _box(press, y0 - 1.0, -hw["grip_height"] / 2.0 + press, hw["grip_depth"] - 2.0 * press, hw["ferrule_len"] + 2.0, hw["grip_height"] - 2.0 * press)
            add(f"ferrule-{label}-{end}", place(outer.cut(inner)), "gidgee")
        for end, yoff in (("a", -hw["grip_len"] / 2.0 + hw["post_inset"]), ("b", hw["grip_len"] / 2.0 - hw["post_inset"])):
            post = Part.makeCylinder(
                hw["post_d"] / 2.0,
                design.standoff - seam,
                App.Vector(-(design.standoff + hw["washer_t"]), yoff, 0.0),
                App.Vector(1, 0, 0),
            )
            add(f"post-{label}-{end}", place(post), "ss")
            washer = Part.makeCylinder(
                hw["washer_d"] / 2.0,
                hw["washer_t"] - seam,
                App.Vector(-hw["washer_t"], yoff, 0.0),
                App.Vector(1, 0, 0),
            )
            add(f"washer-{label}-{end}", place(washer), "ptfe")

    for sign, yf in ((-1.0, y_front + hw["foot_inset"]), (1.0, y_back - hw["foot_inset"])):
        for sx, xlabel in ((-1.0, "port"), (1.0, "starboard")):
            add(
                f"foot-{xlabel}-{'rear' if sign > 0 else 'front'}",
                Part.makeCylinder(hw["foot_d"] / 2.0, hw["foot_h"], App.Vector(sx * (plan_w / 2.0 - hw["foot_inset"]), yf, -hw["foot_h"]), App.Vector(0, 0, 1)),
                "rubber",
            )

    peel_z = design.base_t + wall_h / 2.0
    add(
        "peel-rest",
        _box(-design.mouth_w / 2.0, y_front - hw["peel_standoff"] - 14.0, peel_z, design.mouth_w, 14.0, 18.0),
        "jarrah",
    )

    if design.sill_d > 0.0 and design.sill_w > 0.0:
        # Forward of the front wall, 1 mm under the deck, not touching the free plate.
        add(
            "launch-sill",
            _box(
                -design.sill_w / 2.0,
                y_front - 2.0 - design.sill_d,
                deck - 1.0 - design.sill_t,
                design.sill_w,
                design.sill_d,
                design.sill_t,
            ),
            "ss",
        )

    doc.recompute()
    solids = [(part, shape) for part, shape, _kind in made]
    hits = _interfere(solids)
    press = [hit for hit in hits if "ferrule" in hit["a"] or "ferrule" in hit["b"]]
    stray = [hit for hit in hits if hit not in press]
    invalid = [part for part, shape, _kind in made if not shape.isValid()]

    out_dir = ROOT / "design" / "stream-1" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    compound = Part.makeCompound([shape for _n, shape, _k in made])
    bb = compound.BoundBox
    gate = {
        "dragon": design.dragon,
        "solids": len(made),
        "invalid": invalid,
        "bbox": {
            "x": round(bb.XLength, 1),
            "y": round(bb.YLength, 1),
            "z": round(bb.ZLength, 1),
        },
        "interference": stray,
        "press_fits": press,
        "analytical_ready_kg": round(report["ready_kg"], 3),
        "door_pose": design.door_pose,
        "box_d": design.box_d,
        "png": (
            {
                "front": "Mouth arch open. Door is the thin fin on the port cheek.",
                "side": "Long barrel. Parked door is the arch along the port side. Short cowl at the rear.",
                "top": "Long plan. Door is a strip outside the port skin. Not a circular plan.",
                "section": "Centreline. Sky plate is the horizontal line. The parked door is off this cut.",
            }
            if design.door_pose == "open"
            else {
                "front": "Shut arched door, shoulders and two grips, four feet. Not a round dome.",
                "side": "Long barrel. Burner box at the rear, peel rest and pull at the front.",
                "top": "Long plan, grips on both sides, four rack bosses. Not a circular plan.",
                "section": "Centreline. Sky plate is the horizontal line in the arch. Steel is the deck.",
            }
        ),
    }
    by_name = {part: shape for part, shape, _kind in made}
    if design.door_pose == "open":
        door_bb = by_name["door"].BoundBox
        skin_bb = by_name["skin"].BoundBox
        gate["door_xmax"] = round(door_bb.XMax, 1)
        gate["skin_xmin"] = round(skin_bb.XMin, 1)
        if door_bb.XMax > -(design.mouth_w / 2.0):
            stray.append({"a": "door", "b": "mouth", "mm3": -1})
        if door_bb.XMax >= skin_bb.XMin - 1.0:
            stray.append({"a": "door", "b": "skin-envelope", "mm3": -1})
    if design.sill_d > 0.0:
        sill_bb = by_name["launch-sill"].BoundBox
        steel_bb = by_name["pizza-steel"].BoundBox
        gate["sill_ymax"] = round(sill_bb.YMax, 1)
        gate["steel_ymin"] = round(steel_bb.YMin, 1)
        gate["sill_zmax"] = round(sill_bb.ZMax, 1)
        gate["side_gap_mm"] = round(report["side_gap_mm"], 2)
        if sill_bb.YMax >= steel_bb.YMin - 1.0:
            stray.append({"a": "launch-sill", "b": "pizza-steel", "mm3": -1})
        if sill_bb.ZMax > deck - 0.5:
            stray.append({"a": "launch-sill", "b": "deck", "mm3": -1})
        gate["png"]["front"] = "Mouth arch open. Launch sill is the lip under the opening."
        gate["png"]["side"] = "Long barrel. Sill projects under the mouth. Parked door on the port cheek."
    if design.plate_pose == "rear":
        plate_bb = by_name["sky-plate"].BoundBox
        gate["plate_ymin"] = round(plate_bb.YMin, 1)
        gate["broil_bay_mm"] = round(plate_bb.YMin - design.landing, 1)
        if plate_bb.YMax > design.length - 10.0:
            stray.append({"a": "sky-plate", "b": "rear-liner", "mm3": -1})
        gate["png"]["front"] = "Mouth open. Five grate bars in the arch. Door fin on the port cheek."
        gate["png"]["section"] = "Centreline. Plate is the rear half. Grate bars cross the front bay."
    if design.door_pose == "shut" and design.sill_d > 0.0:
        door_bb = by_name["door"].BoundBox
        sill_bb = by_name["launch-sill"].BoundBox
        gate["door_zmin"] = round(door_bb.ZMin, 1)
        gate["sill_zmax"] = round(sill_bb.ZMax, 1)
        if door_bb.ZMin <= sill_bb.ZMax:
            stray.append({"a": "door", "b": "launch-sill", "mm3": -1})
        gate["png"]["front"] = "Door shut above the sill. Bread pose. The arch is the door, not a dome."
        gate["png"]["side"] = "Long barrel. Sill and shut door at the mouth. Cowl at the rear."
        gate["png"]["section"] = "Centreline. Sky plate covers the deck. Door is shut at the mouth."
    (out_dir / "gate.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    print("GATE", json.dumps(gate))

    fcstd = out_dir / f"{name}.FCStd"
    doc.saveAs(str(fcstd))
    step = out_dir / f"{name}.step"
    export_objs = []
    for part, _shape, _kind in made:
        obj = doc.getObject(part) or doc.getObject(part.replace("-", "_"))
        if obj is None:
            raise RuntimeError(f"missing object {part}")
        export_objs.append(obj)
    Part.export(export_objs, str(step))

    section_box = _box(-1.0e4, -1.0e4, -1.0e4, 1.0e4, 2.0e4, 2.0e4)
    section = compound.cut(section_box)
    from cad.freecad.build_variant import _oriented_view, _render_png, _sheet
    import cad.freecad.build_variant as _draw

    def _render_png(fragment, title, subtitle, out_path):
        try:
            _draw._render_png(fragment, title, subtitle, out_path)
        except ModuleNotFoundError:
            _render_png_pyside2(fragment, title, subtitle, out_path)

    views = {
        "front": _oriented_view(compound, "front"),
        "side": _oriented_view(compound, "side"),
        "top": _oriented_view(compound, "top"),
        "section": _oriented_view(section, "section"),
    }
    title = f"{design.dragon} — long barrel"
    note = (
        f"{gate['bbox']['y']:.0f} long × {gate['bbox']['x']:.0f} wide × {gate['bbox']['z']:.0f} tall · "
        f"mouth arch {design.mouth_w:.0f}×{design.mouth_h:.0f} · steel {design.steel_w:.0f}×{design.steel_l:.0f}×{design.steel_t:.0f} · "
        f"ready {report['ready_kg']:.1f} kg"
    )
    (out_dir / "ga-arrangement.svg").write_text(
        _sheet(title, "Front, side, section, top", views, note, scale=0.35),
        encoding="utf-8",
    )
    for view_name, fragment in views.items():
        _render_png(fragment, f"{design.dragon} — {view_name}", note, out_dir / f"{view_name}.png")
        print("PNG", out_dir / f"{view_name}.png")
    if stray or invalid:
        raise RuntimeError(f"gate failed: stray={len(stray)} invalid={invalid}")
    print("BUILT", design.dragon)
    return gate


if __name__ == "__main__":
    build("stormcloud")
