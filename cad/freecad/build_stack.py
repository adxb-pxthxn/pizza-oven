"""Build the Vermax modular stack in FreeCAD and write FCStd, STEP, gates, and drawings.

The managed agent returned this builder under the name Stormcloud. That name
belongs to the other stream, so the dragon and the output paths are Vermax.
The section box removes the port half: the side camera looks from -X, and a
cut of +X would hide the centreline behind the port skin.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import FreeCAD as App
import Part
import TechDraw

import cad.freecad.stacklib as _stacklib
from cad.freecad.stacklib import (
    BURNER_KG,
    DECK_L,
    DECK_W,
    DENS,
    GUTTER_L,
    MOUTH_W,
    active_press_fits,
    SOFFIT_Y1,
    Stack,
    evaluate,
    soffit_y0,
    parts,
)

ROOT = Path(_stacklib.__file__).resolve().parents[2]

VERMAX = Stack(
    dragon="Vermax",
    deck_t=4.0,
    ins_t=26.4,
    floor_ins=18.0,
    belly_ins=22.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=256.0,
    soffit_h=118.0,
    air_gap=12.4,
    standoff=55.0,
)

ARRAX = Stack(
    dragon="Arrax",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=110.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=260.0,
    stepped=True,
)

SHRYKOS = Stack(
    dragon="Shrykos",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=110.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
)

MORGHUL = Stack(
    dragon="Morghul",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=110.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
)

SEASMOKE = Stack(
    dragon="Seasmoke",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=110.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
)

CARAXES = Stack(
    dragon="Caraxes",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
)

MELEYS = Stack(
    dragon="Meleys",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
)

SYRAX = Stack(
    dragon="Syrax",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
)

SHEEPSTEALER = Stack(
    dragon="Sheepstealer",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
)

VERMITHOR = Stack(
    dragon="Vermithor",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
)

SILVERWING = Stack(
    dragon="Silverwing",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
    rod_rail=True,
)

VHAGAR = Stack(
    dragon="Vhagar",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
    rod_rail=True,
    wind=True,
)

BALERION = Stack(
    dragon="Balerion",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
    rod_rail=True,
    wind=True,
    panel=True,
)

MERAXES = Stack(
    dragon="Meraxes",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
    rod_rail=True,
    wind=True,
    panel=True,
    door_air=True,
)

DREAMFYRE = Stack(
    dragon="Dreamfyre",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
    rod_rail=True,
    wind=True,
    panel=True,
    door_air=True,
    door_hinge=True,
)

CANNIBAL = Stack(
    dragon="Cannibal",
    deck_t=4.0,
    ins_t=22.0,
    floor_ins=12.0,
    belly_ins=12.0,
    liner_t=0.6,
    skin_t=0.6,
    pit_t=1.0,
    front_h=294.0,
    soffit_h=150.0,
    air_gap=16.0,
    standoff=54.0,
    launch_y=150.0,
    stepped=True,
    sloped=True,
    split=True,
    seated=True,
    grill=True,
    broiler=True,
    bail=True,
    damper_shut=True,
    gasket=True,
    slide=True,
    rod_rail=True,
    wind=True,
    panel=True,
    door_air=True,
    door_hinge=True,
    door_tie=True,
)

DRAGONS = {
    "vermax": VERMAX,
    "arrax": ARRAX,
    "shrykos": SHRYKOS,
    "morghul": MORGHUL,
    "seasmoke": SEASMOKE,
    "caraxes": CARAXES,
    "meleys": MELEYS,
    "syrax": SYRAX,
    "sheepstealer": SHEEPSTEALER,
    "vermithor": VERMITHOR,
    "silverwing": SILVERWING,
    "vhagar": VHAGAR,
    "balerion": BALERION,
    "meraxes": MERAXES,
    "dreamfyre": DREAMFYRE,
    "cannibal": CANNIBAL,
}

FORBIDDEN_CONSOLE_TOKENS = ("Error", "Recompute failed", "subshape")


class _ConsoleObserver:
    """Capture FreeCAD console messages and document recompute diagnostics."""

    _CONSOLE_HOOKS = (
        "PrintMessage",
        "PrintLog",
        "PrintWarning",
        "PrintDeveloperWarning",
        "PrintUserWarning",
        "PrintTranslatedUserWarning",
        "PrintError",
        "PrintDeveloperError",
        "PrintUserError",
        "PrintTranslatedUserError",
        "PrintCritical",
        "PrintNotification",
        "PrintTranslatedNotification",
    )

    def __init__(self) -> None:
        self.messages: list[str] = []
        self._originals: dict[str, object] = {}
        self._doc_observed = False

    def _record(self, prefix: str, *args: object) -> None:
        text = " ".join(str(arg) for arg in args if arg is not None).strip()
        if text:
            self.messages.append(f"{prefix}: {text}" if prefix else text)

    def Error(self, msg: str) -> None:
        self._record("Error", msg)

    def Warning(self, msg: str) -> None:
        self._record("Warning", msg)

    def Message(self, msg: str) -> None:
        self._record("Message", msg)

    def Log(self, msg: str) -> None:
        self._record("Log", msg)

    def Critical(self, msg: str) -> None:
        self._record("Critical", msg)

    def receive(self, msg: str) -> None:
        self._record("", msg)

    def sendLog(self, notifier: str, msg: str, *rest: object) -> None:
        del rest
        self._record(notifier, msg)

    SendLog = sendLog

    def slotRecomputedObject(self, obj: object) -> None:
        state = [str(item) for item in getattr(obj, "State", ())]
        status = str(obj.getStatusString()) if hasattr(obj, "getStatusString") else ""
        label = str(getattr(obj, "Label", getattr(obj, "Name", "object")))
        if "Invalid" in state or "Error" in status or "Recompute failed" in status or "subshape" in status:
            self._record("Error", f"{label} state={state} status={status}")

    def slotRecomputedDocument(self, doc: object) -> None:
        for obj in getattr(doc, "Objects", ()):
            self.slotRecomputedObject(obj)

    def install(self) -> None:
        console = getattr(App, "Console", None)
        if console is not None:
            for hook_name in self._CONSOLE_HOOKS:
                orig = getattr(console, hook_name, None)
                if callable(orig) and hook_name not in self._originals:
                    self._originals[hook_name] = orig
                    prefix = "Error" if "Error" in hook_name else ""

                    def _make_wrapper(fn, tag: str):
                        def _wrapped(*args):
                            self._record(tag, *args)
                            return fn(*args)

                        return _wrapped

                    try:
                        setattr(console, hook_name, _make_wrapper(orig, prefix))
                    except Exception:
                        pass
            for attach_name in ("attachObserver", "addObserver"):
                attach_fn = getattr(console, attach_name, None)
                if callable(attach_fn):
                    try:
                        attach_fn(self)
                    except Exception:
                        pass
        if hasattr(App, "addDocumentObserver") and not self._doc_observed:
            try:
                App.addDocumentObserver(self)
                self._doc_observed = True
            except Exception:
                self._doc_observed = False

    def uninstall(self) -> None:
        console = getattr(App, "Console", None)
        if console is not None:
            for hook_name, orig in list(self._originals.items()):
                try:
                    setattr(console, hook_name, orig)
                except Exception:
                    pass
            self._originals.clear()
            for detach_name in ("detachObserver", "removeObserver"):
                detach_fn = getattr(console, detach_name, None)
                if callable(detach_fn):
                    try:
                        detach_fn(self)
                    except Exception:
                        pass
        if self._doc_observed and hasattr(App, "removeDocumentObserver"):
            try:
                App.removeDocumentObserver(self)
            except Exception:
                pass
            self._doc_observed = False

    @property
    def report(self) -> str:
        return "\n".join(self.messages)

    def violations(self) -> list[str]:
        bad: list[str] = []
        for entry in self.messages:
            for token in FORBIDDEN_CONSOLE_TOKENS:
                if token in entry:
                    bad.append(f"Console report contains {token!r}: {entry}")
        return bad


def _load_design(name: str | Stack = "vermax") -> Stack:
    if isinstance(name, Stack):
        return name
    key = str(name).strip().lower()
    if key not in DRAGONS:
        raise ValueError(f"Unsupported stack design: {name!r}")
    return DRAGONS[key]


def _make_box(part: dict) -> Part.Shape:
    x, y, z = (float(v) for v in part["corner"])
    dx, dy, dz = (float(v) for v in part["size"])
    if dx <= 0.0 or dy <= 0.0 or dz <= 0.0:
        raise ValueError(f"Box {part['id']} has non-positive size: {(dx, dy, dz)}")
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def _make_tube(part: dict) -> Part.Shape:
    ox, oy, oz = (float(v) for v in part["origin"])
    axis = [int(v) for v in part["axis"]]
    if axis not in ([1, 0, 0], [0, 1, 0], [0, 0, 1]):
        raise ValueError(f"Tube {part['id']} has unsupported axis: {axis}")
    r_in = float(part["r_in"])
    r_out = float(part["r_out"])
    length = float(part["length"])
    if r_out <= 0.0 or length <= 0.0 or r_in < 0.0 or r_in >= r_out:
        raise ValueError(f"Tube {part['id']} has invalid dimensions: r_in={r_in}, r_out={r_out}, length={length}")
    origin_vec = App.Vector(ox, oy, oz)
    axis_vec = App.Vector(float(axis[0]), float(axis[1]), float(axis[2]))
    outer = Part.makeCylinder(r_out, length, origin_vec, axis_vec)
    if r_in > 0.0:
        inner = Part.makeCylinder(r_in, length, origin_vec, axis_vec)
        shape = outer.cut(inner)
        if shape.Solids:
            return shape.Solids[0]
        return shape
    return outer


def _make_revolve(part: dict) -> Part.Shape:
    ox, oy, oz = (float(v) for v in part["origin"])
    axis = [int(v) for v in part["axis"]]
    if axis not in ([1, 0, 0], [0, 1, 0]):
        raise ValueError(f"Revolve {part['id']} has unsupported axis: {axis}")
    profile = [(float(axial), float(radius)) for axial, radius in part["profile"]]
    if len(profile) < 2:
        raise ValueError(f"Revolve {part['id']} requires at least two profile points")
    a0 = profile[0][0]
    a1 = profile[-1][0]
    loop = [(a0, 0.0)] + profile + [(a1, 0.0), (a0, 0.0)]
    if axis == [1, 0, 0]:
        vectors = [App.Vector(ox + axial, oy, oz + radius) for axial, radius in loop]
    else:
        vectors = [App.Vector(ox, oy + axial, oz + radius) for axial, radius in loop]
    edges = [Part.LineSegment(a, b).toShape() for a, b in zip(vectors, vectors[1:])]
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    solid = face.revolve(
        App.Vector(ox, oy, oz),
        App.Vector(float(axis[0]), float(axis[1]), float(axis[2])),
        360.0,
    )
    if solid.Solids:
        solid = solid.Solids[0]
    if solid.Volume < 0.0:
        solid.reverse()
    return solid


def _make_prism(part: dict) -> Part.Shape:
    x = float(part["x"])
    dx = float(part["dx"])
    pts = [App.Vector(x, float(y), float(z)) for y, z in part["profile"]]
    wire = Part.makePolygon(pts + [pts[0]])
    face = Part.Face(wire)
    solid = face.extrude(App.Vector(dx, 0.0, 0.0))
    if solid.Solids:
        solid = solid.Solids[0]
    if solid.Volume < 0.0:
        solid.reverse()
    return solid


def _make_shape(part: dict) -> Part.Shape:
    shape_type = part["shape"]
    if shape_type == "box":
        return _make_box(part)
    if shape_type == "tube":
        return _make_tube(part)
    if shape_type == "revolve":
        return _make_revolve(part)
    if shape_type == "prism":
        return _make_prism(part)
    raise ValueError(f"Unsupported shape type {shape_type!r} for part {part['id']}")


def _add_part_feature(doc, part: dict, shape: Part.Shape):
    pid = str(part["id"])
    module = str(part["module"])
    material = str(part["material"])
    zone = str(part["zone"])
    obj = doc.addObject("Part::Feature", pid)
    obj.Shape = shape
    obj.Label = f"{pid}|{module}|{material}|{zone}"
    return obj


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


def _path_bbox(fragment: str) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for path in re.findall(r'd="([^"]*)"', fragment):
        nums = [float(value) for value in re.findall(r"[-+]?(?:\d+\.\d+|\d+)(?:[eE][-+]?\d+)?", path)]
        xs.extend(nums[0::2])
        ys.extend(nums[1::2])
    if not xs:
        return -1.0, -1.0, 1.0, 1.0
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


def _sheet(title: str, sheet_name: str, views: dict[str, str], note: str, modules_line: str, scale: float) -> str:
    del scale
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
<rect width="420" height="297" fill="#f7f4ee"/>
<rect x="8" y="8" width="404" height="281" fill="none" stroke="#1c1a17" stroke-width="0.6"/>
<text x="14" y="18" font-family="Georgia, serif" font-size="5.2" fill="#1c1a17">{title}</text>
<text x="14" y="24" font-family="Georgia, serif" font-size="3.2" fill="#5c5348">{sheet_name}. Projected from the FreeCAD solid. Each view is fitted to its window. Dimensions in mm.</text>
{_view_svg(views["front"], 14, 30, 96, 188)}
{_view_svg(views["side"], 114, 30, 96, 188)}
{_view_svg(views["section"], 214, 30, 96, 188)}
{_view_svg(views["top"], 314, 30, 96, 188)}
<text x="42" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Front, mouth (-Y)</text>
<text x="142" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Side, port (-X)</text>
<text x="236" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Section, X &lt;= 0 (-X)</text>
<text x="352" y="224" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Top, plan (+Z)</text>
<rect x="8" y="232" width="404" height="57" fill="#f7f4ee" stroke="#1c1a17" stroke-width="0.4"/>
<text x="14" y="248" font-family="Georgia, serif" font-size="3.0" fill="#1c1a17">{note}</text>
<text x="14" y="260" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Dimensions in mm. Origin on the mouth plane at the deck centreline (+X right, +Y into the oven, +Z up, deck top at Z = 0).</text>
<text x="14" y="272" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">{modules_line}</text>
<text x="14" y="282" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Rear gutter behind the floating deck admits the burner flame; overhead soffit and riser form the radiant ceiling inside the hood.</text>
</svg>
'''


def _write_sheets(out_dir: Path, design: Stack, report: dict, compound: Part.Shape, section: Part.Shape) -> None:
    views = {
        "front": _oriented_view(compound, "front"),
        "side": _oriented_view(compound, "side"),
        "top": _oriented_view(compound, "top"),
        "section": _oriented_view(section, "section"),
    }
    title = f"{design.dragon} — modular stack"
    mods = report["modules_kg"]
    split = mods.get("brow", 0.0) > 0.05
    if split:
        module_note = (
            f"Pit {mods['pit']:.2f} kg, hearth {mods['hearth']:.2f} kg, "
            f"brow {mods['brow']:.2f} kg, tunnel {mods['tunnel']:.2f} kg"
        )
        modules_line = (
            "Four modules (pit, hearth, brow, tunnel). The brow sits on a shelf at the fold. "
            "Etched inside the brow: 300 is the deck. 550 is the ceiling."
        )
    else:
        module_note = f"Three modules: pit {mods['pit']:.2f} kg, hearth {mods['hearth']:.2f} kg, hood {mods['hood']:.2f} kg"
        modules_line = (
            "Three modules (pit, hearth, hood): bare-steel pit with insulated belly, "
            "hearth frame with floating mild-steel deck, and insulated rectangular hood."
        )
    note = (
        f"{module_note} · "
        f"floating deck {DECK_W:.0f}×{DECK_L:.0f}×{design.deck_t:.1f} mm · "
        f"rear gutter {GUTTER_L:.0f} mm · "
        f"soffit {design.soffit_h:.0f} mm (Y {soffit_y0(design):.0f}..{SOFFIT_Y1:.0f} mm) · "
        f"mouth {MOUTH_W:.0f}×{report['mouth_h']:.0f} mm · "
        f"overall {report['body_width_mm']:.1f}×{report['body_length_mm']:.1f}×{report['body_height_mm']:.1f} mm · "
        f"ready {report['ready_kg']:.2f} kg"
    )
    sheet = _sheet(title, "General arrangement — front, side, section, top", views, note, modules_line, scale=0.35)
    (out_dir / "ga-arrangement.svg").write_text(sheet, encoding="utf-8")

    subtitles = {
        "front": (
            f"Front view from -Y (mouth {MOUTH_W:.0f}×{report['mouth_h']:.0f} mm, "
            f"front height {design.front_h:.0f} mm, dimensions in mm)"
        ),
        "side": (
            f"Side view from -X "
            f"(length {report['body_length_mm']:.1f} mm, height {report['body_height_mm']:.1f} mm)"
        ),
        "top": (
            f"Top view from +Z (width {report['body_width_mm']:.1f} mm, "
            f"floating deck {DECK_W:.0f}×{DECK_L:.0f} mm, rear gutter {GUTTER_L:.0f} mm)"
        ),
        "section": (
            f"Centreline section, port half removed, from -X (floating deck {design.deck_t:.1f} mm, "
            f"rear gutter {GUTTER_L:.0f} mm, soffit {design.soffit_h:.0f} mm)"
        ),
    }
    for view_name, fragment in views.items():
        png_path = out_dir / f"{view_name}.png"
        _render_png(
            fragment,
            f"{title} — {view_name.capitalize()} View",
            subtitles[view_name],
            png_path,
            width=960,
            height=720,
        )


def build(name: str = "vermax") -> dict:
    design = _load_design(name)
    expected_parts = parts(design)
    report = evaluate(design)

    slug = design.dragon.lower()
    out_dir = ROOT / "design" / "stream-2" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    gate_path = out_dir / "gate.json"

    observer = _ConsoleObserver()
    observer.install()
    try:
        if design.dragon in App.listDocuments():
            App.closeDocument(design.dragon)
        doc = App.newDocument(design.dragon)

        made: list[tuple[object, dict]] = []
        for item in expected_parts:
            shape = _make_shape(item)
            obj = _add_part_feature(doc, item, shape)
            made.append((obj, item))

        doc.recompute()

        gate_errors: list[str] = []
        invalid_parts: list[dict] = []
        part_records: list[dict] = []
        part_masses_map: dict[str, float] = {}
        modules_kg = {"pit": 0.0, "hearth": 0.0, "hood": 0.0}

        doc_objects = list(doc.Objects)
        expected_ids = [str(item["id"]) for item in expected_parts]
        actual_ids = [str(obj.Label).split("|")[0] for obj in doc_objects]

        count_ok = len(doc_objects) == len(expected_parts)
        ids_ok = actual_ids == expected_ids
        if not count_ok:
            gate_errors.append(f"Part count mismatch: got {len(doc_objects)}, expected {len(expected_parts)}")
        if not ids_ok:
            gate_errors.append("Part IDs in document do not match parts(design)")

        all_shapes: list[Part.Shape] = []
        visible_solids: list[Part.Shape] = []
        pit_solids: list[Part.Shape] = []
        total_solid_mass_kg = 0.0

        for obj, item in made:
            pid = str(item["id"])
            module = str(item["module"])
            material = str(item["material"])
            zone = str(item["zone"])
            shp = obj.Shape
            all_shapes.append(shp)

            state_flags = [str(flag) for flag in getattr(obj, "State", ())]
            status_text = str(obj.getStatusString()) if hasattr(obj, "getStatusString") else "Valid"
            valid_shape = bool(shp.isValid()) and ("Invalid" not in state_flags) and ("Error" not in status_text)
            vol_mm3 = float(shp.Volume)
            positive_vol = vol_mm3 > 0.0

            if not valid_shape or not positive_vol:
                invalid_parts.append(
                    {
                        "id": pid,
                        "isValid": valid_shape,
                        "volume_mm3": round(vol_mm3, 3),
                        "state": state_flags,
                        "status": status_text,
                    }
                )
                gate_errors.append(
                    f"Invalid solid {pid}: isValid={valid_shape}, volume={vol_mm3:.3f} mm^3, status={status_text}"
                )

            if material == "keepout":
                mass_kg = 0.0
            else:
                mass_kg = vol_mm3 * 1e-9 * float(DENS[material])
                total_solid_mass_kg += mass_kg
                modules_kg[module] = modules_kg.get(module, 0.0) + mass_kg
                visible_solids.append(shp)
                if module == "pit":
                    pit_solids.append(shp)

            part_masses_map[pid] = round(mass_kg, 4)
            part_records.append(
                {
                    "id": pid,
                    "label": str(obj.Label),
                    "module": module,
                    "material": material,
                    "zone": zone,
                    "isValid": valid_shape,
                    "volume_mm3": round(vol_mm3, 3),
                    "mass_kg": round(mass_kg, 4),
                }
            )

        # Pairwise common() volume check across all built solids (including keepout).
        press_pairs = active_press_fits([item for _obj, item in made])
        press_lookup = {frozenset(pair): (str(pair[0]), str(pair[1])) for pair in press_pairs}
        press_volumes_mm3: dict[str, float] = {f"{a}|{b}": 0.0 for a, b in press_pairs}
        press_pair_rows: list[dict] = []
        interferences: list[dict] = []
        max_non_press_common_mm3 = 0.0

        n_made = len(made)
        for i in range(n_made):
            obj_a, item_a = made[i]
            id_a = str(item_a["id"])
            shape_a = obj_a.Shape
            bb_a = shape_a.BoundBox
            for j in range(i + 1, n_made):
                obj_b, item_b = made[j]
                id_b = str(item_b["id"])
                shape_b = obj_b.Shape
                if bb_a.intersect(shape_b.BoundBox):
                    common_shape = shape_a.common(shape_b)
                    common_vol = abs(float(common_shape.Volume)) if common_shape.Solids else 0.0
                else:
                    common_vol = 0.0

                pair_set = frozenset((id_a, id_b))
                if pair_set in press_lookup:
                    pa, pb = press_lookup[pair_set]
                    press_volumes_mm3[f"{pa}|{pb}"] = round(common_vol, 3)
                else:
                    if common_vol > max_non_press_common_mm3:
                        max_non_press_common_mm3 = common_vol
                    if common_vol > 1.0:
                        msg = f"Interference between {id_a} and {id_b}: common volume {common_vol:.3f} mm^3 > 1.0 mm^3"
                        gate_errors.append(msg)
                        interferences.append(
                            {
                                "ids": [id_a, id_b],
                                "volume_mm3": round(common_vol, 3),
                                "message": msg,
                            }
                        )

        press_fits_ok = True
        for pa, pb in press_pairs:
            key = f"{pa}|{pb}"
            vol = press_volumes_mm3.get(key, 0.0)
            press_pair_rows.append({"ids": [pa, pb], "volume_mm3": vol, "ok": vol > 1.0})
            if vol <= 1.0:
                press_fits_ok = False
                gate_errors.append(
                    f"Press-fit pair {pa} and {pb} has common volume {vol:.3f} mm^3 <= 1.0 mm^3"
                )

        # Bounding box gate: within 3 mm of evaluate(design)["bbox_mm"] on every side.
        all_compound = Part.makeCompound(all_shapes)
        bb = all_compound.BoundBox
        actual_bbox_mm = [
            round(float(bb.XMin), 2),
            round(float(bb.YMin), 2),
            round(float(bb.ZMin), 2),
            round(float(bb.XMax), 2),
            round(float(bb.YMax), 2),
            round(float(bb.ZMax), 2),
        ]
        expected_bbox_mm = [float(x) for x in report["bbox_mm"]]
        bbox_deltas_mm = [round(abs(a - b), 3) for a, b in zip(actual_bbox_mm, expected_bbox_mm)]
        max_bbox_delta_mm = max(bbox_deltas_mm) if bbox_deltas_mm else 0.0
        bbox_ok = all(delta <= 3.0 for delta in bbox_deltas_mm)
        if not bbox_ok:
            gate_errors.append(
                f"Bounding box {actual_bbox_mm} deviates from {expected_bbox_mm} by {bbox_deltas_mm} mm (> 3.0 mm)"
            )

        # Mass gate: within 3% of evaluate(design)["ready_kg"] - 1.85 kg burner allowance.
        expected_solid_mass_kg = float(report["ready_kg"]) - float(BURNER_KG)
        mass_diff_kg = abs(total_solid_mass_kg - expected_solid_mass_kg)
        mass_rel_error = mass_diff_kg / expected_solid_mass_kg if expected_solid_mass_kg > 0.0 else 0.0
        mass_ok = mass_rel_error <= 0.03
        if not mass_ok:
            gate_errors.append(
                f"Mass sum {total_solid_mass_kg:.3f} kg differs from {expected_solid_mass_kg:.3f} kg "
                f"by {mass_rel_error * 100.0:.2f}% (> 3%)"
            )

        # Save FCStd, STEP files, section, and drawings.
        fcstd_path = out_dir / f"{slug}.FCStd"
        step_path = out_dir / f"{slug}.step"
        pit_step_path = out_dir / f"{slug}-pit.step"

        doc.saveAs(str(fcstd_path))

        compound = Part.makeCompound(visible_solids)
        pit_compound = Part.makeCompound(pit_solids)
        compound.exportStep(str(step_path))
        pit_compound.exportStep(str(pit_step_path))

        # The side camera looks from -X. Remove the port half so that face is the cut.
        cbb = compound.BoundBox
        cut_pad = 50.0
        cut_dx = max(-float(cbb.XMin), 0.0) + cut_pad
        cut_dy = float(cbb.YMax - cbb.YMin) + 2.0 * cut_pad
        cut_dz = float(cbb.ZMax - cbb.ZMin) + 2.0 * cut_pad
        cut_box = Part.makeBox(
            cut_dx,
            cut_dy,
            cut_dz,
            App.Vector(float(cbb.XMin) - cut_pad, float(cbb.YMin) - cut_pad, float(cbb.ZMin) - cut_pad),
        )
        section = compound.copy().cut(cut_box)
        _write_sheets(out_dir, design, report, compound, section)

        console_violations = observer.violations()
        gate_errors.extend(console_violations)
        console_ok = len(console_violations) == 0
        shapes_ok = len(invalid_parts) == 0
        interference_ok = len(interferences) == 0 and press_fits_ok
        passed = console_ok and shapes_ok and count_ok and ids_ok and interference_ok and bbox_ok and mass_ok

        gate_payload = {
            "dragon": design.dragon,
            "design": design.to_json(),
            "passed": passed,
            "ok": passed,
            "status": "pass" if passed else "fail",
            "errors": gate_errors,
            "console_ok": console_ok,
            "console_messages": observer.messages,
            "console_report": observer.report,
            "shapes_valid": shapes_ok,
            "all_valid": shapes_ok,
            "positive_volumes": shapes_ok,
            "invalid_parts": invalid_parts,
            "part_count": len(doc_objects),
            "expected_part_count": len(expected_parts),
            "n_parts": len(doc_objects),
            "ids_match": ids_ok,
            "part_ids": actual_ids,
            "press_fits_ok": press_fits_ok,
            "press_fits": press_volumes_mm3,
            "press_fit_pairs": press_pair_rows,
            "interference_ok": interference_ok,
            "interferences": interferences,
            "collisions": interferences,
            "max_non_press_common_mm3": round(max_non_press_common_mm3, 3),
            "bbox_ok": bbox_ok,
            "bbox_mm": actual_bbox_mm,
            "expected_bbox_mm": expected_bbox_mm,
            "bbox_deltas_mm": bbox_deltas_mm,
            "max_bbox_delta_mm": max_bbox_delta_mm,
            "mass_ok": mass_ok,
            "mass_kg": round(total_solid_mass_kg, 3),
            "freecad_kg": round(total_solid_mass_kg, 3),
            "solid_mass_kg": round(total_solid_mass_kg, 3),
            "expected_mass_kg": round(expected_solid_mass_kg, 3),
            "analytical_kg": round(expected_solid_mass_kg, 3),
            "ready_kg": round(total_solid_mass_kg + float(BURNER_KG), 3),
            "expected_ready_kg": round(float(report["ready_kg"]), 3),
            "burner_allowance_kg": float(BURNER_KG),
            "mass_rel_error": round(mass_rel_error, 6),
            "mass_diff_pct": round(mass_rel_error * 100.0, 4),
            "modules_kg": {
                "pit": round(modules_kg["pit"] + float(BURNER_KG), 3),
                "hearth": round(modules_kg["hearth"], 3),
                "hood": round(modules_kg["hood"], 3),
                "brow": round(modules_kg.get("brow", 0.0), 3),
                "tunnel": round(modules_kg.get("tunnel", 0.0), 3),
            },
            "solid_modules_kg": {k: round(v, 3) for k, v in modules_kg.items()},
            "parts": part_masses_map,
            "part_details": part_records,
            "gates": {
                "shapes_and_console": shapes_ok and console_ok,
                "part_count_and_ids": count_ok and ids_ok,
                "pairwise_common": interference_ok,
                "bbox": bbox_ok,
                "mass": mass_ok,
            },
            "files": {
                "fcstd": str(fcstd_path),
                "step": str(step_path),
                "pit_step": str(pit_step_path),
                "svg": str(out_dir / "ga-arrangement.svg"),
                "front_png": str(out_dir / "front.png"),
                "side_png": str(out_dir / "side.png"),
                "top_png": str(out_dir / "top.png"),
                "section_png": str(out_dir / "section.png"),
            },
        }
        gate_path.write_text(json.dumps(gate_payload, indent=2) + "\n", encoding="utf-8")

        if not passed:
            raise SystemExit("; ".join(gate_errors))

        return gate_payload
    finally:
        observer.uninstall()


if __name__ == "__main__":
    build(os.environ.get("VARIANT", "vermax"))