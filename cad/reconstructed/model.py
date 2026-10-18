"""Parametric solids for the three reconstructed ovens.

The cooking void is a half-ellipse of the published width and apex, run the
published depth. The mouth is a shorter window in the front wall, so the
lintel above it is the weir that holds the flame roll. Insulation is one
elliptical blanket per published layer. The outer skin is a thin shell, not
a solid box, because a solid box of this envelope would weigh more than the
published oven.
"""

from __future__ import annotations

from build123d import (
    Axis,
    Box,
    BuildLine,
    BuildSketch,
    Color,
    Compound,
    Cylinder,
    EllipticalCenterArc,
    Line,
    Part,
    Plane,
    Pos,
    Rot,
    extrude,
    make_face,
)

from cad.reconstructed.spec import OvenSpec

# kg/m^3. Used only for the mass report, not for the geometry.
DENSITY = {
    "liner": 7900.0,
    "skin": 7850.0,
    "insulation": 128.0,
    "underfloor": 240.0,
    "stone": 2100.0,
    "flue": 7850.0,
    "landing": 2700.0,
    "door": 7850.0,
    "grate": 7900.0,
    "burner": 7900.0,
    "handles": 2700.0,
}


def _half_ellipse(width: float, height: float, depth: float) -> Part:
    """Half-ellipse extruded along +Y. Base on local Z = 0, apex at +Z."""
    if width <= 0 or height <= 0 or depth <= 0:
        raise ValueError("ellipse dimensions must be positive")
    with BuildSketch(Plane.XY) as sketch:
        with BuildLine():
            EllipticalCenterArc((0, 0), width / 2, height, start_angle=0, arc_size=180)
            Line((width / 2, 0), (-width / 2, 0))
        make_face()
    # Sketch is X (width) by Y (height), extruded +Z (depth).
    # +90° about X maps sketch Y onto +Z and the extrude onto -Y.
    # The following shift puts the depth back on 0..depth.
    raw = extrude(sketch.face(), amount=depth)
    turned = Rot(axis=Axis.X, angle=90) * raw
    return Pos(0, depth, 0) * turned


def _place_vault(width: float, height: float, depth: float, y0: float, z0: float) -> Part:
    return Pos(0, y0, z0) * _half_ellipse(width, height, depth)


def _shell(outer: Part, inner: Part) -> Part:
    return outer - inner


def _color(part: Part, rgb: tuple[float, float, float], label: str) -> Part:
    part.label = label
    part.color = Color(*rgb)
    return part


