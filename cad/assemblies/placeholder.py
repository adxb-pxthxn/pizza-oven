"""Placeholder oven assembly: floor stone, dome shell, insulation layer.

Rebuild from ``OvenParameters``. Nothing in this module hardcodes a
length; every size comes from the parameters object.
"""

from __future__ import annotations

from build123d import Compound

from cad.parameters import ASSEMBLY_LABEL, DEFAULT_PARAMETERS, OvenParameters
from cad.parts.dome_shell import build_dome_shell
from cad.parts.floor_stone import build_floor_stone
from cad.parts.insulation import build_insulation_layer


def build_placeholder_assembly(params: OvenParameters = DEFAULT_PARAMETERS) -> Compound:
    """Return the three solids as one labelled STEP assembly."""
    return Compound(
        children=[
            build_floor_stone(params),
            build_dome_shell(params),
            build_insulation_layer(params),
        ],
        label=ASSEMBLY_LABEL,
    )
