"""Mass, heat, scorch, and warp for the long-vault prototypes.

Morning and Moondancer stay in masslib.py. This module is the next
family: a rolled half-barrel, longer than it is wide, with a free mild-steel
floor and a removable sky plate. Lengths are millimetres. Temperatures
returned to callers are Celsius.

The floor is bare normalised mild steel, seasoned, because that is the
cooking surface that was asked for. It is not galvanised and it is not
painted. Cordierite is not a part.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

SIGMA = 5.670374419e-8
T_AMB = 20.0
PIZZA_MM = 381.0
BURNER_KW = 6.0
BURNER_KG = 1.85
# Ceramic-fibre blanket a kiln offcut actually is. k at a mid-wall mean.
K_FIBRE = 0.075
RHO_FIBRE = 128.0
K_AIR = 0.035
ALPHA_STEEL = 13.0e-6
K_STEEL = 45.0
# Imperfect contact: semolina, bubbles, a wet dough face. Calibrated so a
# 290 C floor chars in a few minutes and a 400 C floor does not wait.
H_CONTACT = 40.0

DENS = {
    "mild": 7850.0,
    "ss": 7900.0,
    "al": 2680.0,
    "jarrah": 820.0,
    "gidgee": 1250.0,
    "fibre": RHO_FIBRE,
    "ptfe": 2200.0,
    "rubber": 1100.0,
}
CP = {"mild": 500.0, "ss": 500.0, "al": 900.0, "fibre": 1000.0, "cordierite": 950.0}
K = {"ss": 16.0, "al": 160.0, "mild": K_STEEL, "fibre": K_FIBRE, "air": K_AIR, "wood": 0.16, "ptfe": 0.25}


def _mm3_to_kg(volume_mm3: float, density: float) -> float:
    return volume_mm3 * 1e-9 * density


def _eps_pair(a: float, b: float) -> float:
    return 1.0 / (1.0 / a + 1.0 / b - 1.0)


@dataclass(frozen=True)
class Vault:
    """One prototype. Geometry is the identity. Gauges are the solver's."""

    name: str
    dragon: str
    radius: float = 250.0
    length: float = 680.0
    mouth_w: float = 430.0
    mouth_h: float = 158.0
    steel_w: float = 450.0
    steel_l: float = 500.0
    steel_t: float = 6.0
    landing: float = 40.0
    plate_t: float = 1.2
    plate_drop: float = 95.0
    liner_t: float = 0.8
    fibre_t: float = 55.0
    air_gap: float = 8.0
    skin_t: float = 1.0
    floor_fibre: float = 28.0
    button_h: float = 4.0
    base_t: float = 1.0
    standoff: float = 18.0
    handle_phi: float = 42.0
    broil_gap: float = 70.0
    pizza_gas: float = 370.0
    broil_gas: float = 500.0
    bread_gas: float = 260.0
    box_d: float = 80.0
    door_pose: str = "shut"
    sill_w: float = 0.0
    sill_d: float = 0.0
    sill_t: float = 1.2
    stop_gap: float = 0.0
    plate_pose: str = "in"
    frame_strap: float = 0.0
    swing_arm: float = 0.0
    module: float = 0.0
    # End skin is a half-ring this far clear of the liner. Zero keeps the
    # earlier solid-end mass, which the shop never cut.
    fascia_gap: float = 0.0
    probe: float = 0.0
    base_mark: float = 0.0
    hinge: float = 0.0
    hinge_sole: float = 0.0


def stack_thickness(v: Vault) -> float:
    return v.liner_t + v.fibre_t + v.air_gap + v.skin_t


def outer_radius(v: Vault) -> float:
    return v.radius + stack_thickness(v)


def hearth_below(v: Vault) -> float:
    """Millimetres of structure under the top of the steel."""
    return v.base_t + v.floor_fibre + v.button_h + v.steel_t


def body_height(v: Vault) -> float:
    return hearth_below(v) + outer_radius(v)


def outer_width(v: Vault) -> float:
    return 2.0 * outer_radius(v)


def outer_length(v: Vault) -> float:
    return v.length + 2.0 * stack_thickness(v)


