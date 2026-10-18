"""Named parameters for the Angas 430.

Lengths are millimetres. This is the design being modelled: Argon's
unconstrained optimum, with the mouth widened so a 381 mm pizza enters
and the crown lifting off at the cinch band so the stone does not have
to pass the mouth. A later critique can move a number; the solids read
this module only.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TailgateSpec:
    name: str = "angas-430"
    # Cooking
    floor_d: float = 430.0
    floor_t: float = 20.0
    chamber_id: float = 470.0
    # The cinch sits above the mouth, with a 12 mm joggle, so the crown
    # lifts off without splitting the arch. Skirt is tall enough for that.
    # Skirt stays taller than the mouth so the cinch ring is a complete
    # circle above the arch. The dome rise is what is left of a 165 mm apex.
    skirt_h: float = 120.0
    dome_rise: float = 45.0
    mouth_w: float = 420.0
    mouth_h: float = 95.0
    joggle_h: float = 12.0
    # Sheets
    liner_t: float = 1.2
    skin_t: float = 1.2
    base_t: float = 1.5
    # Insulation. Wall and crown have the same total thickness so the
    # outer skin is one surface. The wall spends part of it on board.
    # Critique lock: 100 mm of AES on the crown puts the skin under 55°C.
    # The wall matches that total so the outer skin stays one surface.
    wall_aes: float = 75.0
    wall_casi: float = 25.0
    crown_aes: float = 100.0
    floor_aes: float = 25.0
    floor_casi: float = 25.0
    # Hardware
    band_w: float = 35.0
    band_t: float = 3.0
    handle_od: float = 32.0
    handle_len: float = 220.0
    handle_standoff: float = 35.0
    leg_od: float = 25.4
    leg_wall: float = 1.6
    leg_len: float = 750.0
    stub_h: float = 65.0
    # Bought burner allowance, not modelled as a jet.
    burner_kg: float = 1.85
    burner_kw: float = 5.8

    def __post_init__(self) -> None:
        if abs((self.wall_aes + self.wall_casi) - self.crown_aes) > 0.2:
            raise ValueError("wall and crown insulation totals must match so the skin is one surface")
        if self.floor_d < 420:
            raise ValueError("floor is under the 420 mm requirement")
        if self.mouth_w < 400:
            raise ValueError("mouth is tight for a 381 mm pizza")
        if self.skirt_h < self.mouth_h + self.joggle_h + 4:
            raise ValueError("the cinch joggle cuts into the mouth arch")
        if self.outer_diameter > 1224:
            raise ValueError("plan diameter does not pass between the Shark wheel arches")
        if self.body_height > 460:
            raise ValueError("body is too tall for the tub under a tonneau")

    @property
    def chamber_r(self) -> float:
        return self.chamber_id / 2

    @property
    def insulation_t(self) -> float:
        return self.wall_aes + self.wall_casi

    @property
    def wall_stack(self) -> float:
        return self.liner_t + self.insulation_t + self.skin_t

    @property
    def outer_radius(self) -> float:
        return self.chamber_r + self.wall_stack

    @property
    def outer_diameter(self) -> float:
        return 2 * self.outer_radius

    @property
    def hearth_z(self) -> float:
        """Top of the cordierite, millimetres above the underside of the base pan."""
        return self.base_t + self.floor_aes + self.floor_casi + self.liner_t + self.floor_t

    @property
    def apex_h(self) -> float:
        return self.skirt_h + self.dome_rise

    @property
    def mouth_over_apex(self) -> float:
        return self.mouth_h / self.apex_h

    @property
    def inner_apex_z(self) -> float:
        """Inside face of the liner at the crown."""
        return self.hearth_z + self.apex_h

    @property
    def outer_apex_z(self) -> float:
        """Outside of the skin at the crown. The apex normal is vertical."""
        return self.inner_apex_z + self.liner_t + self.crown_aes + self.skin_t

    @property
    def body_height(self) -> float:
        return self.outer_apex_z

    @property
    def spring_z(self) -> float:
        return self.hearth_z + self.skirt_h

    @property
    def handle_span(self) -> float:
        """Tip to tip of the two jarrah bars, matching the grip placement in the model."""
        return self.outer_diameter + 2 * (self.handle_standoff + self.handle_len - 10)

    @property
    def pizza_radial_clearance(self) -> float:
        return (self.floor_d - 381.0) / 2

    @property
    def mouth_side_clearance(self) -> float:
        return (self.mouth_w - 381.0) / 2


def skin_temperature(aes_mm: float, casi_mm: float = 0.0, liner_mm: float = 1.2, skin_mm: float = 1.2,
                     t_gas: float = 500.0, t_amb: float = 20.0, h_in: float = 25.0, h_ext: float = 10.0,
                     k_aes: float = 0.08, k_casi: float = 0.065, k_steel: float = 16.0) -> dict:
    """1D wall. Returns flux and the outer-skin temperature."""
    r = 1 / h_in
    r += (liner_mm / 1000) / k_steel
    r += (aes_mm / 1000) / k_aes
    if casi_mm:
        r += (casi_mm / 1000) / k_casi
    r += (skin_mm / 1000) / k_steel
    r_ext = 1 / h_ext
    flux = (t_gas - t_amb) / (r + r_ext)
    return {
        "R": round(r + r_ext, 4),
        "flux_W_m2": round(flux, 2),
        "skin_C": round(t_amb + flux * r_ext, 2),
    }


SPEC = TailgateSpec()
