"""Solids for the Angas 430.

Axis: X to the right, Y from the mouth (negative) toward the back, Z up
from the underside of the base pan. The crown is a separate solid so it
can lift off the cinch. The burner is an envelope, not a jet.
"""

from __future__ import annotations

from build123d import Axis, Box, Color, Compound, Cylinder, Pos, Rot

from cad.tailgate.profile import cylinder_shell, ellipse_points, offset_open, shell_between
from cad.tailgate.spec import SPEC, TailgateSpec

DENSITY = {
    "cordierite": 2100.0,
    "steel": 7900.0,
    "aes": 128.0,
    "casi": 250.0,
    "brass": 8530.0,
    "jarrah": 820.0,
    "rubber": 1100.0,
}


def _paint(part, rgb: tuple[float, float, float], label: str, kind: str):
    part.label = label
    part.color = Color(*rgb)
    part._kind = kind  # type: ignore[attr-defined]
    return part


def _mouth(spec: TailgateSpec):
    """Cutter through the front wall only. The arch is below the joggle."""
    z = spec.hearth_z + spec.mouth_h / 2
    radial = spec.wall_stack + 24
    y = -(spec.chamber_r + spec.outer_radius) / 2
    return Pos(0, y, z) * Box(spec.mouth_w, radial, spec.mouth_h)


def _dome_shell(spec: TailgateSpec, inner_offset: float, outer_offset: float):
    inner = offset_open(ellipse_points(spec.chamber_r, spec.dome_rise, spec.spring_z, 36), inner_offset)
    outer = offset_open(ellipse_points(spec.chamber_r, spec.dome_rise, spec.spring_z, 36), outer_offset)
    return shell_between(inner, outer)


