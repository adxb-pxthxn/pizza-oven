"""Placeholder insulation layer wrapped around the dome shell.

The layer is a second half-tube. Its inner radius is the dome outer
radius, so the two solids meet on a shared face and do not overlap.
"""

from __future__ import annotations

from build123d import Color, Compound

from cad.parameters import INSULATION_LAYER_LABEL, OvenParameters
from cad.parts.shell import half_cylinder_shell


def build_insulation_layer(params: OvenParameters) -> Compound:
    layer = half_cylinder_shell(
        params.insulation_inner_radius_mm,
        params.insulation_outer_radius_mm,
        params.dome_length_mm,
    )
    layer.label = INSULATION_LAYER_LABEL
    layer.color = Color(0.93, 0.88, 0.72)
    return layer