def plate_span(v: Vault) -> tuple[float, float]:
    """Sky plate must sit inside the arch at its height, with clearance to the liner."""
    height = v.radius - v.plate_drop
    half = math.sqrt(max(v.radius * v.radius - height * height, 0.0)) - 12.0
    width = min(v.steel_w - 16.0, 2.0 * max(half, 0.0))
    length = min(v.steel_l - 20.0, v.length - v.landing - 80.0)
    return width, length


def areas_m2(v: Vault) -> dict[str, float]:
    r = v.radius / 1000.0
    length = v.length / 1000.0
    # Half-barrel lateral area, inner.
    lateral = math.pi * r * length
    end = 0.5 * math.pi * r * r
    steel = (v.steel_w / 1000.0) * (v.steel_l / 1000.0)
    mouth = (v.mouth_w / 1000.0) * (v.mouth_h / 1000.0)
    return {"lateral": lateral, "end": end, "steel": steel, "mouth": mouth, "wall": lateral + 2.0 * end}


def wall_temperature(v: Vault, t_gas: float) -> dict[str, float]:
    """1D arch. Gas, liner, fibre, still air gap, aluminium, outside air."""
    r_in = 1.0 / 25.0
    r_liner = (v.liner_t / 1000.0) / K["ss"]
    r_fibre = (v.fibre_t / 1000.0) / K_FIBRE
    r_air = (v.air_gap / 1000.0) / K_AIR
    r_skin = (v.skin_t / 1000.0) / K["al"]
    r_ext = 1.0 / 10.0
    total = r_in + r_liner + r_fibre + r_air + r_skin + r_ext
    flux = (t_gas - T_AMB) / total
    t = t_gas - flux * r_in
    t_after_liner = t - flux * r_liner
    t_after_fibre = t_after_liner - flux * r_fibre
    t_skin_in = t_after_fibre - flux * r_air
    t_skin = t_skin_in - flux * r_skin
    return {
        "flux": flux,
        "outer_C": t_skin,
        "skin_in_C": t_skin_in,
        "fibre_hot_C": t_after_liner,
        "R": total,
    }


def floor_resistance(v: Vault) -> float:
    """Steel underside to ambient, m2.K/W. Buttons are a parallel metal path."""
    area = areas_m2(v)["steel"]
    button_area = 6.0 * math.pi * (0.005 ** 2)
    r_air = (v.button_h / 1000.0) / K_AIR
    # Parallel: air gap over the whole plan, plus six stainless domes.
    u_air = 1.0 / r_air
    u_buttons = K["ss"] * (button_area / area) / (v.button_h / 1000.0)
    r_gap = 1.0 / (u_air + u_buttons)
    r_fibre = (v.floor_fibre / 1000.0) / K_FIBRE
    r_base = (v.base_t / 1000.0) / K["al"]
    r_ext = 1.0 / 10.0
    return r_gap + r_fibre + r_base + r_ext


def underside_temperature(v: Vault, t_floor: float) -> dict[str, float]:
    total = floor_resistance(v)
    flux = (t_floor - T_AMB) / total
    return {"flux": flux, "under_C": T_AMB + flux / 10.0, "R": total}


def grip_temperature(skin_c: float, standoff_mm: float) -> float:
    """Two grips, two posts each. Jarrah bar in air, PTFE washer on each post."""
    n_posts = 4.0
    a_post = math.pi * (0.003 ** 2)
    r_post = (standoff_mm / 1000.0) / (K["ss"] * a_post)
    a_ptfe = math.pi * (0.008 ** 2)
    r_ptfe = 0.003 / (K["ptfe"] * a_ptfe)
    r_path = (r_post + r_ptfe) / n_posts
    # Two bars, 140 x 36 x 28, cooled on the exposed faces.
    area = 2.0 * (2.0 * (0.140 * 0.036 + 0.140 * 0.028 + 0.036 * 0.028))
    r_conv = 1.0 / (10.0 * area)
    return T_AMB + (skin_c - T_AMB) * r_conv / (r_path + r_conv)


