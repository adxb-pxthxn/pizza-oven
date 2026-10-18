"""Analytical mass and 1D temperatures for the two early Angas variants.

Lengths in millimetres. Mass in kilograms. The cooking geometry is the
Angas 430: circular dome, mouth 420 × 95, apex 165, chamber Ø470, crown
lifting at a cinch above the arch. Insulation is a microporous board
(k = 0.030 W/m·K, 250 kg/m³), one thickness on the wall and the crown
so the outer surface is one surface.

Morning is the wood body. Moondancer is the light shell. Both names are
young dragons because both prototypes are early. Angas stays the baseline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

CHAMBER_D = 470.0
SKIRT_H = 120.0
DOME_RISE = 45.0
MOUTH_W = 420.0
MOUTH_H = 95.0
APEX_H = SKIRT_H + DOME_RISE  # 165

DENS = {
    "ss": 7900.0,
    "al": 2700.0,
    "brass": 8530.0,
    "jarrah": 820.0,
    "blackwood": 640.0,
    "cordierite": 2100.0,
    "micro": 250.0,
    "ptfe": 2200.0,
    "rubber": 1100.0,
}
K = {
    "ss": 16.0,
    "al": 160.0,
    "micro": 0.030,
    "wood": 0.16,
    "ptfe": 0.25,
}
H_IN = 25.0
H_EXT = 10.0
T_GAS = 500.0
T_AMB = 20.0
T_DECK = 430.0
BURNER_KG = 1.85


def ellipse_points(radius: float, rise: float, z0: float, count: int = 48) -> list[tuple[float, float]]:
    points = []
    for index in range(count + 1):
        theta = math.pi / 2 * (1 - index / count)
        points.append((radius * math.cos(theta), z0 + rise * math.sin(theta)))
    return points


def offset_open(points: list[tuple[float, float]], distance: float) -> list[tuple[float, float]]:
    normals = []
    for index, (r, z) in enumerate(points):
        if index == 0:
            dr = points[1][0] - r
            dz = points[1][1] - z
        elif index == len(points) - 1:
            dr = r - points[index - 1][0]
            dz = z - points[index - 1][1]
        else:
            dr = points[index + 1][0] - points[index - 1][0]
            dz = points[index + 1][1] - points[index - 1][1]
        length = math.hypot(dr, dz)
        normals.append((-dz / length, dr / length))
    offset = []
    for (r, z), (nr, nz) in zip(points, normals):
        rr = r + distance * nr
        offset.append((0.0 if rr < 0 else rr, z + distance * nz))
    return offset


def _loop_area_centroid(loop: list[tuple[float, float]]) -> tuple[float, float]:
    twice = 0.0
    moment = 0.0
    for (r0, z0), (r1, z1) in zip(loop, loop[1:]):
        cross = r0 * z1 - r1 * z0
        twice += cross
        moment += (r0 + r1) * cross
    area = twice / 2.0
    if abs(area) < 1e-12:
        return 0.0, 0.0
    r_bar = moment / (6.0 * area)
    return area, r_bar


def revolve_volume_mm3(loop: list[tuple[float, float]]) -> float:
    """Volume of a closed rz loop revolved about Z. Coordinates are millimetres."""
    area, r_bar = _loop_area_centroid(loop)
    return abs(2.0 * math.pi * r_bar * area)


def cylinder_shell_mm3(r_in: float, r_out: float, z0: float, z1: float) -> float:
    return math.pi * (r_out * r_out - r_in * r_in) * (z1 - z0)


def disc_mm3(radius: float, thickness: float) -> float:
    return math.pi * radius * radius * thickness


def kg(volume_mm3: float, density: float) -> float:
    return volume_mm3 * 1e-9 * density


def wall_temperatures(liner_mm: float, ins_mm: float, outer_mm: float, outer_k: float,
                      t_hot: float = T_GAS) -> dict[str, float]:
    """1D wall. Outer layer uses outer_k. Returns flux and the interface temperatures."""
    r_in = 1.0 / H_IN
    r_liner = (liner_mm / 1000.0) / K["ss"]
    r_ins = (ins_mm / 1000.0) / K["micro"]
    r_outer = (outer_mm / 1000.0) / outer_k
    r_ext = 1.0 / H_EXT
    total = r_in + r_liner + r_ins + r_outer + r_ext
    flux = (t_hot - T_AMB) / total
    # Temperatures walking outward. Each drop is flux * R.
    t_liner_in = t_hot - flux * r_in
    t_ins_in = t_liner_in - flux * r_liner
    t_outer_in = t_ins_in - flux * r_ins
    t_outer = t_outer_in - flux * r_outer
    return {
        "R": total,
        "flux": flux,
        "outer_in_C": t_outer_in,
        "outer_C": t_outer,
    }


def underside_temperature(pan_mm: float, ins_mm: float, base_mm: float, base_k: float) -> dict[str, float]:
    """Deck bottom at T_DECK, conducting through the pan, the board, and the base."""
    r_pan = (pan_mm / 1000.0) / K["ss"]
    r_ins = (ins_mm / 1000.0) / K["micro"]
    r_base = (base_mm / 1000.0) / base_k
    r_ext = 1.0 / H_EXT
    total = r_pan + r_ins + r_base + r_ext
    flux = (T_DECK - T_AMB) / total
    return {"R": total, "flux": flux, "under_C": T_AMB + flux * r_ext}


def grip_temperature(skin_c: float, standoff_mm: float, post_d_mm: float = 6.0,
                     grip_od_mm: float = 22.0, grip_len_mm: float = 130.0) -> float:
    """Four stainless posts in series with PTFE washers, jarrah grips cooled by air."""
    n_posts = 4.0
    a_post = math.pi * (post_d_mm / 2000.0) ** 2
    r_post = (standoff_mm / 1000.0) / (K["ss"] * a_post)
    a_ptfe = math.pi * (0.008) ** 2
    r_ptfe = (0.003) / (K["ptfe"] * a_ptfe)
    r_path = (r_post + r_ptfe) / n_posts
    r_grip = grip_od_mm / 2000.0
    length = grip_len_mm / 1000.0
    area = 2.0 * (math.pi * (grip_od_mm / 1000.0) * length + 2.0 * math.pi * r_grip * r_grip)
    r_conv = 1.0 / (H_EXT * area)
    return T_AMB + (skin_c - T_AMB) * r_conv / (r_path + r_conv)


@dataclass(frozen=True)
class Design:
    """Decision variables plus the discrete material choice."""

    name: str
    dragon: str
    skin: str  # "blackwood" or "ss" or "al"
    base: str  # "ss" or "al"
    band: str  # "brass" or "ss"
    liner_t: float
    skin_t: float
    base_t: float
    pan_t: float
    ins_t: float
    floor_ins: float
    stone_t: float
    stone_d: float
    band_t: float
    band_w: float
    standoff: float
    ferrules: bool


def evaluate(design: Design) -> dict:
    """Part masses and temperatures. Ready mass includes the stone and the burner allowance."""
    s = design
    r = CHAMBER_D / 2.0
    stack = s.liner_t + s.ins_t + s.skin_t
    outer_r = r + stack
    hearth = s.base_t + s.floor_ins + s.pan_t + s.stone_t
    spring = hearth + SKIRT_H
    skin_k = K["wood"] if s.skin == "blackwood" else (K["al"] if s.skin == "al" else K["ss"])
    base_k = K["al"] if s.base == "al" else K["ss"]
    skin_rho = DENS[s.skin]
    base_rho = DENS[s.base]
    band_rho = DENS[s.band]

    wall = wall_temperatures(s.liner_t, s.ins_t, s.skin_t, skin_k, T_GAS)
    under = underside_temperature(s.pan_t, s.floor_ins, s.base_t, base_k)
    grip = grip_temperature(wall["outer_C"], s.standoff)

    mouth_area = MOUTH_W * MOUTH_H
    skirt_h = SKIRT_H

    def shell_cyl(r_in: float, thick: float, height: float, density: float, cut_mouth: bool) -> float:
        vol = cylinder_shell_mm3(r_in, r_in + thick, 0.0, height)
        if cut_mouth:
            vol -= mouth_area * thick
        return kg(max(vol, 0.0), density)

    liner_skirt = shell_cyl(r, s.liner_t, skirt_h, DENS["ss"], True)
    ins_skirt = shell_cyl(r + s.liner_t, s.ins_t, skirt_h, DENS["micro"], True)
    skin_skirt = shell_cyl(r + s.liner_t + s.ins_t, s.skin_t, skirt_h, skin_rho, True)

    inner = ellipse_points(r, DOME_RISE, spring)
    liner_outer = offset_open(inner, s.liner_t)
    ins_outer = offset_open(inner, s.liner_t + s.ins_t)
    skin_outer = offset_open(inner, stack)

    def dome_between(a: list[tuple[float, float]], b: list[tuple[float, float]], density: float) -> float:
        loop = list(reversed(a)) + list(b)
        loop.append(loop[0])
        return kg(revolve_volume_mm3(loop), density)

    liner_dome = dome_between(inner, liner_outer, DENS["ss"])
    ins_dome = dome_between(liner_outer, ins_outer, DENS["micro"])
    skin_dome = dome_between(ins_outer, skin_outer, skin_rho)

    base = kg(disc_mm3(outer_r, s.base_t), base_rho)
    # Short lip so the board cannot slide out. 12 mm tall, same gauge as the pan.
    lip = shell_cyl(outer_r - s.base_t, s.base_t, 12.0, base_rho, False)
    floor_ins = kg(disc_mm3(r + s.liner_t, s.floor_ins), DENS["micro"])
    stone_pan = kg(disc_mm3(r, s.pan_t), DENS["ss"])
    stone = kg(disc_mm3(s.stone_d / 2.0, s.stone_t), DENS["cordierite"])

    band_r = outer_r
    band = kg(cylinder_shell_mm3(band_r, band_r + s.band_t, 0.0, s.band_w), band_rho)

    # Mouth face plate, 0.8 mm, 12 mm border, and a throat through the stack.
    frame_t = 0.8
    frame_border = 12.0
    outer_box = (MOUTH_W + 2 * frame_border) * (MOUTH_H + 2 * frame_border)
    inner_box = (MOUTH_W - 4.0) * (MOUTH_H - 4.0)
    frame = kg((outer_box - inner_box) * frame_t, DENS["ss"])
    throat = kg(2.0 * (MOUTH_W + MOUTH_H) * stack * 0.6, DENS["ss"])
    landing = kg(MOUTH_W * 40.0 * s.base_t, base_rho)

    grip_vol = 2.0 * math.pi * (11.0 ** 2) * 130.0
    grips = kg(grip_vol, DENS["jarrah"])
    post_vol = 4.0 * math.pi * (3.0 ** 2) * s.standoff
    posts = kg(post_vol, DENS["ss"])
    washer_vol = 4.0 * math.pi * (8.0 ** 2) * 3.0
    washers = kg(washer_vol, DENS["ptfe"])
    ferrule = kg(4.0 * math.pi * (13.0 ** 2 - 11.0 ** 2) * 8.0, DENS["brass"]) if s.ferrules else 0.0

    if s.skin == "blackwood":
        feet = kg(3.0 * math.pi * (14.0 ** 2) * 12.0, DENS["jarrah"])
        foot_name = "jarrah-feet"
    else:
        feet = kg(3.0 * math.pi * (15.0 ** 2) * 8.0, DENS["rubber"])
        foot_name = "rubber-feet"

    # Rack bosses on the crown, stand bosses on the base. Holes are not subtracted;
    # the extra metal is the interface, and the accessory is not included.
    crown_boss = kg(4.0 * math.pi * (6.0 ** 2) * 6.0, DENS["ss"])
    base_boss = kg(4.0 * math.pi * (7.0 ** 2) * 8.0, DENS["ss"])
    dowels = kg(2.0 * math.pi * (2.5 ** 2) * 14.0, DENS["ss"])

    rows = [
        ("base-pan", s.base, base),
        ("base-lip", s.base, lip),
        ("floor-insulation", "micro", floor_ins),
        ("stone-pan", "ss", stone_pan),
        ("floor-cordierite", "cordierite", stone),
        ("liner-skirt", "ss", liner_skirt),
        ("liner-dome", "ss", liner_dome),
        ("wall-insulation", "micro", ins_skirt),
        ("crown-insulation", "micro", ins_dome),
        ("outer-skirt", s.skin, skin_skirt),
        ("outer-dome", s.skin, skin_dome),
        ("cinch-band", s.band, band),
        ("mouth-frame", "ss", frame),
        ("mouth-throat", "ss", throat),
        ("peel-landing", s.base, landing),
        ("handle-grips", "jarrah", grips),
        ("handle-posts", "ss", posts),
        ("ptfe-washers", "ptfe", washers),
        ("handle-ferrules", "brass", ferrule),
        (foot_name, "jarrah" if s.skin == "blackwood" else "rubber", feet),
        ("rack-bosses", "ss", crown_boss),
        ("stand-bosses", "ss", base_boss),
        ("road-dowels", "ss", dowels),
        ("burner-allowance", "allowance", BURNER_KG),
    ]
    ready = sum(mass for _, _, mass in rows)
    parts = {name: round(mass, 3) for name, _, mass in rows}
    return {
        "ready_kg": ready,
        "stone_kg": stone,
        "parts": parts,
        "wall_outer_C": wall["outer_C"],
        "wall_inner_face_C": wall["outer_in_C"],
        "wall_flux": wall["flux"],
        "under_C": under["under_C"],
        "grip_C": grip,
        "outer_diameter": 2 * outer_r,
        "body_height": spring + DOME_RISE + stack,
        "hearth_z": hearth,
        "spring_z": spring,
        "outer_r": outer_r,
        "stack": stack,
        "pizza_clearance": (s.stone_d - 381.0) / 2.0,
        "mouth_over_apex": MOUTH_H / APEX_H,
    }


def vector_keys() -> tuple[str, ...]:
    return (
        "liner_t", "skin_t", "base_t", "pan_t", "ins_t", "floor_ins",
        "stone_t", "stone_d", "band_t", "band_w", "standoff",
    )
