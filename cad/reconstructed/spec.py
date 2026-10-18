"""Published envelopes and the inferred splits the solids are built from.

Every length is millimetres. A field that is not a published number is named
as inferred in `notes`. The 3D model and the section drawings both read this
module, so they cannot drift apart.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OvenSpec:
    """One reconstructed oven.

    Axis, after the part is built:
    - X across the mouth, centred.
    - Y from the front face (0) toward the back.
    - Z up from the underside of the body (0).
    """

    oven_id: str
    model_no: str
    # Published external body. Dome XL's installed height includes the flue;
    # `body_h` is the inferred solid that fits the carton.
    ext_w: float
    ext_d: float
    ext_h_published: float
    body_h: float
    int_w: float
    int_d: float
    int_h: float
    mouth_w: float
    mouth_h: float
    stone_t: float
    mass_kg: float
    power_kw: float
    # Inferred splits. front + rear + int_d = ext_d.
    front_wall: float
    rear_wall: float
    # Inferred stack.
    liner_t: float
    outer_t: float
    insulation_mm: tuple[float, ...]
    hearth_z: float
    flue: bool
    door: bool
    notes: str

    def __post_init__(self) -> None:
        side = (self.ext_w - self.int_w) / 2
        depth_sum = self.front_wall + self.rear_wall + self.int_d
        if abs(depth_sum - self.ext_d) > 0.2:
            raise ValueError(f"{self.oven_id}: front+rear+internal depth {depth_sum} != external {self.ext_d}")
        stack = self.liner_t + self.outer_t + sum(self.insulation_mm)
        if stack >= side:
            raise ValueError(f"{self.oven_id}: wall stack {stack:.1f} mm does not fit in side wall {side:.1f} mm")
        roof = self.body_h - self.hearth_z - self.int_h
        if roof <= self.outer_t + 5:
            raise ValueError(f"{self.oven_id}: roof space {roof:.1f} mm is thinner than a real crown")
        if self.hearth_z <= self.stone_t:
            raise ValueError(f"{self.oven_id}: hearth is not above the stone")

    @property
    def side_wall(self) -> float:
        return (self.ext_w - self.int_w) / 2

    @property
    def air_gap(self) -> float:
        return self.side_wall - self.liner_t - self.outer_t - sum(self.insulation_mm)

    @property
    def roof_space(self) -> float:
        return self.body_h - self.hearth_z - self.int_h

    @property
    def mouth_over_apex(self) -> float:
        return self.mouth_h / self.int_h

    @property
    def mouth_over_width(self) -> float:
        return self.mouth_w / self.int_w

    @property
    def installed_h(self) -> float:
        return self.ext_h_published if self.flue else self.body_h


# Hearth heights are inferred so the body height, the published cavity
# height, and a crown that can hold the stated insulation all close.
# The Dome XL 219 mm spec-sheet callout is not used as hearth_z.

ARC_LITE = OvenSpec(
    oven_id="arc-lite",
    model_no="GOZ-3102",
    ext_w=430,
    ext_d=481,
    ext_h_published=297,
    body_h=297,
    int_w=325,
    int_d=355,
    int_h=150,
    mouth_w=325,
    mouth_h=85,
    stone_t=12,
    mass_kg=12.0,
    power_kw=3.4,
    front_wall=40,
    rear_wall=86,
    liner_t=1.0,
    outer_t=1.0,
    insulation_mm=(25,),
    hearth_z=107,
    flue=False,
    door=False,
    notes=(
        "Published envelope and 12 mm stone. Side wall (430-325)/2 = 52.5 mm. "
        "One 25 mm AES layer inferred inside that wall, leaving an air gap. "
        "Hearth at 107 mm is inferred: 297 - 150 - 40 mm of crown. "
        "UK/EU plate 3.4 kW and 252 g/h; the comparison tool's 273.8 g/h is Tread's figure."
    ),
)

TREAD = OvenSpec(
    oven_id="tread",
    model_no="GOZ-1893",
    ext_w=418,
    ext_d=484,
    ext_h_published=320,
    body_h=320,
    int_w=310,
    int_d=380,
    int_h=150,
    mouth_w=310,
    mouth_h=85,
    stone_t=12,
    mass_kg=13.5,
    power_kw=3.7,
    front_wall=35,
    rear_wall=69,
    liner_t=1.0,
    outer_t=1.0,
    insulation_mm=(25,),
    hearth_z=115,
    flue=False,
    door=False,
    notes=(
        "Published envelope, 12 mm stone, SPCC pressings, 304 core, HPDC landing. "
        "Side wall (418-310)/2 = 54 mm. The extra external height over Arc Lite "
        "is modelled as a deeper base plus roof-rack handles, not a taller cavity. "
        "The 125 mm drawing callout is left unassigned."
    ),
)

DOME_XL = OvenSpec(
    oven_id="dome-xl",
    model_no="GOZ-2509",
    ext_w=946,
    ext_d=697,
    ext_h_published=997,
    body_h=520,
    int_w=724,
    int_d=543,
    int_h=238,
    mouth_w=470,
    mouth_h=140,
    stone_t=30,
    mass_kg=73.0,
    power_kw=10.6,
    front_wall=64,
    rear_wall=90,
    liner_t=1.5,
    outer_t=1.5,
    insulation_mm=(25, 25, 25),
    hearth_z=187,
    flue=True,
    door=True,
    notes=(
        "Published cavity 724 x 543 x 238, mouth 470 x 140, installed height 997 "
        "with flue. Body height 520 mm is the geometry worker's inference: "
        "613 mm carton minus 93 mm of packing. Floor plus roof is 520 - 238 = 282 mm. "
        "Hearth at 187 mm leaves a 95 mm crown, enough for three 25 mm blankets "
        "plus the skins. The unassigned 219 mm callout is not the hearth. "
        "Flue rise is 997 - 520 = 477 mm. Side wall (946-724)/2 = 111 mm."
    ),
)

OVENS: tuple[OvenSpec, ...] = (ARC_LITE, TREAD, DOME_XL)


def by_id(oven_id: str) -> OvenSpec:
    for spec in OVENS:
        if spec.oven_id == oven_id:
            return spec
    raise KeyError(oven_id)