def _exchange(v: Vault, t_gas: float, t_plate: float, t_floor: float, leak: float = 1.0) -> dict[str, float]:
    """Fluxes in W/m2 on the steel plan. Plate area is taken equal to the floor."""
    tg = t_gas + 273.15
    tp = t_plate + 273.15
    tf = t_floor + 273.15
    ta = T_AMB + 273.15
    eps_up = _eps_pair(0.85, 0.75)
    eps_pf = _eps_pair(0.75, 0.79)
    q_up = 18.0 * (t_gas - t_plate) + eps_up * SIGMA * 0.85 * (tg**4 - tp**4)
    q_pf = 6.0 * (t_plate - t_floor) + eps_pf * SIGMA * 0.82 * (tp**4 - tf**4)
    # Half-ellipse mouth, about four fifths of the rectangular opening.
    # leak is 1 with the door open. A shut door leaves a slot, not the whole mouth.
    q_pm = 0.75 * SIGMA * 0.08 * leak * (tp**4 - ta**4)
    q_fm = 0.79 * SIGMA * 0.13 * leak * (tf**4 - ta**4)
    q_down = (t_floor - T_AMB) / floor_resistance(v)
    return {"q_up": q_up, "q_pf": q_pf, "q_pm": q_pm, "q_fm": q_fm, "q_down": q_down}


def equilibrium(v: Vault, t_gas: float, leak: float = 1.0) -> dict[str, float]:
    """Sky plate in. Plate and floor float. Vault gas is the burner setpoint."""

    def mismatch(tp: float, tf: float) -> tuple[float, float]:
        q = _exchange(v, t_gas, tp, tf, leak)
        return q["q_up"] - q["q_pf"] - q["q_pm"], q["q_pf"] - q["q_fm"] - q["q_down"]

    tp, tf = t_gas - 30.0, min(300.0, t_gas - 50.0)
    for _ in range(40):
        f_p, f_f = mismatch(tp, tf)
        # Numerical derivatives. The map is smooth and monotonic.
        dp, df = 1.0, 1.0
        f_p_tp, f_f_tp = mismatch(tp + dp, tf)
        f_p_tf, f_f_tf = mismatch(tp, tf + df)
        j00 = (f_p_tp - f_p) / dp
        j01 = (f_p_tf - f_p) / df
        j10 = (f_f_tp - f_f) / dp
        j11 = (f_f_tf - f_f) / df
        det = j00 * j11 - j01 * j10
        if abs(det) < 1e-9:
            break
        tp -= (f_p * j11 - j01 * f_f) / det
        tf -= (j00 * f_f - f_p * j10) / det
        tp = min(max(tp, T_AMB + 5.0), t_gas)
        tf = min(max(tf, T_AMB + 5.0), t_gas)
    q = _exchange(v, t_gas, tp, tf, leak)
    under = underside_temperature(v, tf)
    return {
        "plate_C": tp,
        "floor_C": tf,
        "under_C": under["under_C"],
        "q_down": q["q_down"],
        "balance_plate": q["q_up"] - q["q_pf"] - q["q_pm"],
        "balance_floor": q["q_pf"] - q["q_fm"] - q["q_down"],
    }


def scorch_seconds(t_floor: float) -> float:
    """Seconds until a 1 mm dough face hits 230 C, after the surface water is gone.

    Baker's 70% hydration. The wet face holds 100 C until a 0.3 mm layer's
    water is gone, then a dry 1 mm layer climbs toward the steel temperature.
    """
    if t_floor <= 100.0:
        return 1.0e6
    water_kg_m2 = 1100.0 * 0.0003 * (0.70 / 1.70)
    q_evap = water_kg_m2 * 2.26e6
    q_dry = H_CONTACT * (t_floor - 100.0)
    t_dry = q_evap / q_dry
    if t_floor <= 230.0:
        return 1.0e6
    tau = 1100.0 * 0.001 * 3200.0 / H_CONTACT
    # 230 = T - (T - 100) * exp(-t/tau)
    ratio = (t_floor - 230.0) / (t_floor - 100.0)
    t_climb = -tau * math.log(ratio)
    return t_dry + t_climb


