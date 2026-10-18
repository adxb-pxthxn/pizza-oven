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

from cad.freecad.stream_physics import (
    BASE_MARK,
    Vault,
    evaluate,
    plate_span,
    skin_development,
    stack_thickness,
    write_skin_dxf,
)

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


def _cheek_strap(sign: float, skin_r: float, deck: float, y_mid: float, thick: float) -> Part.Shape:
    """Stainless strap on the outside of the skin, from the spring line past the grip.

    It stops 0.4 mm clear of the skin and continues down the base wall.
    The posts land on it, so the 1 mm skin is not the handle.
    """
    gap = 0.4
    outer = Part.makeCylinder(skin_r + gap + thick, 40.0, App.Vector(0.0, y_mid - 20.0, deck), App.Vector(0, 1, 0))
    inner = Part.makeCylinder(skin_r + gap, 44.0, App.Vector(0.0, y_mid - 22.0, deck), App.Vector(0, 1, 0))
    band = outer.cut(inner)
    band = band.common(_box(-(skin_r + thick + 2.0), y_mid - 22.0, deck - 1.0, 2.0 * (skin_r + thick + 2.0), 44.0, skin_r + thick + 4.0))
    # Keep the sector from the spring line up to 55 degrees on this cheek.
    wedge = _box(0.0, y_mid - 22.0, deck - 1.0, skin_r + thick + 4.0, 44.0, skin_r + thick + 4.0)
    wedge.rotate(App.Vector(0.0, y_mid, deck), App.Vector(0, 1, 0), 35.0)
    if sign < 0.0:
        wedge.rotate(App.Vector(0.0, y_mid, deck), App.Vector(0, 0, 1), 180.0)
    band = band.common(wedge)
    tab_x = sign * (skin_r + gap)
    tab = _box(tab_x if sign > 0.0 else tab_x - thick, y_mid - 20.0, 0.0, thick, 40.0, deck)
    return band.fuse(tab)


def _scribe_mark(doc, base: Part.Shape, y_mid: float, depth: float):
    """Cut the line into the underside. Readable when the oven is lifted."""
    import Draft

    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    obj = Draft.makeShapeString(String=BASE_MARK, FontFile=font, Size=6.0, Tracking=0.0)
    doc.recompute()
    shape = obj.Shape
    doc.removeObject(obj.Name)
    wires = [wire for wire in shape.Wires if wire.isClosed()]
    if not wires:
        raise RuntimeError("base mark did not close")
    solid = Part.Compound([Part.Face(wire) for wire in wires]).extrude(App.Vector(0.0, 0.0, depth))
    mirror = App.Matrix()
    mirror.scale(-1.0, 1.0, 1.0)
    solid = solid.transformGeometry(mirror)
    bb = solid.BoundBox
    solid.translate(App.Vector(-bb.Center.x, y_mid - bb.Center.y, 0.0))
    cut = base.cut(solid)
    if cut.isNull() or not cut.isValid() or cut.Volume > base.Volume - 0.05:
        raise RuntimeError("base mark did not cut the plate")
    edges = []
    for edge in solid.Edges:
        pts = edge.discretize(8)
        for start, end in zip(pts, pts[1:]):
            edges.append((start.x, start.y, end.x, end.y))
    return cut, edges


def _spin_about(shape: Part.Shape, origin: App.Vector, degrees: float) -> Part.Shape:
    spun = shape.copy()
    spun.rotate(origin, App.Vector(0.0, 0.0, 1.0), degrees)
    return spun