def build(spec: TailgateSpec = SPEC, *, explode: float = 0.0, cutaway: bool = False,
          deployed_legs: bool = True, stowed: bool = False) -> Compound:
    """One assembly. `explode` lifts the crown, in millimetres."""
    s = spec
    mouth = _mouth(s)
    r = s.chamber_r
    skin_in = r + s.liner_t + s.insulation_t
    skin_out = skin_in + s.skin_t

    base = _paint(Pos(0, 0, s.base_t / 2) * Cylinder(skin_out, s.base_t), (0.45, 0.47, 0.49), "base-pan", "steel")
    lip = _paint(
        cylinder_shell(skin_out - s.base_t, skin_out, s.base_t, s.base_t + 14),
        (0.45, 0.47, 0.49), "base-lip", "steel",
    )
    floor_aes = _paint(
        Pos(0, 0, s.base_t + s.floor_aes / 2) * Cylinder(r + s.liner_t, s.floor_aes),
        (0.86, 0.78, 0.55), "floor-aes", "aes",
    )
    floor_casi = _paint(
        Pos(0, 0, s.base_t + s.floor_aes + s.floor_casi / 2) * Cylinder(r, s.floor_casi),
        (0.78, 0.76, 0.70), "floor-casi", "casi",
    )
    stone_pan_z = s.base_t + s.floor_aes + s.floor_casi
    stone_pan = _paint(
        Pos(0, 0, stone_pan_z + s.liner_t / 2) * Cylinder(r, s.liner_t),
        (0.62, 0.64, 0.66), "stone-pan", "steel",
    )
    # Stone offset to +X leaves a crescent on the left for the bought burner.
    stone_shift = 8.0
    stone = _paint(
        Pos(stone_shift, 0, s.hearth_z - s.floor_t / 2) * Cylinder(s.floor_d / 2, s.floor_t),
        (0.76, 0.60, 0.40), "floor-cordierite", "cordierite",
    )

    liner_skirt = cylinder_shell(r, r + s.liner_t, s.hearth_z, s.spring_z) - mouth
    liner_skirt = _paint(liner_skirt, (0.62, 0.64, 0.66), "liner-skirt", "steel")
    liner_dome = _paint(_dome_shell(s, 0.0, s.liner_t), (0.62, 0.64, 0.66), "liner-dome", "steel")

    wall_aes = cylinder_shell(r + s.liner_t, r + s.liner_t + s.wall_aes, s.hearth_z, s.spring_z) - mouth
    wall_aes = _paint(wall_aes, (0.90, 0.84, 0.62), "wall-aes", "aes")
    wall_casi = cylinder_shell(
        r + s.liner_t + s.wall_aes,
        r + s.liner_t + s.insulation_t,
        s.hearth_z,
        s.spring_z,
    ) - mouth
    wall_casi = _paint(wall_casi, (0.78, 0.76, 0.70), "wall-casi", "casi")
    crown_aes = _paint(
        _dome_shell(s, s.liner_t, s.liner_t + s.crown_aes),
        (0.90, 0.84, 0.62), "crown-aes", "aes",
    )

    skirt = cylinder_shell(skin_in, skin_out, s.base_t, s.spring_z - s.joggle_h) - mouth
    skirt = _paint(skirt, (0.72, 0.74, 0.76), "shell-skirt", "steel")
    joggle_r_out = skin_in - 0.4
    joggle = _paint(
        cylinder_shell(joggle_r_out - s.skin_t, joggle_r_out, s.spring_z - s.joggle_h, s.spring_z),
        (0.68, 0.70, 0.72), "shell-joggle", "steel",
    )
    # Crown starts just below the top of the joggle so it captures it, and
    # is the part that lifts off.
    dome = _dome_shell(s, s.liner_t + s.crown_aes, s.wall_stack)
    # A short lip on the dome, down over the joggle.
    lip_dome = cylinder_shell(skin_in, skin_out, s.spring_z - s.joggle_h + 1.0, s.spring_z + 2.0)
    dome = _paint(dome + lip_dome, (0.78, 0.80, 0.82), "shell-crown", "steel")

    band = _paint(
        cylinder_shell(skin_out, skin_out + s.band_t, s.spring_z - s.joggle_h - 4, s.spring_z - s.joggle_h - 4 + s.band_w),
        (0.72, 0.55, 0.28), "cinch-band", "brass",
    )
    # Two dowels through the band into the skirt, so the crown cannot walk
    # in the tub. They are the road lock. The band bolt is the third.
    dowels = []
    for angle, name in ((140, "dowel-a"), (220, "dowel-b")):
        pin = (
            Rot(axis=Axis.Z, angle=angle)
            * Pos(skin_out - 2, 0, s.spring_z - s.joggle_h + 8)
            * Rot(axis=Axis.Y, angle=90)
            * Cylinder(2.5, s.band_t + 8)
        )
        dowels.append(_paint(pin, (0.55, 0.56, 0.58), name, "steel"))

    handles = []
    handle_z = s.hearth_z + 40
    for sign, name in ((-1, "handle-port"), (1, "handle-starboard")):
        grip = (
            Pos(sign * (skin_out + s.handle_standoff + s.handle_len / 2 - 10), 0, handle_z)
            * Rot(axis=Axis.Y, angle=90)
            * Cylinder(s.handle_od / 2, s.handle_len)
        )
        handles.append(_paint(grip, (0.40, 0.22, 0.14), name, "jarrah"))
        ferrule = (
            Pos(sign * (skin_out + s.handle_standoff), 0, handle_z)
            * Rot(axis=Axis.Y, angle=90)
            * Cylinder(s.handle_od / 2 + 2, 8)
        )
        handles.append(_paint(ferrule, (0.72, 0.55, 0.28), name + "-ferrule", "brass"))

    # Bought burner envelope. Mass is an allowance, not this volume.
    burner = _paint(
        Pos(-(r - 18), 30, s.hearth_z + 18) * Box(36, 260, 28),
        (0.40, 0.42, 0.44), "burner-certified", "allowance",
    )
    badge = _paint(
        Pos(0, -(skin_out + 1), s.spring_z + 18) * Box(90, 3, 28),
        (0.72, 0.55, 0.28), "badge", "brass",
    )
    # Mouth frame. Covers the cut edge of the blanket. Sits on the front face.
    frame_y = -(skin_out - 2)
    frame_z = s.hearth_z + s.mouth_h / 2
    frame_outer = Pos(0, frame_y, frame_z) * Box(s.mouth_w + 28, 3, s.mouth_h + 22)
    frame_inner = Pos(0, frame_y, frame_z) * Box(s.mouth_w - 6, 12, s.mouth_h - 6)
    mouth_frame = _paint(frame_outer - frame_inner, (0.55, 0.57, 0.60), "mouth-frame", "steel")
    # Peel landing, stolen from the wood concept: a sill in front of the arch.
    landing = _paint(
        Pos(0, -(skin_out + 22), s.hearth_z - 2) * Box(s.mouth_w, 45, s.base_t),
        (0.62, 0.64, 0.66), "peel-landing", "steel",
    )

    stubs = []
    for angle in (30, 150, 270):
        foot = (
            Rot(axis=Axis.Z, angle=angle)
            * Pos(skin_out * 0.72, 0, -s.stub_h / 2)
            * Cylinder(22, s.stub_h)
        )
        stubs.append(_paint(foot, (0.35, 0.20, 0.12), "stub-foot", "jarrah"))

    legs = []
    if deployed_legs and not stowed:
        from design.tailgate.geom import foot_center, tube_along
        for angle in (30, 150, 270):
            leg = tube_along(s.leg_len, s.leg_od / 2, 12, angle, 8)
            legs.append(_paint(leg, (0.55, 0.57, 0.60), "leg", "steel"))
            dx, dy, dz = foot_center(s.leg_len, 12, angle, 8)
            legs.append(_paint(Pos(dx, dy, dz) * Cylinder(16, 10), (0.12, 0.12, 0.12), "leg-foot", "rubber"))
    if stowed:
        for index, angle_name in enumerate(("leg-stowed-a", "leg-stowed-b", "leg-stowed-c")):
            laid = Pos(skin_out + 40 + index * (s.leg_od + 8), 0, s.leg_od) * Rot(axis=Axis.X, angle=90) * Cylinder(s.leg_od / 2, s.leg_len)
            legs.append(_paint(laid, (0.55, 0.57, 0.60), angle_name, "steel"))

    crown_parts = [liner_dome, crown_aes, dome, badge]
    body_parts = [
        base, lip, floor_aes, floor_casi, stone_pan, stone, liner_skirt,
        wall_aes, wall_casi, skirt, joggle, band, *dowels, *handles, burner, mouth_frame, landing, *stubs,
    ]
    if explode:
        crown_parts = [Pos(0, 0, explode) * part for part in crown_parts]
        band_lifted = Pos(0, 0, explode * 0.35) * band
        body_parts = [part for part in body_parts if part.label != "cinch-band"]
        body_parts.append(band_lifted)

    parts = body_parts + crown_parts + legs
    if cutaway:
        cutter = Pos(s.outer_radius * 0.45, -s.outer_radius * 0.15, s.body_height * 0.55) * Box(
            s.outer_diameter * 0.7, s.outer_diameter * 0.7, s.body_height
        )
        opened = []
        for part in parts:
            if part.label and any(token in part.label for token in ("shell-skirt", "wall-aes", "wall-casi", "shell-crown", "crown-aes", "liner-skirt", "liner-dome")):
                rgb = tuple(part.color)[:3]
                opened.append(_paint(part - cutter, rgb, part.label, part._kind))
            else:
                opened.append(part)
        parts = opened

    compound = Compound(children=parts)
    compound.label = s.name
    return compound


def mass_report(assembly: Compound, spec: TailgateSpec = SPEC) -> dict:
    """Kilograms from solid volumes. The burner allowance replaces its placeholder."""
    by_kind: dict[str, float] = {}
    rows = []
    for child in assembly.children:
        kind = getattr(child, "_kind", "steel")
        if kind == "allowance":
            continue
        kg = child.volume * 1e-9 * DENSITY[kind]
        by_kind[kind] = by_kind.get(kind, 0.0) + kg
        rows.append({"label": child.label, "kind": kind, "kg": round(kg, 3)})
    metal_and_rest = sum(by_kind.values())
    stone = by_kind.get("cordierite", 0.0)
    legs = sum(row["kg"] for row in rows if row["label"] and "leg" in row["label"])
    total = metal_and_rest + spec.burner_kg
    return {
        "by_kind_kg": {key: round(value, 2) for key, value in by_kind.items()},
        "burner_allowance_kg": spec.burner_kg,
        "stone_kg": round(stone, 2),
        "legs_kg": round(legs, 2),
        "ready_kg": round(total, 2),
        "stone_out_kg": round(total - stone, 2),
        "carry_without_stone_or_legs_kg": round(total - stone - legs, 2),
        "rows": rows,
    }