def warp(v: Vault, q_down: float) -> dict[str, float]:
    """Thermal camber of a free plate, plus the in-plane growth the gap must clear.

    A through-thickness gradient bends a free plate into a spherical cap.
    Residual stress is kept off the plate by specifying normalised
    AS/NZS 3678-250, not by a fastener.
    """
    t = v.steel_t / 1000.0
    length = v.steel_l / 1000.0
    delta_t = q_down * t / K_STEEL
    camber = ALPHA_STEEL * delta_t * length * length / (8.0 * t)
    growth = ALPHA_STEEL * (320.0 - T_AMB) * v.steel_l
    side_gap = (2.0 * v.radius - v.steel_w) / 2.0
    # Self weight on a 2 x 3 button grid. Long span is half the plate.
    span = (v.steel_l - 80.0) / 2.0
    width = v.steel_w
    inertia = width * (v.steel_t ** 3) / 12.0
    load_per_mm = (v.steel_w * v.steel_l * v.steel_t * 1e-9 * DENS["mild"] * 9.81) / v.steel_l
    # 5 w L^4 / 384 E I, millimetres. E = 210000 MPa = N/mm2.
    sag = 5.0 * load_per_mm * (span ** 4) / (384.0 * 210000.0 * inertia)
    return {
        "gradient_K": delta_t,
        "camber_mm": camber * 1000.0,
        "growth_mm": growth,
        "side_gap_mm": side_gap,
        "sag_mm": sag,
    }


def bay_underside(v: Vault, view_crown: float = 0.55, view_mouth: float = 0.20) -> dict[str, float]:
    """Bare front bay under the broil crown. The plate is parked behind it.

    The view pair is the hotter of the two cases checked while sizing the
    floor blanket. More mouth view runs a cooler floor.
    """
    resistance = floor_resistance(v)
    crown = v.broil_gas + 273.15
    ambient = T_AMB + 273.15
    tf = 400.0
    for _ in range(60):
        tk = tf + 273.15
        q_in = 0.79 * SIGMA * view_crown * (crown**4 - tk**4)
        q_out = 0.79 * SIGMA * view_mouth * (tk**4 - ambient**4) + (tf - T_AMB) / resistance
        tf += (q_in - q_out) * 0.0015
        tf = min(max(tf, 40.0), 520.0)
    under = T_AMB + ((tf - T_AMB) / resistance) / 10.0
    return {"floor_C": tf, "under_C": under, "R": resistance}


def broil_flux(v: Vault) -> float:
    """Plate out. Steak 70 mm under a  sooted crown at the broil setpoint."""
    crown = v.broil_gas + 273.15
    steak = 100.0 + 273.15
    view = 0.65
    return 0.85 * SIGMA * view * (crown**4 - steak**4)


def _cool_seconds(capacity_j_k: float, area_m2: float, eps: float, view: float, h: float, t0_c: float, t1_c: float) -> float:
    temp = t0_c + 273.15
    goal = t1_c + 273.15
    ambient = T_AMB + 273.15
    elapsed = 0.0
    step = 2.0
    while temp > goal and elapsed < 6.0 * 3600.0:
        flux = eps * SIGMA * view * (temp**4 - ambient**4) + h * (temp - ambient)
        temp -= flux * area_m2 / capacity_j_k * step
        elapsed += step
    return elapsed


def tread_cooldown_s() -> float:
    """Open-mouth cool of a 13.5 kg Tread-class stone, stated assumptions.

    2.8 kg of cordierite from 400 C, 0.33 m square, view 0.25 out a low mouth.
    The rest of the 13.5 kg is shell and is not the cooking surface.
    """
    capacity = 2.8 * CP["cordierite"]
    return _cool_seconds(capacity, 0.33 * 0.33, 0.85, 0.25, 12.0, 400.0, 60.0)


def cooldown_open_s(v: Vault, t_floor: float) -> float:
    """Door open, sky plate lifted out, steel radiating through the tall mouth."""
    mass = (v.steel_w * v.steel_l * v.steel_t) * 1e-9 * DENS["mild"]
    capacity = mass * CP["mild"]
    return _cool_seconds(capacity, areas_m2(v)["steel"], 0.79, 0.40, 15.0, t_floor, 60.0)