def _hinged_door(design, hw, deck: float, skin_r: float, y_front: float):
    """Mouth-sized door on two straps. Built shut, returned open.

    The pin is outboard of the skin. The straps bridge the port jamb to the
    pin, so the arch itself is not a wing. A +90 degree swing about the pin
    lays the door along the port side.
    """
    door_w = design.mouth_w + 2.0 * hw["door_border"]
    door_rise = design.mouth_h + hw["door_border"] - 3.0
    door_t = 2.0 * hw["door_skin"] + hw["door_fibre"]
    z0 = deck + 3.0
    # Far enough port that the pull, which was on the outer face, clears the skin when parked.
    ax = -(skin_r + door_t + hw["pull_gap"] + hw["pull_d"] + 3.2)
    ay = y_front - 6.0
    origin = App.Vector(ax, ay, 0.0)
    door_y = ay - door_t
    door_cut = _arch_cutter(door_w, door_rise, door_y - 1.0, door_t + 2.0, z0)
    door_blank = _box(
        -door_w / 2.0 - 4.0,
        door_y,
        z0 - 4.0,
        door_w + 8.0,
        door_t,
        door_rise + hw["door_border"] + 8.0,
    )
    door = door_blank.common(door_cut)
    bore_r = design.hinge / 2.0 + 0.4
    strap_z = (z0 + 6.0, z0 + door_rise - 22.0)
    for sz in strap_z:
        strap = _box(ax - 8.0, door_y, sz, (-door_w / 2.0 + 6.0) - (ax - 8.0), 2.0, 16.0)
        bore = Part.makeCylinder(bore_r, 20.0, App.Vector(ax, ay, sz - 2.0), App.Vector(0.0, 0.0, 1.0))
        door = door.fuse(strap.cut(bore))
    pull = _box(
        -hw["pull_len"] / 2.0,
        door_y - hw["pull_gap"] - hw["pull_d"],
        deck + 40.0,
        hw["pull_len"],
        hw["pull_d"],
        hw["pull_h"],
    )
    pin_z = z0 - 16.0
    pin_h = door_rise + 32.0
    pin = Part.makeCylinder(design.hinge / 2.0, pin_h, App.Vector(ax, ay, pin_z), App.Vector(0.0, 0.0, 1.0))
    # Stile inboard of the parked door, foot welded into the base wall, eyes on the pin.
    stile_x = ax + door_t + 2.0
    stile = _box(stile_x, ay + 6.0, z0 - 16.0, 10.0, (y_front + 6.0) - (ay + 6.0), door_rise + 28.0)
    if design.hinge_sole > 0.0:
        # Column down to the floor, plus a lap inside the front corner.
        foot = _box(stile_x, ay + 4.0, 0.0, (-(skin_r) + 4.0) - stile_x, (y_front + 8.0) - (ay + 4.0), z0 - 6.0)
        sole = _box(-(skin_r) + 1.0, y_front, 0.0, design.hinge_sole, 25.0, 8.0)
        post = stile.fuse(foot).fuse(sole)
    else:
        foot = _box(stile_x, ay + 4.0, z0 - 16.0, (-(skin_r) + 2.0) - stile_x, (y_front + 8.0) - (ay + 4.0), 10.0)
        post = stile.fuse(foot)
    for lz in (z0 - 16.0, z0 + door_rise - 4.0):
        eye = _box(ax - 10.0, ay - 10.0, lz, (stile_x + 10.0) - (ax - 10.0), 20.0, 12.0)
        bore = Part.makeCylinder(bore_r, 16.0, App.Vector(ax, ay, lz - 2.0), App.Vector(0.0, 0.0, 1.0))
        post = post.fuse(eye.cut(bore))
    shut = door.copy()
    return {
        "door": _spin_about(door, origin, 90.0),
        "pull": _spin_about(pull, origin, 90.0),
        "pin": pin,
        "lugs": [("hinge-post", post)],
        "shut": shut,
        "axis": (ax, ay),
    }


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


class _ReportTap:
    """Document observer. This FreeCAD build has no Console.AddObserver.

    Invalid shapes are recorded as they recompute. After the last recompute
    the build also rejects a part left Touched or Invalid.
    """

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def slotRecomputedObject(self, obj) -> None:
        shape = getattr(obj, "Shape", None)
        if shape is None or shape.isNull() or not shape.isValid():
            self.errors.append(f"{obj.Name} invalid")


