"""Master dimensions for the parametric oven model.

Every length in this package is millimetres. Part modules read these
fields and do not keep a second copy of a number.

The defaults are a generic placeholder: a square floor slab under a
half-cylinder shell and a concentric insulation layer. They are round
numbers chosen so a parameter edit is obvious. They are not a capacity,
a material specification, or a copy of any commercial oven.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

FLOOR_STONE_LABEL = "floor_stone"
DOME_SHELL_LABEL = "dome_shell"
INSULATION_LAYER_LABEL = "insulation_layer"
ASSEMBLY_LABEL = "placeholder_oven_assembly"


@dataclass(frozen=True)
class OvenParameters:
    """Placeholder envelope. Replace the defaults when a design is specified.

    Axis convention for the built assembly:
    - X is across the floor.
    - Y is along the dome axis (floor depth).
    - Z is up. The stone occupies z <= 0 and the shells sit on z = 0.
    """

    # Square slab so changing one side is easy to see in the bounding box.
    stone_length_mm: float = 300.0
    stone_width_mm: float = 300.0
    stone_thickness_mm: float = 20.0

    # Half-cylinder shell. Wall thickness is a solid placeholder, not a
    # sheet-metal gauge and not a chosen refractory.
    dome_inner_radius_mm: float = 160.0
    dome_wall_thickness_mm: float = 12.0
    dome_length_mm: float = 320.0

    # Concentric layer outside the dome shell, same axial length.
    insulation_thickness_mm: float = 40.0

    def __post_init__(self) -> None:
        for name, value in (
            ("stone_length_mm", self.stone_length_mm),
            ("stone_width_mm", self.stone_width_mm),
            ("stone_thickness_mm", self.stone_thickness_mm),
            ("dome_inner_radius_mm", self.dome_inner_radius_mm),
            ("dome_wall_thickness_mm", self.dome_wall_thickness_mm),
            ("dome_length_mm", self.dome_length_mm),
            ("insulation_thickness_mm", self.insulation_thickness_mm),
        ):
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite length in millimetres, got {value!r}")

    @property
    def dome_outer_radius_mm(self) -> float:
        return self.dome_inner_radius_mm + self.dome_wall_thickness_mm

    @property
    def insulation_inner_radius_mm(self) -> float:
        return self.dome_outer_radius_mm

    @property
    def insulation_outer_radius_mm(self) -> float:
        return self.dome_outer_radius_mm + self.insulation_thickness_mm


DEFAULT_PARAMETERS = OvenParameters()