def heatup_minutes(v: Vault, floor_c: float, plate_c: float, t_gas: float, eta: float = 0.35) -> dict[str, float]:
    """Energy to the setpoints. 0.35 is the door-open hold-in. 0.55 is the door shut."""
    steel_kg = (v.steel_w * v.steel_l * v.steel_t) * 1e-9 * DENS["mild"]
    plate_w, plate_l = plate_span(v)
    plate_kg = (plate_w * plate_l * v.plate_t) * 1e-9 * DENS["ss"]
    liner_m2 = areas_m2(v)["wall"]
    liner_kg = liner_m2 * (v.liner_t / 1000.0) * DENS["ss"]
    # The hot third of the blanket, not the cold face.
    fibre_kg = liner_m2 * (v.fibre_t / 1000.0) * RHO_FIBRE / 3.0
    energy = (
        steel_kg * CP["mild"] * (floor_c - T_AMB)
        + plate_kg * CP["ss"] * (plate_c - T_AMB)
        + liner_kg * CP["ss"] * (t_gas - T_AMB) * 0.85
        + fibre_kg * CP["fibre"] * (t_gas - T_AMB) * 0.5
    )
    watts = BURNER_KW * 1000.0 * eta
    shut = BURNER_KW * 1000.0 * 0.55
    return {
        "energy_MJ": energy / 1e6,
        "minutes": energy / watts / 60.0,
        "shut_minutes": energy / shut / 60.0,
        "steel_kg": steel_kg,
    }


