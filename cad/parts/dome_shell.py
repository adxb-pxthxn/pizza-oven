"""Placeholder dome shell: a half-cylinder of constant wall thickness."""

from __future__ import annotations

from build123d import Color, Compound

from cad.parameters import DOME_SHELL_LABEL, OvenParameters
from cad.parts.shell import half_cylinder_shell


def build_dome_shell(params: OvenParameters) -> Compound:
    """Half-tube centred on X/Y, flat face on z = 0, crown toward +Z."""
    shell = half_cylinder_shell(
        params.dome_inner_radius_mm,
        params.dome_outer_radius_mm,
        params.dome_length_mm,
    )
    shell.label = DOME_SHELL_LABEL
    shell.color = Color(0.45, 0.47, 0.50)
    return shell