def build_oven(spec: OvenSpec, *, explode: float = 0.0, cutaway: bool = False) -> Compound:
    """Assemble one oven. `explode` pulls layers apart along Z, in millimetres."""
    hearth = spec.hearth_z
    roof = spec.roof_space
    layers = spec.insulation_mm
    insul_total = sum(layers)

    void = _place_vault(spec.int_w, spec.int_h, spec.int_d, spec.front_wall, hearth)

    liner_outer = _place_vault(
        spec.int_w + 2 * spec.liner_t,
        spec.int_h + spec.liner_t,
        spec.int_d,
        spec.front_wall,
        hearth,
    )
    liner = _color(_shell(liner_outer, void), (0.72, 0.74, 0.78), f"{spec.oven_id}-liner")

    blankets: list[Part] = []
    grown = spec.liner_t
    previous = liner_outer
    for index, thickness in enumerate(layers, start=1):
        grown += thickness
        nxt = _place_vault(
            spec.int_w + 2 * grown,
            spec.int_h + grown,
            spec.int_d,
            spec.front_wall,
            hearth,
        )
        blanket = _color(_shell(nxt, previous), (0.86, 0.78, 0.55), f"{spec.oven_id}-blanket-{index}")
        blankets.append(blanket)
        previous = nxt

    # Outer elliptical skin. Width is the published external width. Apex
    # reaches the published (or inferred) body height.
    skin_outer = _place_vault(spec.ext_w, spec.int_h + roof, spec.ext_d, 0, hearth)
    skin_inner = _place_vault(
        spec.ext_w - 2 * spec.outer_t,
        spec.int_h + roof - spec.outer_t,
        spec.ext_d - 2 * spec.outer_t,
        spec.outer_t,
        hearth,
    )
    skin = _shell(skin_outer, skin_inner)

    # Skirt below the hearth: a thin rectangular shell, open at the top.
    skirt_h = hearth - spec.stone_t - 25.0
    if skirt_h < 12:
        skirt_h = max(8.0, hearth * 0.45)
    skirt_outer = Pos(0, spec.ext_d / 2, skirt_h / 2) * Box(spec.ext_w, spec.ext_d, skirt_h)
    skirt_inner = Pos(0, spec.ext_d / 2, (skirt_h + spec.outer_t) / 2) * Box(
        spec.ext_w - 2 * spec.outer_t,
        spec.ext_d - 2 * spec.outer_t,
        skirt_h,
    )
    skirt = _color(skirt_outer - skirt_inner, (0.22, 0.23, 0.26), f"{spec.oven_id}-skirt")

    under_t = 25.0 if spec.stone_t < 20 else 40.0
    under = _color(
        Pos(0, spec.front_wall + spec.int_d / 2, hearth - spec.stone_t - under_t / 2)
        * Box(spec.int_w - 4, spec.int_d - 4, under_t),
        (0.80, 0.76, 0.62),
        f"{spec.oven_id}-underfloor",
    )

    # Stone floats: 4 mm clear of the liner in plan, top flush with the hearth.
    stone = _color(
        Pos(0, spec.front_wall + spec.int_d / 2, hearth - spec.stone_t / 2)
        * Box(spec.int_w - 8, spec.int_d - 8, spec.stone_t),
        (0.55, 0.62, 0.72),
        f"{spec.oven_id}-stone",
    )

    # Mouth window through the front cap. The metal left above the opening is
    # the lintel: mouth height over apex is the published ratio, and the
    # opening is the published width. A separate rectangular plate is not
    # used, because it does not follow the vault.
    window = Pos(0, max(spec.front_wall, 8) / 2, hearth + spec.mouth_h / 2) * Box(
        spec.mouth_w,
        max(spec.front_wall, 8) + 6,
        spec.mouth_h,
    )
    skin = _color(skin - window, (0.25, 0.27, 0.30), f"{spec.oven_id}-skin")
    liner = _color(liner - window, (0.72, 0.74, 0.78), f"{spec.oven_id}-liner")
    blankets = [
        _color(blanket - window, (0.86, 0.78, 0.55), f"{spec.oven_id}-blanket-{index}")
        for index, blanket in enumerate(blankets, start=1)
    ]

    # Landing sill, entirely inside the front face.
    landing = _color(
        Pos(0, 10, hearth - 3) * Box(min(spec.mouth_w + 16, spec.ext_w - 8), 12, 6),
        (0.62, 0.64, 0.66),
        f"{spec.oven_id}-landing",
    )

    # Lateral burner: a tube along the left wall, above the stone.
    burner_r = 7.0 if spec.power_kw < 6 else 11.0
    burner_len = spec.int_d * 0.72
    burner = _color(
        Pos(-spec.int_w / 2 + 18, spec.front_wall + spec.int_d * 0.55, hearth + 36)
        * Rot(axis=Axis.X, angle=90)
        * Cylinder(burner_r, burner_len),
        (0.55, 0.57, 0.60),
        f"{spec.oven_id}-burner",
    )

    parts: list[Part] = [skirt, under, stone, liner, *blankets, skin, landing, burner]

    if spec.oven_id == "tread":
        # Roof-rack handles, the feature that makes this the one you carry.
        for x in (-spec.ext_w * 0.28, spec.ext_w * 0.28):
            handle = Pos(x, spec.ext_d * 0.45, spec.body_h - 6) * Rot(axis=Axis.X, angle=90) * Cylinder(6, 70)
            parts.append(_color(handle, (0.45, 0.48, 0.40), f"{spec.oven_id}-handle"))

    if spec.flue:
        flue_h = spec.ext_h_published - spec.body_h
        flue_r = 55.0
        flue_wall = 1.5
        flue_y = spec.front_wall + 70
        flue_z0 = hearth + spec.int_h + roof - 10
        outer_tube = Pos(0, flue_y, flue_z0 + flue_h / 2) * Cylinder(flue_r, flue_h)
        inner_tube = Pos(0, flue_y, flue_z0 + flue_h / 2) * Cylinder(flue_r - flue_wall, flue_h + 2)
        flue = _color(outer_tube - inner_tube, (0.30, 0.32, 0.34), f"{spec.oven_id}-flue")
        cap = _color(
            Pos(0, flue_y, spec.body_h + flue_h - 1.5) * Cylinder(flue_r + 8, 3),
            (0.30, 0.32, 0.34),
            f"{spec.oven_id}-flue-cap",
        )
        # 3 mm rain gap is the published relationship of the cap to the collar.
        # The cap is modelled 3 mm proud of a stop ring rather than sealed down.
        ring = _color(
            Pos(0, flue_y, spec.body_h + flue_h - 8) * Cylinder(flue_r + 4, 2),
            (0.40, 0.42, 0.44),
            f"{spec.oven_id}-flue-ring",
        )
        parts.extend([flue, ring, cap])
        # Throat: a short duct from the crown, just behind the lintel, into the flue.
        throat = _color(
            Pos(0, flue_y, hearth + spec.int_h + 20) * Box(90, 50, 40),
            (0.70, 0.72, 0.75),
            f"{spec.oven_id}-throat",
        )
        parts.append(throat)
        # Wood grate on the right, over the zone the manual calls the duct grate.
        bars = []
        for i, y in enumerate((spec.int_d * 0.35, spec.int_d * 0.5, spec.int_d * 0.65)):
            bar = (
                Pos(spec.int_w / 2 - 80, spec.front_wall + y, hearth + 8)
                * Rot(axis=Axis.Y, angle=90)
                * Cylinder(4, 120)
            )
            bars.append(bar)
        grate = _color(Compound(children=bars), (0.35, 0.36, 0.38), f"{spec.oven_id}-grate")
        parts.append(grate)

    if spec.door:
        door_y = -22 if explode else 4
        door = _color(
            Pos(0, door_y, hearth + spec.mouth_h / 2) * Box(spec.mouth_w + 16, 2.0, spec.mouth_h + 8),
            (0.18, 0.19, 0.20),
            f"{spec.oven_id}-door",
        )
        parts.append(door)

    if cutaway:
        # Remove the right-front quadrant of the skin and blankets so the
        # vault, stone, and burner stay in view. The liner is left whole.
        cutter = Pos(spec.ext_w * 0.25, spec.ext_d * 0.35, spec.body_h * 0.55) * Box(
            spec.ext_w * 0.7,
            spec.ext_d * 0.75,
            spec.body_h,
        )
        opened: list[Part] = []
        for part in parts:
            if part.label and any(token in part.label for token in ("skin", "blanket", "skirt")):
                opened.append(_color(part - cutter, (0.42, 0.44, 0.46), part.label))
            else:
                opened.append(part)
        parts = opened

    if explode:
        lifted: list[Part] = []
        for index, part in enumerate(parts):
            lifted.append(Pos(0, 0, explode * index * 0.15) * part)
        parts = lifted

    compound = Compound(children=parts)
    compound.label = f"{spec.oven_id}-reconstruction"
    return compound


def mass_report(spec: OvenSpec, assembly: Compound) -> dict[str, float]:
    """Estimate mass from part volumes and the density table. Returns kilograms."""
    by_label: dict[str, float] = {}
    total = 0.0
    for child in assembly.children:
        label = child.label or "part"
        kind = "skin"
        for key in DENSITY:
            if key in label:
                kind = key
                break
        if "blanket" in label:
            kind = "insulation"
        if "handle" in label:
            kind = "handles"
        if "mouth" in label or "skirt" in label or "flue" in label or "throat" in label:
            kind = "skin"
        kilograms = child.volume * 1e-9 * DENSITY[kind]
        by_label[label] = round(kilograms, 3)
        total += kilograms
    by_label["total_kg"] = round(total, 2)
    by_label["published_kg"] = spec.mass_kg
    return by_label