def masses(v: Vault) -> dict[str, float]:
    r = v.radius
    stack = stack_thickness(v)
    r_out = r + stack
    length = v.length

    def lateral(r_in: float, thick: float) -> float:
        r_o = r_in + thick
        return 0.5 * math.pi * (r_o * r_o - r_in * r_in) * length

    def end_plates(radius: float, thick: float) -> float:
        """Two half-disc ends. The front one is punched for the mouth later."""
        return 2.0 * 0.5 * math.pi * radius * radius * thick

    def end_annulus(r_in: float, thick: float) -> float:
        """Blanket folded onto both ends, axial depth equal to the layer."""
        r_o = r_in + thick
        return 2.0 * 0.5 * math.pi * (r_o * r_o - r_in * r_in) * thick

    liner = _mm3_to_kg(lateral(r, v.liner_t) + end_plates(r, v.liner_t), DENS["ss"])
    liner -= _mm3_to_kg(v.mouth_w * v.mouth_h * v.liner_t, DENS["ss"])
    fibre = _mm3_to_kg(
        lateral(r + v.liner_t, v.fibre_t) + end_annulus(r + v.liner_t, v.fibre_t),
        DENS["fibre"],
    )
    skin_r = r + v.liner_t + v.fibre_t + v.air_gap
    skin_mm3 = lateral(skin_r, v.skin_t)
    if v.fascia_gap > 0.0:
        inner = r + v.liner_t + v.fascia_gap
        outer = skin_r + v.skin_t
        skin_mm3 += math.pi * (outer * outer - inner * inner) * v.skin_t
    else:
        skin_mm3 += end_plates(skin_r, v.skin_t)
        skin_mm3 -= v.mouth_w * v.mouth_h * v.skin_t
    skin = _mm3_to_kg(skin_mm3, DENS["al"])

    plan_w = outer_width(v)
    plan_l = outer_length(v)
    base = _mm3_to_kg(plan_w * plan_l * v.base_t, DENS["al"])
    floor_ins = _mm3_to_kg(v.steel_w * v.steel_l * v.floor_fibre, DENS["fibre"])
    steel = _mm3_to_kg(v.steel_w * v.steel_l * v.steel_t, DENS["mild"])
    plate_w, plate_l = plate_span(v)
    plate = _mm3_to_kg(plate_w * plate_l * v.plate_t, DENS["ss"])
    # Full slide, forward seat to the rear park, on every pose.
    rail_l = (v.length - 20.0) - (v.landing + 30.0)
    rails = _mm3_to_kg(2.0 * rail_l * 12.0 * 1.2, DENS["ss"])
    buttons = _mm3_to_kg(6.0 * math.pi * 5.0 ** 2 * v.button_h, DENS["ss"])

    # Door: stainless tray, fibre, outer skin, sized over the mouth.
    door_w = v.mouth_w + 36.0
    door_h = v.mouth_h + 36.0
    door_ss = _mm3_to_kg(door_w * door_h * 0.8 * 2.0, DENS["ss"])
    door_fibre = _mm3_to_kg(v.mouth_w * v.mouth_h * 12.0, DENS["fibre"])
    hood = _mm3_to_kg(v.mouth_w * 40.0 * 0.8, DENS["ss"])
    frame = _mm3_to_kg((door_w * door_h - v.mouth_w * v.mouth_h) * 1.2, DENS["ss"])

    # Shell only. Depth follows the cowl; 80 mm is the Stormcloud housing.
    box_d = v.box_d
    box = _mm3_to_kg((180.0 * 140.0 * 2.0 + 180.0 * box_d * 2.0 + 140.0 * box_d) * 0.8, DENS["ss"])
    grips = _mm3_to_kg(2.0 * 140.0 * 36.0 * 28.0 * 0.72, DENS["jarrah"])
    ferrules = _mm3_to_kg(4.0 * math.pi * (16.0 ** 2 - 14.0 ** 2) * 8.0, DENS["gidgee"])
    posts = _mm3_to_kg(4.0 * math.pi * 3.0 ** 2 * v.standoff, DENS["ss"])
    washers = _mm3_to_kg(4.0 * math.pi * 8.0 ** 2 * 3.0, DENS["ptfe"])
    peel = _mm3_to_kg(v.mouth_w * 22.0 * 14.0, DENS["jarrah"])
    pull = _mm3_to_kg(90.0 * 22.0 * 16.0, DENS["jarrah"])
    sill = _mm3_to_kg(v.sill_w * v.sill_d * v.sill_t, DENS["ss"])
    stop_t, stop_h = 2.0, 3.0
    if v.stop_gap > 0.0:
        end_mm3 = 2.0 * v.steel_w * stop_t * stop_h
        side_len = v.steel_l - 2.0 * (v.stop_gap + stop_t)
        side_mm3 = 2.0 * side_len * stop_t * stop_h
        stops = _mm3_to_kg(end_mm3 + side_mm3, DENS["ss"])
    else:
        stops = 0.0
    if v.frame_strap > 0.0:
        # Two cheek straps, 40 mm wide, from the spring line up past the grip.
        arc = outer_radius(v) * math.radians(55.0)
        strap = _mm3_to_kg(2.0 * arc * 40.0 * v.frame_strap, DENS["ss"])
        strap += _mm3_to_kg(2.0 * 40.0 * (v.base_t + v.floor_fibre) * v.frame_strap, DENS["ss"])
    else:
        strap = 0.0
    if v.swing_arm > 0.0:
        tray = _mm3_to_kg(160.0 * 120.0 * 1.5 + 220.0 * math.pi * 5.0 ** 2, DENS["ss"])
    else:
        tray = 0.0
    if v.probe > 0.0:
        gland = _mm3_to_kg(math.pi * (6.0 ** 2 - (v.probe / 2.0) ** 2) * 8.0, DENS["ss"])
    else:
        gland = 0.0
    if v.hinge > 0.0:
        # Two 2 mm straps from the mouth arch out to the pin, plus the pin and two lugs.
        strap_l = (outer_radius(v) + 13.6 + 12.0 + 16.0 + 3.2) - (v.mouth_w / 2.0 + 18.0)
        hinge_kg = _mm3_to_kg(2.0 * strap_l * 16.0 * 2.0, DENS["ss"])
        hinge_kg += _mm3_to_kg(math.pi * (v.hinge / 2.0) ** 2 * (v.mouth_h + 50.0), DENS["ss"])
        hinge_kg += _mm3_to_kg(2.0 * 20.0 * 16.0 * 14.0, DENS["al"])
        if v.hinge_sole > 0.0:
            hinge_kg += _mm3_to_kg(v.hinge_sole * 25.0 * 8.0, DENS["al"])
    else:
        hinge_kg = 0.0
    feet = _mm3_to_kg(4.0 * math.pi * 16.0 ** 2 * 10.0, DENS["rubber"])
    rack = _mm3_to_kg(4.0 * math.pi * 6.0 ** 2 * 8.0, DENS["ss"])
    stand = _mm3_to_kg(4.0 * math.pi * 7.0 ** 2 * 8.0, DENS["ss"])
    broil = _mm3_to_kg(8.0 * v.steel_w * math.pi * 2.0 ** 2, DENS["ss"])

    rows = {
        "liner": liner,
        "fibre-arch": fibre,
        "aluminium-skin": skin,
        "base": base,
        "floor-fibre": floor_ins,
        "pizza-steel": steel,
        "sky-plate": plate,
        "sky-rails": rails,
        "buttons": buttons,
        "door": door_ss + door_fibre,
        "throat-hood": hood,
        "mouth-frame": frame,
        "burner-box": box,
        "grips": grips,
        "gidgee-ferrules": ferrules,
        "posts": posts,
        "ptfe": washers,
        "peel-rest": peel,
        "door-pull": pull,
        "launch-sill": sill,
        "plate-stops": stops,
        "cheek-straps": strap,
        "swing-tray": tray,
        "probe-gland": gland,
        "hinge": hinge_kg,
        "feet": feet,
        "rack-bosses": rack,
        "stand-bosses": stand,
        "broil-rack": broil,
        "burner-allowance": BURNER_KG,
    }
    return {key: round(value, 3) for key, value in rows.items()}


