"""Shared parameters, mass, and heat for the modular stack.

Lengths are millimetres. The cooking origin is the mouth plane on the
deck centreline: +X to the right, +Y into the oven, +Z up, deck top at
Z = 0. Every solid in ``parts()`` is placed from these numbers. The
FreeCAD build must not invent a second set.

The floor is a floating mild-steel plate. There is no cordierite, no
cast part, and no cut stone. Insulation sits under the plate. The plate
is not bolted down, so in-plane growth cannot go into compression, which
is the warp that ruins a clamped pizza steel.

Wood is only the grips, the feet, and the peel rest. The firebox walls
are bare steel and are allowed to be hot. The hood skin is not.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

# Planform. These are the launch and the pizza, so the solver does not move them.
DECK_W = 440.0
DECK_L = 520.0
GUTTER_L = 140.0
MOUTH_W = 424.0
CHEEK = 20.0
SILL_L = 80.0
SOFFIT_Y0 = 110.0
SOFFIT_Y1 = 540.0
PIT_H = 170.0
SIDE_GAP = 12.0
PAD = 25.0
PAD_H = 10.0
BELLY_SKIN_T = 0.8
FOOT_H = 12.0
FOOT_D = 28.0
POST_D = 5.0
GRIP_LEN = 150.0
FERRULE_LEN = 12.0
FERRULE_PRESS = 0.15  # radial, millimetres, the only permitted interference
RACK_BELOW_SOFFIT = 50.0
BURNER_KG = 1.85
BURNER_OD = 42.0
T_DECK = 300.0
T_SOFFIT = 550.0
T_GAS = 500.0
T_AMB = 20.0
T_PIT_GAS = 500.0

DENS = {
    "mild": 7850.0,
    "ss": 7900.0,
    "al": 2700.0,
    "micro": 250.0,
    "jarrah": 820.0,
    "gidgee": 1200.0,
    "ptfe": 2200.0,
    "keepout": 0.0,
}
K = {
    "mild": 45.0,
    "ss": 16.0,
    "al": 160.0,
    "micro": 0.030,
    "air": 0.032,
    "wood": 0.16,
    "ptfe": 0.25,
}
CP = {"mild": 480.0, "ss": 500.0, "al": 900.0, "micro": 1050.0, "jarrah": 1600.0, "gidgee": 1600.0}
ALPHA_MILD = 12.0e-6
E_MILD = 200.0e9
NU = 0.30
H_IN = 25.0
H_FLAME = 35.0
H_EXT = 10.0
SIGMA = 5.670374419e-8
LHV_PROPANE = 46.4e6
BURNER_W = 8000.0

# Aicher: thumb swell, a hollow for the forefinger, bulk for the palm.
# Axial position from the thumb end, radius. Revolved about the grip axis.
GRIP_PROFILE = (
    (0.0, 11.0),
    (12.0, 14.5),
    (26.0, 16.0),
    (42.0, 12.5),
    (58.0, 17.0),
    (95.0, 18.0),
    (122.0, 16.0),
    (140.0, 13.0),
    (150.0, 11.0),
)


def chamber_w() -> float:
    return MOUTH_W + 2.0 * CHEEK


def chamber_l() -> float:
    return DECK_L + GUTTER_L


def mouth_h(front_h: float) -> float:
    """63% of the front crown, so a tall mouth stays a tall crown."""
    return 0.63 * front_h


@dataclass(frozen=True)
class Stack:
    dragon: str
    deck_t: float
    ins_t: float
    floor_ins: float
    belly_ins: float
    liner_t: float
    skin_t: float
    pit_t: float
    front_h: float
    soffit_h: float
    air_gap: float
    standoff: float
    # Arrax: the tall brow is only the launch. The body crown sits on the soffit.
    # Vermax leaves both at the defaults, so its boxes do not move.
    launch_y: float = 110.0
    stepped: bool = False
    # Shrykos folds the step. Arrax and Vermax stay square.
    sloped: bool = False
    # Morghul: the fold is the joint. Brow and tunnel lift separately.
    split: bool = False

    def to_json(self) -> dict:
        return asdict(self)


def _kg(volume_mm3: float, material: str) -> float:
    return volume_mm3 * 1e-9 * DENS[material]


def _box_vol(size: tuple[float, float, float]) -> float:
    return abs(size[0] * size[1] * size[2])


def _tube_vol(r_in: float, r_out: float, length: float) -> float:
    return math.pi * (r_out * r_out - r_in * r_in) * length


def _grip_vol() -> float:
    total = 0.0
    for (x0, r0), (x1, r1) in zip(GRIP_PROFILE, GRIP_PROFILE[1:]):
        length = x1 - x0
        total += math.pi * length / 3.0 * (r0 * r0 + r0 * r1 + r1 * r1)
    return total


def _resist_wall(s: Stack) -> dict[str, float]:
    """Hood wall. Gas at T_GAS, air gap on the cool side of the board."""
    terms = [
        1.0 / H_IN,
        (s.liner_t / 1000.0) / K["mild"],
        (s.ins_t / 1000.0) / K["micro"],
        (s.air_gap / 1000.0) / K["air"],
        (s.skin_t / 1000.0) / K["al"],
        1.0 / H_EXT,
    ]
    total = sum(terms)
    flux = (T_GAS - T_AMB) / total
    t_skin_in = T_AMB + flux * (1.0 / H_EXT + (s.skin_t / 1000.0) / K["al"])
    # Walk from the outside: skin outer, then skin inner.
    t_outer = T_AMB + flux / H_EXT
    return {"R": total, "flux": flux, "outer_C": t_outer, "skin_in_C": t_skin_in}


def _resist_under(s: Stack) -> dict[str, float]:
    """Deck at T_DECK, through the board and the belly, into air."""
    terms = [
        (s.deck_t / 1000.0) / K["mild"],
        (s.floor_ins / 1000.0) / K["micro"],
        (s.pit_t / 1000.0) / K["mild"],
        (s.belly_ins / 1000.0) / K["micro"],
        (BELLY_SKIN_T / 1000.0) / K["al"],
        1.0 / H_EXT,
    ]
    total = sum(terms)
    flux = (T_DECK - T_AMB) / total
    t_under = T_AMB + flux / H_EXT
    return {"R": total, "flux": flux, "under_C": t_under}


def _pit_wall_c(s: Stack) -> float:
    """Bare firebox wall. Inner film is flame, outer film is air."""
    r_in = 1.0 / H_FLAME
    r_steel = (s.pit_t / 1000.0) / K["mild"]
    r_ext = 1.0 / H_EXT
    total = r_in + r_steel + r_ext
    flux = (T_PIT_GAS - T_AMB) / total
    return T_AMB + flux * r_ext


def grip_temperature(root_c: float, standoff_mm: float, n_posts: int = 2) -> float:
    """Wood bar on stainless posts with a PTFE washer under each post."""
    radius = POST_D / 2000.0
    area_post = math.pi * radius * radius
    r_post = (standoff_mm / 1000.0) / (K["ss"] * area_post)
    area_ptfe = math.pi * (0.008 ** 2)
    r_ptfe = 0.003 / (K["ptfe"] * area_ptfe)
    r_path = (r_post + r_ptfe) / float(n_posts)
    # Surface of one grip, from the profile, plus the two ends.
    lateral = 0.0
    for (x0, r0), (x1, r1) in zip(GRIP_PROFILE, GRIP_PROFILE[1:]):
        length = (x1 - x0) / 1000.0
        radius_m = ((r0 + r1) / 2.0) / 1000.0
        lateral += 2.0 * math.pi * radius_m * length
    ends = 2.0 * math.pi * (GRIP_PROFILE[0][1] / 1000.0) ** 2
    r_conv = 1.0 / (H_EXT * (lateral + ends))
    return T_AMB + (root_c - T_AMB) * r_conv / (r_path + r_conv)


def deck_growth_mm(length_mm: float, t_hot: float = T_DECK) -> float:
    return ALPHA_MILD * length_mm * (t_hot - T_AMB)


def deck_bow_mm(s: Stack) -> float:
    """Through-thickness bow of a free plate. The clamped-buckling term is designed out."""
    under = _resist_under(s)
    # Flux through the deck equals the underside flux once the plate has soaked.
    delta_t = under["flux"] * (s.deck_t / 1000.0) / K["mild"]
    span = max(DECK_W, DECK_L) / 1000.0
    thick = s.deck_t / 1000.0
    return ALPHA_MILD * delta_t * span * span / (8.0 * thick) * 1000.0


def deck_sag_mm(s: Stack) -> float:
    """Self-weight of the plate as a beam on the long span. Conservative versus a plate."""
    span = DECK_L / 1000.0
    thick = s.deck_t / 1000.0
    width = DECK_W / 1000.0
    inertia = width * thick ** 3 / 12.0
    load_per_m = DENS["mild"] * thick * width * 9.81
    deflection = 5.0 * load_per_m * span ** 4 / (384.0 * E_MILD * inertia)
    return deflection * 1000.0


def contact_temperature(e_floor: float, t_floor_c: float, e_dough: float = 1259.0, t_dough_c: float = 20.0) -> float:
    t_f = t_floor_c + 273.15
    t_d = t_dough_c + 273.15
    return (e_floor * t_f + e_dough * t_d) / (e_floor + e_dough) - 273.15


def steel_effusivity() -> float:
    return math.sqrt(K["mild"] * DENS["mild"] * CP["mild"])


def _integrate_cool(t0: float, t1: float, loss_per_k: float, capacity: float) -> float:
    """Minutes to fall from t0 to t1. loss_per_k is watts per kelvin, constant."""
    if t0 <= t1 or loss_per_k <= 0.0 or capacity <= 0.0:
        return 0.0
    # dT/dt = -(loss_per_k/capacity) * (T - Tamb). Closed form.
    rate = loss_per_k / capacity
    return math.log((t0 - T_AMB) / (t1 - T_AMB)) / rate / 60.0


def _cool_open_minutes(s: Stack, deck_kg: float) -> float:
    """Door open, burner off. Deck top radiates and convects. Integrate numerically."""
    mass = max(deck_kg, 0.2)
    capacity = mass * CP["mild"]
    area = (DECK_W / 1000.0) * (DECK_L / 1000.0)
    epsilon = 0.8
    temp = T_DECK
    elapsed = 0.0
    step = 2.0
    while temp > 60.0 and elapsed < 6.0 * 3600.0:
        q = epsilon * SIGMA * ((temp + 273.15) ** 4 - (T_AMB + 273.15) ** 4) + H_EXT * (temp - T_AMB)
        temp -= q * area / capacity * step
        elapsed += step
    return elapsed / 60.0


def body_crown(s: Stack) -> float:
    """Height of the liner over the parked pizza. Vermax uses the front crown."""
    if not s.stepped:
        return s.front_h
    return s.soffit_h + 8.0


def soffit_y0(s: Stack) -> float:
    if not s.stepped:
        return SOFFIT_Y0
    if s.sloped:
        return s.launch_y + (s.front_h - body_crown(s))
    return s.launch_y


def _hood_areas(s: Stack) -> dict[str, float]:
    """Inner-surface areas, mm². A stepped hood does not count the empty plenum."""
    cw = chamber_w()
    cl = chamber_l()
    fh = s.front_h
    bh = body_crown(s)
    launch = s.launch_y if s.stepped else cl
    mh = mouth_h(fh)
    top = cw * cl
    side = launch * fh + max(cl - launch, 0.0) * bh
    back = cw * bh
    front_gross = cw * fh
    mouth = MOUTH_W * mh
    front = max(front_gross - mouth, 0.0)
    step = max(fh - bh, 0.0) * (cw - 2.0 * s.liner_t) if s.stepped else 0.0
    y0 = soffit_y0(s)
    soffit = max(SOFFIT_Y1 - y0, 0.0) * (cw - 2.0 * s.liner_t)
    riser = max(bh - s.soffit_h, 0.0) * (cw - 2.0 * s.liner_t)
    return {
        "top": top,
        "side": side,
        "back": back,
        "front": front,
        "mouth": mouth,
        "soffit": soffit,
        "riser": riser,
        "step": step,
        "inner": top + 2.0 * side + back + front + step,
    }


def _part(pid: str, module: str, material: str, zone: str, shape: str, **payload) -> dict:
    item = {
        "id": pid,
        "module": module,
        "material": material,
        "zone": zone,
        "shape": shape,
    }
    item.update(payload)
    return item


def _prism(pid: str, module: str, material: str, zone: str,
           x: float, dx: float, profile: list[list[float]]) -> dict:
    """Polygon in the YZ plane, extruded along +X. Profile is [[y, z], ...]."""
    return _part(pid, module, material, zone, "prism", x=x, dx=dx, profile=profile)


def _slope_plate(pid: str, module: str, material: str, zone: str,
                 x: float, dx: float, y0: float, z_hi: float, y1: float, z_lo: float,
                 start: float, thick: float) -> dict:
    """Plate along the cowl, thickness measured outward (up and back)."""
    run = y1 - y0
    rise = z_hi - z_lo
    length = math.hypot(run, rise)
    if length < 1.0 or thick <= 0.0 or dx <= 0.0:
        raise ValueError(f"bad slope {pid}")
    ny = rise / length
    nz = run / length

    def shift(y: float, z: float, dist: float) -> list[float]:
        return [y + ny * dist, z + nz * dist]

    profile = [
        shift(y0, z_hi, start),
        shift(y1, z_lo, start),
        shift(y1, z_lo, start + thick),
        shift(y0, z_hi, start + thick),
    ]
    return _prism(pid, module, material, zone, x, dx, profile)


def _append_cowl(items: list, s: Stack, pid: str, material: str, zone: str,
                 x: float, dx: float, y0: float, z_hi: float, y1: float, z_lo: float,
                 start: float, thick: float) -> None:
    """One plate, or two plates with a gap at the fold when the hood splits."""
    if not s.split:
        items.append(_slope_plate(pid, "hood", material, zone, x, dx, y0, z_hi, y1, z_lo, start, thick))
        return
    mid_y = (y0 + y1) * 0.5
    mid_z = (z_hi + z_lo) * 0.5
    run = y1 - y0
    rise = z_hi - z_lo
    length = math.hypot(run, rise)
    gap = 2.0
    dy = (run / length) * (gap * 0.5)
    dz = ((z_lo - z_hi) / length) * (gap * 0.5)
    items.append(_slope_plate(
        f"{pid}-upper", "brow", material, zone, x, dx,
        y0, z_hi, mid_y - dy, mid_z - dz, start, thick,
    ))
    items.append(_slope_plate(
        f"{pid}-lower", "tunnel", material, zone, x, dx,
        mid_y + dy, mid_z + dz, y1, z_lo, start, thick,
    ))


def _box(pid: str, module: str, material: str, zone: str, x: float, y: float, z: float,
         dx: float, dy: float, dz: float) -> dict:
    return _part(
        pid, module, material, zone, "box",
        corner=[x, y, z],
        size=[dx, dy, dz],
    )


def _tube(pid: str, module: str, material: str, zone: str, origin: list[float], axis: list[float],
          r_in: float, r_out: float, length: float) -> dict:
    return _part(
        pid, module, material, zone, "tube",
        origin=list(origin),
        axis=axis,
        r_in=r_in,
        r_out=r_out,
        length=length,
    )


def parts(s: Stack) -> list[dict]:
    """Every solid. Boxes are axis-aligned. Tubes and the grip are the exceptions."""
    cw = chamber_w()
    cl = chamber_l()
    mh = mouth_h(s.front_h)
    wall = s.liner_t + s.ins_t + s.air_gap + s.skin_t
    # Pit inner opening is the chamber plan, so the hearth frame lands on a ledge.
    pit_inner_w = cw
    pit_inner_l = cl
    hx0 = -pit_inner_w / 2.0
    # Deck sits inside the chamber with SIDE_GAP to the liner.
    deck_x = -DECK_W / 2.0
    deck_y = (cw - DECK_W) / 2.0 - SIDE_GAP  # placeholder, replaced below
    del deck_y
    # Chamber x from -cw/2 to cw/2. Deck centred, gap is (cw - DECK_W) / 2.
    gap_x = (cw - DECK_W) / 2.0
    if gap_x < SIDE_GAP - 1e-6:
        raise ValueError("planform gap is smaller than SIDE_GAP")
    z_deck = 0.0
    z_pad = -s.deck_t - PAD_H
    z_board = z_pad - s.floor_ins
    # Ledge and pit rim: the board sits on the pit floor only at the front.
    # The pit floor is lower, by the firebox depth under the ledge.
    # z=0 is the deck top. Pit rim is flush with the deck surround, at z=0.
    # Pit inner height PIT_H goes downward from the rim.
    z_rim = 0.0
    z_pit_floor = -PIT_H
    z_belly_top = z_pit_floor - s.pit_t
    z_belly_ins = z_belly_top - s.belly_ins
    z_belly_skin = z_belly_ins - BELLY_SKIN_T
    z_foot = z_belly_skin - FOOT_H

    items: list[dict] = []

    # --- pit ---
    # Floor, four walls, outward top flange, ledge on three sides (rear is the gutter).
    items.append(_box("pit-floor", "pit", "mild", "hot", hx0, 0.0, z_pit_floor, pit_inner_w, pit_inner_l, s.pit_t))
    items.append(_box("pit-wall-port", "pit", "mild", "hot", hx0 - s.pit_t, 0.0, z_pit_floor, s.pit_t, pit_inner_l, PIT_H))
    items.append(_box("pit-wall-starboard", "pit", "mild", "hot", hx0 + pit_inner_w, 0.0, z_pit_floor, s.pit_t, pit_inner_l, PIT_H))
    items.append(_box("pit-wall-front", "pit", "mild", "hot", hx0 - s.pit_t, -s.pit_t, z_pit_floor, pit_inner_w + 2 * s.pit_t, s.pit_t, PIT_H))
    items.append(_box("pit-wall-rear", "pit", "mild", "hot", hx0 - s.pit_t, pit_inner_l, z_pit_floor, pit_inner_w + 2 * s.pit_t, s.pit_t, PIT_H))
    flange_w = 16.0
    items.append(_box("pit-flange", "pit", "mild", "hot", hx0 - s.pit_t - flange_w, -s.pit_t - flange_w, -s.pit_t,
                       pit_inner_w + 2 * s.pit_t + 2 * flange_w, pit_inner_l + 2 * s.pit_t + 2 * flange_w, s.pit_t))
    # The flange above overlaps the wall tops. Build it as four strips instead.
    items.pop()
    z_flange = -s.pit_t
    items.append(_box("pit-flange-port", "pit", "mild", "hot", hx0 - s.pit_t - flange_w, -s.pit_t, z_flange, flange_w, pit_inner_l + 2 * s.pit_t, s.pit_t))
    items.append(_box("pit-flange-starboard", "pit", "mild", "hot", hx0 + pit_inner_w + s.pit_t, -s.pit_t, z_flange, flange_w, pit_inner_l + 2 * s.pit_t, s.pit_t))
    items.append(_box("pit-flange-front", "pit", "mild", "hot", hx0 - s.pit_t, -s.pit_t - flange_w, z_flange, pit_inner_w + 2 * s.pit_t, flange_w, s.pit_t))
    items.append(_box("pit-flange-rear", "pit", "mild", "hot", hx0 - s.pit_t, pit_inner_l + s.pit_t, z_flange, pit_inner_w + 2 * s.pit_t, flange_w, s.pit_t))

    # Ledge the hearth sits on. Rear is open so the flame can rise.
    ledge = 18.0
    z_ledge = -s.deck_t - PAD_H - s.floor_ins - 1.5
    items.append(_box("pit-ledge-port", "pit", "mild", "hot", hx0, 0.0, z_ledge, ledge, DECK_L, 1.5))
    items.append(_box("pit-ledge-starboard", "pit", "mild", "hot", hx0 + pit_inner_w - ledge, 0.0, z_ledge, ledge, DECK_L, 1.5))
    items.append(_box("pit-ledge-front", "pit", "mild", "hot", hx0 + ledge, 0.0, z_ledge, pit_inner_w - 2 * ledge, ledge, 1.5))

    # Belly: insulation and aluminium tray, larger than the pit by the flange.
    belly_x = hx0 - s.pit_t - flange_w
    belly_y = -s.pit_t - flange_w
    belly_dx = pit_inner_w + 2 * s.pit_t + 2 * flange_w
    belly_dy = pit_inner_l + 2 * s.pit_t + 2 * flange_w
    items.append(_box("belly-ins", "pit", "micro", "cool", belly_x, belly_y, z_belly_ins, belly_dx, belly_dy, s.belly_ins))
    items.append(_box("belly-skin", "pit", "al", "cool", belly_x, belly_y, z_belly_skin, belly_dx, belly_dy, BELLY_SKIN_T))

    # Locator pins sit in the side gap, clear of the deck. Slip fit, not a press.
    pin_r = 4.0
    for index, px in enumerate((-120.0, 120.0)):
        items.append(_tube(
            f"locator-pin-{index}", "pit", "ss", "hot",
            [px, -10.0, 0.4], [0, 0, 1], 0.0, pin_r, 8.0,
        ))

    # Burner keepout in the gutter. Mass is the bought allowance, not this volume.
    burner_y = DECK_L + GUTTER_L / 2.0
    burner_z = z_pit_floor + 28.0
    items.append(_tube(
        "burner-keepout", "pit", "keepout", "hot",
        [hx0 + 20.0, burner_y, burner_z], [1, 0, 0],
        0.0, BURNER_OD / 2.0, pit_inner_w - 40.0,
    ))

    if s.stepped:
        # The grate stays in the pit, under the hearth. Lift the hearth off and it is the fire.
        grate_z = z_pit_floor + 90.0
        grate_x0 = hx0 + 28.0
        grate_x1 = hx0 + pit_inner_w - 28.0
        grate_y0 = 70.0
        grate_y1 = DECK_L - 40.0
        items.append(_box(
            "grate-rail-port", "pit", "ss", "hot",
            grate_x0, grate_y0, grate_z, 4.0, grate_y1 - grate_y0, 4.0,
        ))
        items.append(_box(
            "grate-rail-starboard", "pit", "ss", "hot",
            grate_x1 - 4.0, grate_y0, grate_z, 4.0, grate_y1 - grate_y0, 4.0,
        ))
        grate_span = grate_x1 - grate_x0
        for index in range(6):
            gy = grate_y0 + (grate_y1 - grate_y0) * (index + 0.5) / 6.0
            items.append(_tube(
                f"grate-rod-{index}", "pit", "ss", "hot",
                [grate_x0 + 4.4, gy, grate_z + 2.0], [1, 0, 0],
                0.0, 2.0, grate_span - 8.8,
            ))

    # Feet, inboard of the corners, on the belly skin.
    foot_r = FOOT_D / 2.0
    inset = 40.0
    for index, (fx, fy) in enumerate((
        (belly_x + inset, belly_y + inset),
        (belly_x + belly_dx - inset, belly_y + inset),
        (belly_x + inset, belly_y + belly_dy - inset),
        (belly_x + belly_dx - inset, belly_y + belly_dy - inset),
    )):
        items.append(_tube(
            f"foot-{index}", "pit", "jarrah", "cool",
            [fx, fy, z_foot], [0, 0, 1], 0.0, foot_r, FOOT_H,
        ))

    # Carry grips. Bar runs front-to-back so a person at each side can lift.
    # Posts stand off the bare firebox wall. The ferrule is the only press fit.
    grip_z = z_pit_floor + PIT_H * 0.55
    grip_y0 = cl * 0.28
    port_face = hx0 - s.pit_t
    star_face = hx0 + pit_inner_w + s.pit_t
    post_len = s.standoff
    palm_r = 18.0
    for end, sign, face in (("port", -1.0, port_face), ("starboard", 1.0, star_face)):
        axis_x = face + sign * (post_len + 3.4 + palm_r)
        for step, axial in enumerate((70.0, 110.0)):
            post_x = face if sign > 0 else face - post_len
            items.append(_tube(
                f"post-{end}-{step}", "pit", "ss", "hot",
                [post_x, grip_y0 + axial, grip_z],
                [1, 0, 0], 0.0, POST_D / 2.0, post_len,
            ))
            washer_x = face + sign * post_len if sign > 0 else face - post_len - 3.2
            items.append(_tube(
                f"washer-{end}-{step}", "pit", "ptfe", "cool",
                [washer_x, grip_y0 + axial, grip_z],
                [1, 0, 0], 0.0, 8.0, 3.0,
            ))
        items.append(_part(
            f"grip-{end}", "pit", "jarrah", "cool", "revolve",
            origin=[axis_x, grip_y0, grip_z],
            axis=[0, 1, 0],
            profile=[list(pair) for pair in GRIP_PROFILE],
        ))
        items.append(_tube(
            f"ferrule-{end}", "pit", "ss", "cool",
            [axis_x, grip_y0, grip_z],
            [0, 1, 0],
            GRIP_PROFILE[0][1] - FERRULE_PRESS,
            GRIP_PROFILE[0][1] + 3.0,
            FERRULE_LEN,
        ))

    # Gidgee peel rest, below and in front of the steel sill, clear of the flame.
    rest_y = -s.pit_t - flange_w - SILL_L - 8.0
    items.append(_box(
        "peel-rest", "pit", "gidgee", "cool",
        -90.0, rest_y - 20.0, -48.0, 180.0, 20.0, 16.0,
    ))

    # --- hearth ---
    # Board fills the plan under the deck, sitting on the ledges with 0.4 mm vertical clearance.
    board_x = deck_x - 4.0
    board_y = 4.0
    board_dx = DECK_W + 8.0
    board_dy = DECK_L - 8.0
    items.append(_box("hearth-board", "hearth", "micro", "cool", board_x, board_y, z_board, board_dx, board_dy, s.floor_ins))
    # Three pads. Triangle: two front, one rear centre. On the board, 0.2 mm above it.
    pad_z = z_board + s.floor_ins + 0.2
    pads = (
        (deck_x + 36.0, 36.0),
        (deck_x + DECK_W - 36.0 - PAD, 36.0),
        (deck_x + DECK_W / 2.0 - PAD / 2.0, DECK_L - 36.0 - PAD),
    )
    for index, (px, py) in enumerate(pads):
        items.append(_box(f"pad-{index}", "hearth", "micro", "cool", px, py, pad_z, PAD, PAD, PAD_H - 0.2))
    # Deck, 0.2 mm above the pads. Centred in X. Front edge inset from the mouth by the growth gap.
    rear_gap = max(4.0, deck_growth_mm(DECK_L) + 2.0)
    deck_y0 = 6.0
    items.append(_box("deck", "hearth", "mild", "hot", deck_x, deck_y0, -s.deck_t, DECK_W, DECK_L - rear_gap, s.deck_t))
    # Keepers: three clips above the deck edge, 2 mm clear, so the plate cannot hop out.
    clip_z = 2.0
    items.append(_box("keeper-front", "hearth", "mild", "hot", deck_x + 40.0, deck_y0 + 4.0, clip_z, 50.0, 8.0, 3.0))
    items.append(_box("keeper-port", "hearth", "mild", "hot", deck_x - 8.0, 80.0, clip_z, 6.0, 40.0, 3.0))
    items.append(_box("keeper-starboard", "hearth", "mild", "hot", deck_x + DECK_W + 2.0, 80.0, clip_z, 6.0, 40.0, 3.0))
    # Frame rails around the deck, 1.2 mm, leaving the gap. They sit on the ledge.
    rail_t = 1.2
    items.append(_box("rail-port", "hearth", "mild", "hot", deck_x - gap_x, 0.0, -s.deck_t, rail_t, DECK_L, s.deck_t))
    items.append(_box("rail-starboard", "hearth", "mild", "hot", deck_x + DECK_W + gap_x - rail_t, 0.0, -s.deck_t, rail_t, DECK_L, s.deck_t))
    items.append(_box("rail-front", "hearth", "mild", "hot", deck_x, 0.0, -s.deck_t, DECK_W, rail_t, s.deck_t))

    # Sill, steel, in front of the flange. The peel lands here. Wood stays further out.
    sill_y1 = -s.pit_t - flange_w - 0.6
    items.append(_box("sill", "hearth", "mild", "hot", -MOUTH_W / 2.0, sill_y1 - SILL_L, -s.deck_t, MOUTH_W, SILL_L, s.deck_t))

    # --- hood ---
    # Liner plates. Front is two cheeks and a lintel, so the mouth is a real opening.
    # Vermax is one crown. Arrax keeps that crown only for the launch, then drops
    # to a body crown 8 mm above the soffit so the outside is the ceiling that cooks.
    z_top = s.front_h
    seam = 0.4
    t = s.liner_t
    bh = body_crown(s)
    launch = s.launch_y if s.stepped else cl
    # A 45° fold runs as far as it rises. The square step is the Arrax case.
    y1 = launch + (s.front_h - bh) if s.sloped else launch
    if s.stepped:
        items.append(_box("liner-top-brow", "hood", "mild", "hot", hx0, 0.0, z_top, cw, launch - seam, t))
        liner_body_y = y1 + seam
        if s.sloped:
            slope_len = math.hypot(y1 - launch, s.front_h - bh)
            liner_body_y = y1 + ((s.front_h - bh) / slope_len) * t + seam
        items.append(_box("liner-top-body", "hood", "mild", "hot", hx0, liner_body_y, bh, cw, cl - liner_body_y, t))
        if s.sloped:
            _append_cowl(items, s, "liner-cowl", "mild", "hot", hx0, cw, launch, z_top, y1, bh, 0.0, t)
        else:
            items.append(_box(
                "liner-step", "hood", "mild", "hot",
                hx0 + t + seam, launch - t, bh + t, cw - 2.0 * t - 2.0 * seam, t, z_top - bh - t,
            ))
        brow_len = launch - t - 2.0 * seam
        body_y = y1 + t + seam
        body_len = cl - t - seam - body_y
        items.append(_box("liner-port-brow", "hood", "mild", "hot", hx0, t + seam, 0.0, t, brow_len, s.front_h))
        items.append(_box("liner-port-body", "hood", "mild", "hot", hx0, body_y, 0.0, t, body_len, bh))
        items.append(_box("liner-starboard-brow", "hood", "mild", "hot", hx0 + cw - t, t + seam, 0.0, t, brow_len, s.front_h))
        items.append(_box("liner-starboard-body", "hood", "mild", "hot", hx0 + cw - t, body_y, 0.0, t, body_len, bh))
        items.append(_box("liner-rear", "hood", "mild", "hot", hx0, cl - t, 0.0, cw, t, bh))
        if s.sloped:
            for side, xside in (("port", hx0), ("starboard", hx0 + cw - t)):
                if s.split:
                    mid_y = (launch + y1) * 0.5
                    def _z_at(y_pos: float) -> float:
                        return s.front_h + (bh - s.front_h) * (y_pos - launch) / (y1 - launch)
                    cut_u = mid_y - 1.0
                    cut_l = mid_y + 1.0
                    items.append(_prism(
                        f"liner-{side}-cowl-upper", "brow", "mild", "hot", xside, t,
                        [[launch, 0.0], [cut_u, 0.0], [cut_u, _z_at(cut_u)], [launch, s.front_h]],
                    ))
                    items.append(_prism(
                        f"liner-{side}-cowl-lower", "tunnel", "mild", "hot", xside, t,
                        [[cut_l, 0.0], [y1, 0.0], [y1, bh], [cut_l, _z_at(cut_l)]],
                    ))
                else:
                    items.append(_prism(
                        f"liner-{side}-cowl", "hood", "mild", "hot", xside, t,
                        [[launch, 0.0], [y1, 0.0], [y1, bh], [launch, s.front_h]],
                    ))
    else:
        items.append(_box("liner-top", "hood", "mild", "hot", hx0, 0.0, z_top, cw, cl, t))
        items.append(_box("liner-port", "hood", "mild", "hot", hx0, t + seam, 0.0, t, cl - 2.0 * t - 2.0 * seam, s.front_h))
        items.append(_box("liner-starboard", "hood", "mild", "hot", hx0 + cw - t, t + seam, 0.0, t, cl - 2.0 * t - 2.0 * seam, s.front_h))
        items.append(_box("liner-rear", "hood", "mild", "hot", hx0, cl - t, 0.0, cw, t, s.front_h))
    items.append(_box("liner-cheek-port", "hood", "mild", "hot", hx0, 0.0, 0.0, CHEEK, t, mh))
    items.append(_box("liner-cheek-starboard", "hood", "mild", "hot", hx0 + cw - CHEEK, 0.0, 0.0, CHEEK, t, mh))
    items.append(_box("liner-lintel", "hood", "mild", "hot", hx0, 0.0, mh + seam, cw, t, s.front_h - mh - seam))
    # Soffit and its riser. The riser is the step you see through the mouth.
    soffit_x = hx0 + t + 2.0
    soffit_w = cw - 2.0 * t - 4.0
    y0 = soffit_y0(s)
    riser_h = bh - s.soffit_h - 0.4
    items.append(_box("soffit", "hood", "mild", "hot", soffit_x, y0, s.soffit_h, soffit_w, SOFFIT_Y1 - y0, 1.2))
    items.append(_box(
        "soffit-riser", "hood", "mild", "hot",
        soffit_x, y0 - 1.5, s.soffit_h, soffit_w, 1.5, riser_h,
    ))
    # Broiler rods under the soffit, over the rear half of the deck.
    rod_z = s.soffit_h - RACK_BELOW_SOFFIT
    rod_y0 = max(y0, 200.0)
    rod_y1 = min(DECK_L - 10.0, SOFFIT_Y1)
    rod_x0 = soffit_x + 8.0
    rod_x1 = soffit_x + soffit_w - 8.0
    items.append(_box("rack-rail-port", "hood", "ss", "hot", rod_x0, rod_y0, rod_z, 4.0, rod_y1 - rod_y0, 4.0))
    items.append(_box("rack-rail-starboard", "hood", "ss", "hot", rod_x1 - 4.0, rod_y0, rod_z, 4.0, rod_y1 - rod_y0, 4.0))
    rod_span = rod_x1 - rod_x0
    n_rods = 8
    for index in range(n_rods):
        y = rod_y0 + (rod_y1 - rod_y0) * (index + 0.5) / n_rods
        items.append(_tube(
            f"rack-rod-{index}", "hood", "ss", "hot",
            [rod_x0 + 4.4, y, rod_z + 2.0], [1, 0, 0],
            0.0, 2.0, rod_span - 8.8,
        ))

    # Insulation and aluminium skin, outside the liner, air gap between board and skin.
    # The mouth is left open by stopping the front board and skin at the lintel and the cheeks.
    # A stepped hood repeats the stack on the brow and on the lower body, with a board on the step.
    ins_x = hx0 - s.ins_t
    ins_y = -s.ins_t
    del ins_y
    ins_z = s.front_h + s.liner_t
    body_ins_z = bh + s.liner_t
    skin_off = s.ins_t + s.air_gap
    skin_x = hx0 - skin_off
    brow_skin_z = ins_z + s.ins_t + s.air_gap
    body_skin_z = body_ins_z + s.ins_t + s.air_gap
    if s.stepped:
        body_y_shell = y1 if s.sloped else launch
        if s.sloped:
            slope_len = math.hypot(y1 - launch, s.front_h - bh)
            ny = (s.front_h - bh) / slope_len
        else:
            ny = 0.0
        items.append(_box("ins-top-brow", "hood", "micro", "cool", ins_x, 0.0, ins_z, cw + 2 * s.ins_t, launch, s.ins_t))
        ins_body_y = body_y_shell + (ny * (t + s.ins_t) + seam if s.sloped else 0.0)
        items.append(_box("ins-top-body", "hood", "micro", "cool", ins_x, ins_body_y, body_ins_z, cw + 2 * s.ins_t, cl + s.ins_t - ins_body_y, s.ins_t))
        items.append(_box("ins-port-brow", "hood", "micro", "cool", ins_x, 0.0, 0.0, s.ins_t, launch, s.front_h + s.liner_t))
        items.append(_box("ins-port-body", "hood", "micro", "cool", ins_x, ins_body_y, 0.0, s.ins_t, cl - ins_body_y, bh + s.liner_t))
        items.append(_box("ins-starboard-brow", "hood", "micro", "cool", hx0 + cw, 0.0, 0.0, s.ins_t, launch, s.front_h + s.liner_t))
        items.append(_box("ins-starboard-body", "hood", "micro", "cool", hx0 + cw, ins_body_y, 0.0, s.ins_t, cl - ins_body_y, bh + s.liner_t))
        items.append(_box("ins-rear", "hood", "micro", "cool", ins_x, cl, 0.0, cw + 2 * s.ins_t, s.ins_t, bh + s.liner_t))
        brow_skin_dy = launch if s.sloped else launch + skin_off
        body_skin_y = (y1 + ny * (t + s.ins_t + s.air_gap + s.skin_t) + seam) if s.sloped else (launch + skin_off)
        items.append(_box("skin-top-brow", "hood", "al", "cool", skin_x, 0.0, brow_skin_z, cw + 2 * skin_off, brow_skin_dy, s.skin_t))
        items.append(_box("skin-top-body", "hood", "al", "cool", skin_x, body_skin_y, body_skin_z, cw + 2 * skin_off, cl + skin_off - body_skin_y, s.skin_t))
        items.append(_box("skin-port-brow", "hood", "al", "cool", skin_x, 0.0, 0.0, s.skin_t, launch, s.front_h + s.liner_t + s.ins_t + s.air_gap))
        skin_side_y = body_skin_y if s.sloped else body_y_shell
        items.append(_box("skin-port-body", "hood", "al", "cool", skin_x, skin_side_y, 0.0, s.skin_t, cl - skin_side_y, bh + s.liner_t + s.ins_t + s.air_gap))
        items.append(_box("skin-starboard-brow", "hood", "al", "cool", hx0 + cw + skin_off - s.skin_t, 0.0, 0.0, s.skin_t, launch, s.front_h + s.liner_t + s.ins_t + s.air_gap))
        items.append(_box("skin-starboard-body", "hood", "al", "cool", hx0 + cw + skin_off - s.skin_t, skin_side_y, 0.0, s.skin_t, cl - skin_side_y, bh + s.liner_t + s.ins_t + s.air_gap))
        items.append(_box("skin-rear", "hood", "al", "cool", skin_x, cl + skin_off - s.skin_t, 0.0, cw + 2 * skin_off, s.skin_t, bh + s.liner_t + s.ins_t + s.air_gap))
        if s.sloped:
            _append_cowl(
                items, s, "ins-cowl", "micro", "cool",
                ins_x, cw + 2.0 * s.ins_t,
                launch, z_top, y1, bh, t, s.ins_t,
            )
            _append_cowl(
                items, s, "skin-cowl", "al", "cool",
                skin_x, cw + 2.0 * skin_off,
                launch, z_top, y1, bh, t + s.ins_t + s.air_gap, s.skin_t,
            )
        else:
            step_ins_h = s.front_h - bh - s.ins_t
            items.append(_box("ins-step", "hood", "micro", "cool", ins_x, launch, body_ins_z + s.ins_t, cw + 2 * s.ins_t, s.ins_t, step_ins_h))
            items.append(_box(
                "skin-step", "hood", "al", "cool",
                skin_x, launch + skin_off, body_skin_z + s.skin_t,
                cw + 2 * skin_off, s.skin_t, s.front_h - bh - s.skin_t,
            ))
    else:
        items.append(_box("ins-top", "hood", "micro", "cool", ins_x, 0.0, ins_z, cw + 2 * s.ins_t, cl + s.ins_t, s.ins_t))
        items.append(_box("ins-port", "hood", "micro", "cool", ins_x, 0.0, 0.0, s.ins_t, cl, s.front_h + s.liner_t))
        items.append(_box("ins-starboard", "hood", "micro", "cool", hx0 + cw, 0.0, 0.0, s.ins_t, cl, s.front_h + s.liner_t))
        items.append(_box("ins-rear", "hood", "micro", "cool", ins_x, cl, 0.0, cw + 2 * s.ins_t, s.ins_t, s.front_h + s.liner_t))
        items.append(_box("skin-top", "hood", "al", "cool", skin_x, 0.0, brow_skin_z, cw + 2 * skin_off, cl + skin_off, s.skin_t))
        items.append(_box("skin-port", "hood", "al", "cool", skin_x, 0.0, 0.0, s.skin_t, cl, s.front_h + s.liner_t + s.ins_t + s.air_gap))
        items.append(_box("skin-starboard", "hood", "al", "cool", hx0 + cw + skin_off - s.skin_t, 0.0, 0.0, s.skin_t, cl, s.front_h + s.liner_t + s.ins_t + s.air_gap))
        items.append(_box("skin-rear", "hood", "al", "cool", skin_x, cl + skin_off - s.skin_t, 0.0, cw + 2 * skin_off, s.skin_t, s.front_h + s.liner_t + s.ins_t + s.air_gap))
    items.append(_box("ins-lintel", "hood", "micro", "cool", ins_x, -s.ins_t, mh, cw + 2 * s.ins_t, s.ins_t, s.front_h - mh + s.liner_t))
    items.append(_box("ins-cheek-port", "hood", "micro", "cool", ins_x, -s.ins_t, 0.0, s.ins_t + CHEEK, s.ins_t, mh))
    items.append(_box("ins-cheek-starboard", "hood", "micro", "cool", hx0 + cw - CHEEK, -s.ins_t, 0.0, s.ins_t + CHEEK, s.ins_t, mh))
    items.append(_box("skin-lintel", "hood", "al", "cool", skin_x, -skin_off, mh, cw + 2 * skin_off, s.skin_t, s.front_h - mh + s.liner_t + s.ins_t + s.air_gap))

    # Door, closed, in front of the cheek insulation so the hinge leaf is in free air.
    door_t_ins = 16.0
    door_x = hx0 + CHEEK + 1.5
    door_w = MOUTH_W - 3.0
    door_h = mh - 3.0
    door_back = -(skin_off + 1.0)
    items.append(_box("door-inner", "hood", "mild", "hot", door_x, door_back - 1.2, 1.5, door_w, 1.2, door_h))
    items.append(_box("door-ins", "hood", "micro", "cool", door_x, door_back - 1.2 - door_t_ins, 1.5, door_w, door_t_ins, door_h))
    items.append(_box("door-skin", "hood", "al", "cool", door_x, door_back - 1.2 - door_t_ins - 0.8, 1.5, door_w, 0.8, door_h))
    door_front = door_back - 1.2 - door_t_ins - 0.8
    items.append(_tube(
        "hinge-pin", "hood", "ss", "cool",
        [door_x + 8.0, door_front - 8.0, 10.0], [0, 0, 1],
        0.0, 3.0, door_h - 16.0,
    ))

    # Flue, front top, in the eyebrow. Four walls and a parked damper.
    flue_w = 120.0
    flue_d = 36.0
    flue_h = 70.0
    flue_x = -flue_w / 2.0
    flue_y = -skin_off
    flue_z = s.front_h + s.liner_t + s.ins_t + s.air_gap + s.skin_t
    ft = 1.0
    items.append(_box("flue-port", "hood", "mild", "hot", flue_x, flue_y, flue_z, ft, flue_d, flue_h))
    items.append(_box("flue-starboard", "hood", "mild", "hot", flue_x + flue_w - ft, flue_y, flue_z, ft, flue_d, flue_h))
    items.append(_box("flue-front", "hood", "mild", "hot", flue_x + ft + 0.4, flue_y, flue_z, flue_w - 2 * ft - 0.8, ft, flue_h))
    items.append(_box("flue-rear", "hood", "mild", "hot", flue_x + ft + 0.4, flue_y + flue_d - ft, flue_z, flue_w - 2 * ft - 0.8, ft, flue_h))
    items.append(_box("damper", "hood", "mild", "hot", flue_x + flue_w + 4.0, flue_y, flue_z + 10.0, 1.5, flue_d, flue_h - 20.0))

    # Hood lift grip, on the cool top skin. On a stepped hood it sits on the low body.
    hood_post = 16.0
    # Behind the step, with the palm radius clear of the vertical skin.
    grip_clear = (y1 if s.sloped else launch) + s.ins_t + s.air_gap + 18.0 + 16.0
    grip_y = grip_clear if s.stepped else cl * 0.45
    grip_crown = bh if s.stepped else s.front_h
    skin_top_z = grip_crown + s.liner_t + s.ins_t + s.air_gap + s.skin_t
    hood_axis_z = skin_top_z + hood_post + 0.4 + 18.0
    for step, xoff in enumerate((-40.0, 40.0)):
        items.append(_tube(
            f"post-hood-{step}", "hood", "ss", "cool",
            [xoff, grip_y, skin_top_z], [0, 0, 1],
            0.0, POST_D / 2.0, hood_post,
        ))
    items.append(_part(
        "grip-hood", "hood", "jarrah", "cool", "revolve",
        origin=[-GRIP_LEN / 2.0, grip_y, hood_axis_z],
        axis=[1, 0, 0],
        profile=[list(pair) for pair in GRIP_PROFILE],
    ))
    items.append(_tube(
        "ferrule-hood", "hood", "ss", "cool",
        [-GRIP_LEN / 2.0, grip_y, hood_axis_z],
        [1, 0, 0],
        GRIP_PROFILE[0][1] - FERRULE_PRESS,
        GRIP_PROFILE[0][1] + 3.0,
        FERRULE_LEN,
    ))

    # Skirt: four aluminium plates that drop over the pit flange with 2 mm clearance.
    # They belong to the hood and stop 2 mm above the flange and 2 mm outside the pit wall.
    skirt_h = 24.0
    skirt_gap = 2.0
    skirt_t = 1.2
    skirt_z = -skirt_h - skirt_gap
    if s.split:
        cut = (launch + y1) * 0.5
        for side, xside in (("port", port_face - skirt_gap - skirt_t), ("starboard", star_face + skirt_gap)):
            items.append(_box(f"skirt-{side}-brow", "brow", "al", "cool", xside, 8.0, skirt_z, skirt_t, cut - 1.0 - 8.0, skirt_h))
            items.append(_box(f"skirt-{side}-tunnel", "tunnel", "al", "cool", xside, cut + 1.0, skirt_z, skirt_t, (8.0 + cl - 16.0) - (cut + 1.0), skirt_h))
    else:
        items.append(_box("skirt-port", "hood", "al", "cool", port_face - skirt_gap - skirt_t, 8.0, skirt_z, skirt_t, cl - 16.0, skirt_h))
        items.append(_box("skirt-starboard", "hood", "al", "cool", star_face + skirt_gap, 8.0, skirt_z, skirt_t, cl - 16.0, skirt_h))
    front_skirt_z = -s.deck_t - 0.8 - skirt_h
    items.append(_box(
        "skirt-front", "hood", "al", "cool",
        hx0 + 8.0, -s.pit_t - flange_w - skirt_gap - skirt_t,
        front_skirt_z, cw - 16.0, skirt_t, skirt_h,
    ))
    items.append(_box("skirt-rear", "hood", "al", "cool", hx0 + 8.0, cl + s.pit_t + flange_w + skirt_gap, skirt_z, cw - 16.0, skirt_t, skirt_h))

    # Latches on the side walls, below the flange and below the hood insulation.
    items.append(_box("latch-port", "pit", "mild", "hot", port_face - 16.0, cl * 0.55, -52.0, 8.0, 18.0, 12.0))
    items.append(_box("latch-starboard", "pit", "mild", "hot", star_face + 8.0, cl * 0.55, -52.0, 8.0, 18.0, 12.0))

    if s.split:
        brow_names = ("brow", "door", "flue", "damper", "hinge", "lintel", "cheek", "skirt-front")
        for item in items:
            if item["module"] != "hood":
                continue
            pid = item["id"]
            item["module"] = "brow" if any(token in pid for token in brow_names) else "tunnel"

    return items


PRESS_FITS = (
    ("ferrule-port", "grip-port"),
    ("ferrule-starboard", "grip-starboard"),
    ("ferrule-hood", "grip-hood"),
)


def part_volume_mm3(part: dict) -> float:
    shape = part["shape"]
    if shape == "box":
        return _box_vol(tuple(part["size"]))
    if shape == "tube":
        return _tube_vol(part["r_in"], part["r_out"], part["length"])
    if shape == "revolve":
        return _grip_vol()
    if shape == "prism":
        return _poly_area(part["profile"]) * abs(float(part["dx"]))
    raise KeyError(shape)


def _poly_area(profile: list) -> float:
    area = 0.0
    pts = [(float(y), float(z)) for y, z in profile]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:] + pts[:1]):
        area += y0 * z1 - y1 * z0
    return abs(area) * 0.5


def part_mass_kg(part: dict) -> float:
    if part["material"] == "keepout":
        return 0.0
    return _kg(part_volume_mm3(part), part["material"])


def _aabb(part: dict) -> tuple[float, float, float, float, float, float] | None:
    if part["shape"] == "box":
        x, y, z = part["corner"]
        dx, dy, dz = part["size"]
        return x, y, z, x + dx, y + dy, z + dz
    if part["shape"] == "tube":
        ox, oy, oz = part["origin"]
        r = part["r_out"]
        length = part["length"]
        axis = part["axis"]
        if axis == [1, 0, 0]:
            return ox, oy - r, oz - r, ox + length, oy + r, oz + r
        if axis == [0, 1, 0]:
            return ox - r, oy, oz - r, ox + r, oy + length, oz + r
        if axis == [0, 0, 1]:
            return ox - r, oy - r, oz, ox + r, oy + r, oz + length
        return None
    if part["shape"] == "revolve":
        ox, oy, oz = part["origin"]
        r = max(radius for _, radius in part["profile"])
        length = part["profile"][-1][0]
        axis = part.get("axis", [1, 0, 0])
        if axis == [0, 1, 0]:
            return ox - r, oy, oz - r, ox + r, oy + length, oz + r
        return ox, oy - r, oz - r, ox + length, oy + r, oz + r
    if part["shape"] == "prism":
        ys = [float(p[0]) for p in part["profile"]]
        zs = [float(p[1]) for p in part["profile"]]
        x = float(part["x"])
        return x, min(ys), min(zs), x + float(part["dx"]), max(ys), max(zs)
    return None


def _overlap(a: tuple[float, ...], b: tuple[float, ...], pad: float = 0.05) -> bool:
    return not (
        a[3] <= b[0] + pad or b[3] <= a[0] + pad
        or a[4] <= b[1] + pad or b[4] <= a[1] + pad
        or a[5] <= b[2] + pad or b[5] <= a[2] + pad
    )


def _yz_polygon(part: dict) -> list[tuple[float, float]] | None:
    if part["shape"] == "prism":
        return [(float(y), float(z)) for y, z in part["profile"]]
    if part["shape"] == "box":
        _x, y, z = part["corner"]
        _dx, dy, dz = part["size"]
        return [(y, z), (y + dy, z), (y + dy, z + dz), (y, z + dz)]
    return None


def _x_interval(part: dict) -> tuple[float, float] | None:
    box = _aabb(part)
    if box is None:
        return None
    return box[0], box[3]


def _polygons_overlap(poly_a: list[tuple[float, float]], poly_b: list[tuple[float, float]], pad: float = 0.05) -> bool:
    """Separating-axis test for two convex YZ polygons. The pad ignores a seat face."""
    def axes(poly: list[tuple[float, float]]) -> list[tuple[float, float]]:
        found = []
        for (y0, z0), (y1, z1) in zip(poly, poly[1:] + poly[:1]):
            found.append((-(z1 - z0), y1 - y0))
        return found

    def project(poly: list[tuple[float, float]], axis: tuple[float, float]) -> tuple[float, float]:
        vals = [y * axis[0] + z * axis[1] for y, z in poly]
        return min(vals), max(vals)

    for axis in axes(poly_a) + axes(poly_b):
        if abs(axis[0]) + abs(axis[1]) < 1e-9:
            continue
        a0, a1 = project(poly_a, axis)
        b0, b1 = project(poly_b, axis)
        if a1 <= b0 + pad or b1 <= a0 + pad:
            return False
    return True


def aabb_collisions(items: list[dict]) -> list[tuple[str, str]]:
    """Overlaps. Boxes use their bounds. A folded plate uses the real polygon, so a
    parallel cowl is not a hit just because the bounds cross. Press fits are excluded.
    """
    allowed = {frozenset(pair) for pair in PRESS_FITS}
    solids = []
    for part in items:
        box = _aabb(part)
        if box is not None:
            solids.append(part)
    hits = []
    for i, part_a in enumerate(solids):
        box_a = _aabb(part_a)
        poly_a = _yz_polygon(part_a)
        span_a = _x_interval(part_a)
        for part_b in solids[i + 1:]:
            pair = frozenset((part_a["id"], part_b["id"]))
            if pair in allowed:
                continue
            box_b = _aabb(part_b)
            if not _overlap(box_a, box_b):
                continue
            poly_b = _yz_polygon(part_b)
            span_b = _x_interval(part_b)
            if poly_a is not None and poly_b is not None and span_a is not None and span_b is not None:
                if span_a[1] <= span_b[0] + 0.05 or span_b[1] <= span_a[0] + 0.05:
                    continue
                if not _polygons_overlap(poly_a, poly_b):
                    continue
            hits.append((part_a["id"], part_b["id"]))
    return hits


def evaluate(s: Stack) -> dict:
    items = parts(s)
    rows = []
    modules = {"pit": 0.0, "hearth": 0.0, "hood": 0.0, "brow": 0.0, "tunnel": 0.0}
    for part in items:
        mass = part_mass_kg(part)
        rows.append((part["id"], part["module"], part["material"], mass))
        modules[part["module"]] += mass
    modules["pit"] += BURNER_KG
    ready = sum(modules.values())
    wall = _resist_wall(s)
    under = _resist_under(s)
    pit_wall = _pit_wall_c(s)
    grip_pit = grip_temperature(pit_wall, s.standoff, n_posts=2)
    grip_hood = grip_temperature(wall["outer_C"], 18.0, n_posts=2)
    bow = deck_bow_mm(s)
    sag = deck_sag_mm(s)
    growth = deck_growth_mm(DECK_L)
    deck_kg = sum(mass for pid, _, _, mass in rows if pid == "deck")
    bread_kg = sum(
        mass for pid, _mod, mat, mass in rows
        if mat in ("mild", "ss") and (
            pid == "deck" or pid.startswith("liner") or pid.startswith("soffit") or pid == "door-inner"
        )
    )
    areas = _hood_areas(s)
    area_m2 = areas["inner"] * 1e-6
    loss_per_k = area_m2 / wall["R"]
    capacity = max(bread_kg, 0.5) * CP["mild"]
    bread_min = _integrate_cool(240.0, 180.0, loss_per_k, capacity)
    pack_shut_min = _integrate_cool(T_DECK, 60.0, loss_per_k, capacity)
    pack_open_min = _cool_open_minutes(s, deck_kg)
    # Heat-up. Storage to the operating point, exhaust leaving at 280°C mean.
    soffit_kg = sum(mass for pid, _, _, mass in rows if pid.startswith("soffit"))
    liner_kg = sum(mass for pid, _, _, mass in rows if pid.startswith("liner"))
    ins_kg = sum(mass for _pid, _mod, mat, mass in rows if mat == "micro")
    storage_j = (
        deck_kg * CP["mild"] * (T_DECK - T_AMB)
        + soffit_kg * CP["mild"] * (T_SOFFIT - T_AMB)
        + liner_kg * CP["mild"] * (450.0 - T_AMB)
        + ins_kg * CP["micro"] * 0.5 * (250.0 - T_AMB)
    )
    # Open mouth, about 100% excess air, exhaust averaging 350°C, 85% combustion.
    fuel_kg_s = BURNER_W / LHV_PROPANE
    exhaust_kg_s = fuel_kg_s * 32.0
    q_exhaust = exhaust_kg_s * 1200.0 * (350.0 - T_AMB)
    q_walls = wall["flux"] * area_m2 * 0.5
    useful = max(0.85 * BURNER_W - q_exhaust - q_walls, 500.0)
    heatup_min = (storage_j / useful) / 60.0
    e_steel = steel_effusivity()
    # Cordierite reference: k 2.2, rho 2100, cp 950, at 450°C. Comparison only.
    e_cord = math.sqrt(2.2 * 2100.0 * 950.0)
    view = 0.65
    q_steak = 0.85 * SIGMA * ((T_SOFFIT + 273.15) ** 4 - (100.0 + 273.15) ** 4) * view
    collisions = aabb_collisions(items)
    mh = mouth_h(s.front_h)
    return {
        "dragon": s.dragon,
        "ready_kg": round(ready, 3),
        "modules_kg": {key: round(value, 3) for key, value in modules.items()},
        "deck_kg": round(deck_kg, 3),
        "parts": {pid: round(mass, 3) for pid, _, _, mass in rows},
        "skin_C": round(wall["outer_C"], 2),
        "under_C": round(under["under_C"], 2),
        "pit_wall_C": round(pit_wall, 2),
        "grip_pit_C": round(grip_pit, 2),
        "grip_hood_C": round(grip_hood, 2),
        "bow_mm": round(bow, 4),
        "sag_mm": round(sag, 4),
        "growth_mm": round(growth, 3),
        "side_gap_mm": round((chamber_w() - DECK_W) / 2.0, 3),
        "mouth_h": round(mh, 2),
        "front_h": s.front_h,
        "mouth_ratio": round(mh / s.front_h, 4),
        "soffit_h": s.soffit_h,
        "contact_steel_C": round(contact_temperature(e_steel, T_DECK), 1),
        "contact_cordierite_450_C": round(contact_temperature(e_cord, 450.0), 1),
        "steak_flux_W_m2": round(q_steak, 0),
        "heatup_min": round(heatup_min, 1),
        "bread_window_min": round(bread_min, 1),
        "pack_open_min": round(pack_open_min, 1),
        "pack_shut_min": round(pack_shut_min, 1),
        "bbox_mm": _bbox(items),
        "aabb_hits": len(collisions),
        "aabb_pairs": collisions[:12],
        "n_parts": len(items),
        "pizza_clearance_mm": round((min(DECK_W, MOUTH_W) - 381.0) / 2.0, 2),
        "body_height_mm": round(_bbox(items)[5] - _bbox(items)[2], 1),
        "body_length_mm": round(_bbox(items)[4] - _bbox(items)[1], 1),
        "body_width_mm": round(_bbox(items)[3] - _bbox(items)[0], 1),
    }


def _bbox(items: list[dict]) -> list[float]:
    boxes = [_aabb(part) for part in items]
    boxes = [box for box in boxes if box is not None]
    return [
        round(min(box[0] for box in boxes), 2),
        round(min(box[1] for box in boxes), 2),
        round(min(box[2] for box in boxes), 2),
        round(max(box[3] for box in boxes), 2),
        round(max(box[4] for box in boxes), 2),
        round(max(box[5] for box in boxes), 2),
    ]


def vector_keys() -> tuple[str, ...]:
    return (
        "deck_t", "ins_t", "floor_ins", "belly_ins", "liner_t", "skin_t",
        "pit_t", "front_h", "soffit_h", "air_gap", "standoff",
    )


def design_from(values: dict, dragon: str) -> Stack:
    return Stack(dragon=dragon, **{key: float(values[key]) for key in vector_keys()})