def _measured(made: list[tuple[str, Part.Shape, str]]) -> dict:
    open_shells = []
    volume = 0.0
    for part, shape, _kind in made:
        volume += float(shape.Volume)
        closed = True
        if hasattr(shape, "isClosed"):
            try:
                closed = bool(shape.isClosed())
            except Exception:
                closed = False
        if not closed or not shape.isValid():
            open_shells.append(part)
    mx = my = mz = mass = 0.0
    for _part, shape, _kind in made:
        pieces = list(shape.Solids) if shape.Solids else [shape]
        for piece in pieces:
            part_volume = float(piece.Volume)
            centre = piece.CenterOfMass
            mx += centre.x * part_volume
            my += centre.y * part_volume
            mz += centre.z * part_volume
            mass += part_volume
    scale = mass if mass else 1.0
    return {
        "volume_mm3": round(volume, 1),
        "com_mm": [round(mx / scale, 1), round(my / scale, 1), round(mz / scale, 1)],
        "open_shells": open_shells,
    }


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
    tap = _ReportTap()
    App.addDocumentObserver(tap)
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
    mark_edges: list[tuple[float, float, float, float]] = []
    if design.base_mark > 0.0:
        base, mark_edges = _scribe_mark(doc, base, length / 2.0, design.base_mark)
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

    skin = _half_tube(skin_r0 + seam, skin_r, seam, length - seam, deck).cut(mouth).cut(slot)
    if design.fascia_gap > 0.0:
        # Half-rings over the fibre faces. They stop clear of the liner.
        inner = liner_r + design.fascia_gap
        y_face = -(design.fibre_t + design.air_gap + design.skin_t)
        y_rear = length + design.fibre_t + design.air_gap
        for part, y0 in (("fascia-front", y_face), ("fascia-rear", y_rear)):
            plate = _half_disc(skin_r - seam, design.skin_t, y0, deck).cut(
                _half_disc(inner, design.skin_t + 2.0, y0 - 1.0, deck)
            )
            add(part, plate, "al")
    else:
        skin_front = _half_disc(skin_r, design.skin_t, -(design.fibre_t + design.air_gap + design.skin_t), deck).cut(
            _half_disc(skin_r0, design.skin_t + 2.0, -(design.fibre_t + design.air_gap + design.skin_t) - 1.0, deck)
        )
        skin_rear = _half_disc(skin_r, design.skin_t, length + design.fibre_t + design.air_gap, deck).cut(
            _half_disc(skin_r0, design.skin_t + 2.0, length + design.fibre_t + design.air_gap - 1.0, deck)
        )
        skin = skin.fuse(skin_front).fuse(skin_rear)
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
    rail_l = (design.length - 20.0) - rail_y
    rail_z = plate_z - gap - 8.0
    for sign, label in ((-1.0, "port"), (1.0, "starboard")):
        add(
            f"rail-{label}",
            _box(sign * (plate_w / 2.0 - 10.0) - 4.0, rail_y, rail_z, 8.0, rail_l, 8.0 - gap),
            "ss",
        )
    bay_y = design.length - 20.0 - plate_l
    if bay_y - design.landing > 200.0:
        # Permanent grate in the bay the plate uncovers when it slides back.
        # The plate passes 15 mm above these rods when it is forward.
        rod_z = deck + design.mouth_h - 20.0
        y_a = design.landing + 16.0
        y_b = bay_y - 12.0
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
    if design.probe > 0.0:
        # Beside the arch, in the gas, clear of the liner face. Not through the fibre.
        gx = design.mouth_w / 2.0 + 14.0
        gy = 0.4
        gz = deck + 70.0
        outer = Part.makeCylinder(6.0, 8.0, App.Vector(gx, gy, gz), App.Vector(0, 1, 0))
        bore = Part.makeCylinder(design.probe / 2.0, 12.0, App.Vector(gx, gy - 2.0, gz), App.Vector(0, 1, 0))
        add("probe-gland", outer.cut(bore), "ss")

    door_rise = design.mouth_h + hw["door_border"]
    door_w = design.mouth_w + 2.0 * hw["door_border"]
    door_t = 2.0 * hw["door_skin"] + hw["door_fibre"]
    z_sill = deck - hw["door_border"]
    shut_door = None
    if design.door_pose == "open" and design.hinge > 0.0:
        hinged = _hinged_door(design, hw, deck, skin_r, y_front)
        add("door", hinged["door"], "ss")
        add("door-pull", hinged["pull"], "jarrah")
        add("hinge-pin", hinged["pin"], "ss")
        for lug_name, lug_shape in hinged["lugs"]:
            add(lug_name, lug_shape, "al")
        shut_door = hinged["shut"]
    elif design.door_pose == "open":
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
        if design.grip_hand > 0.0:
            # Finger hollow in the middle only. The ferrule ends stay square.
            span = hw["grip_len"] - 2.0 * hw["ferrule_len"] - 4.0
            y_hollow = -(span / 2.0)
            hollow = Part.makeCylinder(
                design.grip_hand,
                span,
                App.Vector(design.grip_hand, y_hollow, -hw["grip_height"] / 2.0),
                App.Vector(0, 1, 0),
            )
            # 3 mm arris so the top inner corner does not dig. The top stays full.
            chamfer = Part.Face(
                Part.makePolygon(
                    [
                        App.Vector(0.0, y_hollow, hw["grip_height"] / 2.0),
                        App.Vector(3.0, y_hollow, hw["grip_height"] / 2.0),
                        App.Vector(0.0, y_hollow, hw["grip_height"] / 2.0 - 3.0),
                        App.Vector(0.0, y_hollow, hw["grip_height"] / 2.0),
                    ]
                )
            ).extrude(App.Vector(0.0, span, 0.0))
            grip = grip_box.cut(hollow).cut(chamfer)
        else:
            groove = Part.makeCylinder(
                hw["groove_r"],
                hw["grip_len"] + 4.0,
                App.Vector(hw["groove_r"], -hw["grip_len"] / 2.0 - 2.0, -hw["grip_height"] / 2.0),
                App.Vector(0, 1, 0),
            )
            grip = grip_box.cut(groove)
        add(f"grip-{label}", place(grip), "jarrah")
        press = hw["ferrule_press"]
        wall = hw["ferrule_wall"]
        for end, y0 in (
            ("a", -hw["grip_len"] / 2.0),
            ("b", hw["grip_len"] / 2.0 - hw["ferrule_len"]),
        ):
            outer = _box(-wall, y0, -hw["grip_height"] / 2.0 - wall, hw["grip_depth"] + 2.0 * wall, hw["ferrule_len"], hw["grip_height"] + 2.0 * wall)
            inner = _box(press, y0 - 1.0, -hw["grip_height"] / 2.0 + press, hw["grip_depth"] - 2.0 * press, hw["ferrule_len"] + 2.0, hw["grip_height"] - 2.0 * press)
            add(f"ferrule-{label}-{end}", place(outer.cut(inner)), "gidgee")
        post_lift = (design.frame_strap + 0.4) if design.frame_strap > 0.0 else 0.0
        for end, yoff in (("a", -hw["grip_len"] / 2.0 + hw["post_inset"]), ("b", hw["grip_len"] / 2.0 - hw["post_inset"])):
            post = Part.makeCylinder(
                hw["post_d"] / 2.0,
                design.standoff - seam - post_lift,
                App.Vector(-(design.standoff + hw["washer_t"]) + post_lift, yoff, 0.0),
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
        sill = _box(
            -design.sill_w / 2.0,
            y_front - 2.0 - design.sill_d,
            deck - 1.0 - design.sill_t,
            design.sill_w,
            design.sill_d,
            design.sill_t,
        )
        if design.module > 0.0:
            # Scribed on the landing. The cooking steel is not marked.
            score_n = int(design.sill_d // design.module)
            for index in range(1, score_n):
                sill = sill.cut(
                    _box(
                        -design.sill_w / 2.0 - 1.0,
                        y_front - 2.0 - design.sill_d + index * design.module,
                        deck - 1.0 - 0.3,
                        design.sill_w + 2.0,
                        0.6,
                        0.5,
                    )
                )
        add("launch-sill", sill, "ss")

    if design.frame_strap > 0.0:
        for sign, label in ((-1.0, "port"), (1.0, "starboard")):
            add(
                f"strap-{label}",
                _cheek_strap(sign, skin_r, deck, length / 2.0, design.frame_strap),
                "ss",
            )

    swing_park = None
    if design.swing_arm > 0.0:
        # Working pose, in the broil bay. Steel only. The park pose is checked below.
        tray_z = deck + 90.0
        tray = _box(-80.0, 100.0, tray_z, 160.0, 120.0, 1.5)
        lug = _box(-200.0, 48.0, tray_z - 6.0, 16.0, 16.0, 14.0)
        arm = Part.makeCylinder(5.0, 140.0, App.Vector(-170.0, 72.0, tray_z + 14.0), App.Vector(0.72, 0.69, 0.0))
        add("swing-lug", lug, "ss")
        add("swing-arm", arm, "ss")
        add("swing-tray", tray, "ss")
        swing_park = {
            "xmax": round(-(skin_r + 16.0), 1),
            "ymin": 40.0,
            "ymax": 160.0,
        }

    doc.recompute()
    for obj in doc.Objects:
        state = set(obj.State)
        if "Invalid" in state or "Touched" in state:
            tap.errors.append(f"{obj.Name} left {sorted(state)}")
        shape = getattr(obj, "Shape", None)
        if shape is not None and (shape.isNull() or not shape.isValid()):
            tap.errors.append(f"{obj.Name} shape invalid")
    solids = [(part, shape) for part, shape, _kind in made]
    hits = _interfere(solids)
    press = [hit for hit in hits if "ferrule" in hit["a"] or "ferrule" in hit["b"]]
    weld = [
        hit
        for hit in hits
        if {hit["a"], hit["b"]} == {"hinge-post", "base-tub"}
    ]
    stray = [hit for hit in hits if hit not in press and hit not in weld]
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
        "welds": weld,
        "weld_mm3": round(sum(hit["mm3"] for hit in weld), 1),
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
    if swing_park is not None:
        gate["swing_park"] = swing_park
        tray_bb = by_name["swing-tray"].BoundBox
        rod_bb = by_name["broil-rod-2"].BoundBox
        gate["tray_zmax"] = round(tray_bb.ZMax, 1)
        gate["rod_zmin"] = round(rod_bb.ZMin, 1)
        if tray_bb.ZMax > rod_bb.ZMin - 5.0:
            stray.append({"a": "swing-tray", "b": "broil-rod", "mm3": -1})
        if swing_park["ymax"] > length / 2.0 - 70.0:
            stray.append({"a": "swing-park", "b": "grip", "mm3": -1})
    if design.door_pose == "open":
        door_bb = by_name["door"].BoundBox
        skin_bb = by_name["skin"].BoundBox
        gate["door_xmax"] = round(door_bb.XMax, 1)
        gate["skin_xmin"] = round(skin_bb.XMin, 1)
        if door_bb.XMax > -(design.mouth_w / 2.0):
            stray.append({"a": "door", "b": "mouth", "mm3": -1})
        if door_bb.XMax >= skin_bb.XMin - 1.0:
            stray.append({"a": "door", "b": "skin-envelope", "mm3": -1})
        if design.hinge > 0.0 and shut_door is not None:
            shut_bb = shut_door.BoundBox
            gate["shut_xmin"] = round(shut_bb.XMin, 1)
            gate["shut_xmax"] = round(shut_bb.XMax, 1)
            gate["shut_zmin"] = round(shut_bb.ZMin, 1)
            gate["hinge_d"] = design.hinge
            if shut_bb.XMin > -design.mouth_w / 2.0 or shut_bb.XMax < design.mouth_w / 2.0:
                stray.append({"a": "door-shut", "b": "mouth", "mm3": -1})
            sill_bb = by_name["launch-sill"].BoundBox
            gap_sill = shut_door.distToShape(by_name["launch-sill"])[0]
            gap_skin = shut_door.distToShape(by_name["skin"])[0]
            gate["shut_sill_mm"] = round(gap_sill, 2)
            gate["shut_skin_mm"] = round(gap_skin, 2)
            if gap_sill < 1.0 or gap_skin < 1.0:
                stray.append({"a": "door-shut", "b": "stack", "mm3": -1})
            if shut_bb.ZMin <= sill_bb.ZMax:
                stray.append({"a": "door-shut", "b": "sill-height", "mm3": -1})
            if swing_park is not None:
                swing_park["xmax"] = round(door_bb.XMin - 4.0, 1)
                gate["swing_park"] = swing_park
            if design.hinge_sole > 0.0 and gate["weld_mm3"] < 400.0:
                stray.append({"a": "hinge-post", "b": "weld-land", "mm3": -1})
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
    if design.fascia_gap > 0.0:
        flat = skin_development(design)
        front = by_name["fascia-front"]
        fibre_shape = by_name["fibre-arch"]
        liner_shape = by_name["liner"]
        gate["flat_arc_mm"] = round(flat["arc_mm"], 2)
        gate["fascia_inner_r"] = round(flat["inner_r"], 2)
        gate["fascia_fibre_mm"] = round(front.distToShape(fibre_shape)[0], 2)
        gate["fascia_liner_mm"] = round(front.distToShape(liner_shape)[0], 2)
        if gate["fascia_fibre_mm"] < 0.5 or gate["fascia_liner_mm"] < 0.5:
            stray.append({"a": "fascia-front", "b": "stack", "mm3": -1})
        if flat["inner_r"] <= design.mouth_w / 2.0:
            stray.append({"a": "fascia-front", "b": "mouth", "mm3": -1})
        dxf_path = out_dir / "skin.dxf"
        write_skin_dxf(dxf_path, flat, mark_edges or None)
        gate["dxf"] = dxf_path.name
        gate["png"]["front"] = "Mouth open. Aluminium half-rings close the fibre. Door fin on the port cheek."
    if design.probe > 0.0:
        gland = by_name["probe-gland"]
        gate["gland_liner_mm"] = round(gland.distToShape(by_name["liner"])[0], 2)
        gate["gland_fibre_mm"] = round(gland.distToShape(by_name["fibre-arch"])[0], 2)
        gate["probe_bore"] = design.probe
        if gate["gland_liner_mm"] < 0.3 or gate["gland_fibre_mm"] < 1.0:
            stray.append({"a": "probe-gland", "b": "stack", "mm3": -1})
    if design.base_mark > 0.0:
        gate["base_mark"] = BASE_MARK
        gate["mark_depth"] = design.base_mark
        if not mark_edges:
            stray.append({"a": "base-mark", "b": "base-tub", "mm3": -1})
    measured = _measured(made)
    gate["measured"] = measured
    gate["console_errors"] = tap.errors
    gate["console_warnings"] = len(tap.warnings)
    if measured["open_shells"]:
        stray.append({"a": "shell", "b": measured["open_shells"][0], "mm3": -1})
    if tap.errors:
        stray.append({"a": "console", "b": "report-view", "mm3": -1})
    steel_bb = by_name["pizza-steel"].BoundBox
    gate["steel_mm"] = [round(steel_bb.XLength, 2), round(steel_bb.YLength, 2), round(steel_bb.ZLength, 2)]
    if abs(steel_bb.ZLength - design.steel_t) > 0.2 or abs(steel_bb.XLength - design.steel_w) > 0.2:
        stray.append({"a": "pizza-steel", "b": "spec", "mm3": -1})
    if report["skin_C"] > 60.0 or report["under_C"] > 60.0 or report["grip_C"] > 40.0:
        stray.append({"a": "touch", "b": "limit", "mm3": -1})
    spec_path = out_dir / "spec.json"
    if spec_path.exists():
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        expected = spec.get("steel_mm")
        if expected and [round(value, 1) for value in gate["steel_mm"]] != [round(value, 1) for value in expected]:
            stray.append({"a": "pizza-steel", "b": "spec-file", "mm3": -1})
    try:
        App.removeDocumentObserver(tap)
    except Exception:
        pass
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