def evaluate(v: Vault) -> dict:
    skin = wall_temperature(v, v.broil_gas)
    hold = equilibrium(v, v.pizza_gas)
    bread = equilibrium(v, v.bread_gas, leak=0.03)
    bent = warp(v, hold["q_down"])
    parts = masses(v)
    ready = sum(parts.values())
    cool = cooldown_open_s(v, hold["floor_C"])
    tread = tread_cooldown_s()
    heat = heatup_minutes(v, hold["floor_C"], hold["plate_C"], v.pizza_gas)
    pizza_clearance = (v.steel_w - PIZZA_MM) / 2.0
    return {
        "ready_kg": ready,
        "parts": parts,
        "skin_C": skin["outer_C"],
        "skin_in_C": skin["skin_in_C"],
        "fibre_hot_C": skin["fibre_hot_C"],
        "wall_flux": skin["flux"],
        "floor_C": hold["floor_C"],
        "plate_C": hold["plate_C"],
        "under_C": hold["under_C"],
        "bread_floor_C": bread["floor_C"],
        "bread_plate_C": bread["plate_C"],
        "balance_plate": hold["balance_plate"],
        "balance_floor": hold["balance_floor"],
        "scorch_s": scorch_seconds(hold["floor_C"]),
        "camber_mm": bent["camber_mm"],
        "sag_mm": bent["sag_mm"],
        "growth_mm": bent["growth_mm"],
        "side_gap_mm": bent["side_gap_mm"],
        "gradient_K": bent["gradient_K"],
        "broil_W_m2": broil_flux(v),
        "cooldown_s": cool,
        "tread_cooldown_s": tread,
        "cooldown_ratio": cool / tread,
        "heatup_min": heat["minutes"],
        "heatup_shut_min": heat["shut_minutes"],
        "heatup_MJ": heat["energy_MJ"],
        "steel_kg": heat["steel_kg"],
        "grip_C": grip_temperature(skin["outer_C"], v.standoff),
        "outer_width": outer_width(v),
        "outer_length": outer_length(v),
        "body_height": body_height(v),
        "outer_r": outer_radius(v),
        "mouth_over_crown": v.mouth_h / v.radius,
        "pizza_clearance": pizza_clearance,
        "free_floating": True,
    }


def vector_keys() -> tuple[str, ...]:
    return ("steel_t", "fibre_t", "floor_fibre", "skin_t", "plate_t", "standoff", "air_gap")


# Laser blank. The barrel is a true development. The ends are flat half-rings.
SKIN_SEAM = 0.3
SKIN_TAB = 12.0
RIVET_PITCH = 40.0
RIVET_D = 4.2
BASE_MARK = "be vigilant. don't die."


def skin_development(v: Vault) -> dict:
    """Flat aluminium. Arc length is the mid-thickness of the rolled half-barrel."""
    skin_r0 = v.radius + v.liner_t + v.fibre_t + v.air_gap
    mid_r = skin_r0 + v.skin_t / 2.0
    outer_r = skin_r0 + v.skin_t
    inner_r = v.radius + v.liner_t + v.fascia_gap
    arc = math.pi * mid_r
    cyl = v.length - 2.0 * SKIN_SEAM
    return {
        "mid_r": mid_r,
        "outer_r": outer_r,
        "inner_r": inner_r,
        "arc_mm": arc,
        "cyl_mm": cyl,
        "tab_mm": SKIN_TAB,
        "rivet_d": RIVET_D,
        "rivet_pitch": RIVET_PITCH,
        "sheet_w": arc + 2.0 * SKIN_TAB,
        "sheet_l": cyl,
    }


def gland_clears_mouth(v: Vault) -> bool:
    """The bore sits in the front plate, beside the arch, not in the opening."""
    x = v.mouth_w / 2.0 + 14.0
    z = 70.0
    return (x / (v.mouth_w / 2.0)) ** 2 + (z / v.mouth_h) ** 2 > 1.0


def _dxf_pair(code: str, value: str) -> list[str]:
    return [code, value]


def write_skin_dxf(path, spec: dict, mark_edges: list[tuple[float, float, float, float]] | None = None) -> None:
    """R12 entities. Tabs are the spring line. Rivets are every two modules."""
    ents: list[str] = []

    def line(x1: float, y1: float, x2: float, y2: float, layer: str) -> None:
        ents.extend(
            [
                "0", "LINE", "8", layer,
                "10", f"{x1:.3f}", "20", f"{y1:.3f}", "30", "0.000",
                "11", f"{x2:.3f}", "21", f"{y2:.3f}", "31", "0.000",
            ]
        )

    def circle(x: float, y: float, r: float, layer: str) -> None:
        ents.extend(
            [
                "0", "CIRCLE", "8", layer,
                "10", f"{x:.3f}", "20", f"{y:.3f}", "30", "0.000",
                "40", f"{r:.3f}",
            ]
        )

    def arc(cx: float, cy: float, r: float, a0: float, a1: float, layer: str) -> None:
        ents.extend(
            [
                "0", "ARC", "8", layer,
                "10", f"{cx:.3f}", "20", f"{cy:.3f}", "30", "0.000",
                "40", f"{r:.3f}", "50", f"{a0:.3f}", "51", f"{a1:.3f}",
            ]
        )

    tab = spec["tab_mm"]
    arc_mm = spec["arc_mm"]
    cyl = spec["cyl_mm"]
    pitch = spec["rivet_pitch"]
    hole = spec["rivet_d"] / 2.0
    # Barrel, tabs included. X is the unrolled arc. Y is the barrel axis.
    line(0.0, 0.0, arc_mm + 2.0 * tab, 0.0, "TAB")
    line(arc_mm + 2.0 * tab, 0.0, arc_mm + 2.0 * tab, cyl, "TAB")
    line(arc_mm + 2.0 * tab, cyl, 0.0, cyl, "TAB")
    line(0.0, cyl, 0.0, 0.0, "TAB")
    line(tab, 0.0, tab, cyl, "ROLL")
    line(tab + arc_mm, 0.0, tab + arc_mm, cyl, "ROLL")
    line(tab + arc_mm / 2.0, 0.0, tab + arc_mm / 2.0, cyl, "ROLL")
    y = pitch / 2.0
    while y < cyl - pitch / 4.0:
        circle(tab / 2.0, y, hole, "RIVET")
        circle(tab + arc_mm + tab / 2.0, y, hole, "RIVET")
        y += pitch
    # Two half-rings, flat on the diameter, to the right of the barrel.
    gap = 30.0
    cx = arc_mm + 2.0 * tab + gap + spec["outer_r"]
    for name_y in (0.0, spec["outer_r"] + gap):
        cy = -(spec["outer_r"] + 20.0 + name_y)
        arc(cx, cy, spec["outer_r"], 0.0, 180.0, "FASCIA")
        arc(cx, cy, spec["inner_r"], 0.0, 180.0, "FASCIA")
        line(cx - spec["outer_r"], cy, cx - spec["inner_r"], cy, "FASCIA")
        line(cx + spec["inner_r"], cy, cx + spec["outer_r"], cy, "FASCIA")
        # Rivets on the outer rim, two modules apart along the arc.
        step = pitch / spec["outer_r"]
        theta = step
        while theta < math.pi - step / 2.0:
            rx = cx + spec["outer_r"] * math.cos(theta) * 0.96
            ry = cy + spec["outer_r"] * math.sin(theta) * 0.96
            circle(rx, ry, hole, "RIVET")
            theta += step
    if mark_edges:
        xs = [value for edge in mark_edges for value in (edge[0], edge[2])]
        ys = [value for edge in mark_edges for value in (edge[1], edge[3])]
        ox = tab - min(xs)
        oy = cyl + 40.0 - min(ys)
        for x1, y1, x2, y2 in mark_edges:
            line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, "MARK")
    body = "\n".join(["0", "SECTION", "2", "ENTITIES", *ents, "0", "ENDSEC", "0", "EOF"]) + "\n"
    path.write_text(body, encoding="utf-8")
