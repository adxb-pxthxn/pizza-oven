"""Placeholder baking-floor slab. A box, not a specified stone product."""

from __future__ import annotations

from build123d import Box, Color, Part, Pos

from cad.parameters import FLOOR_STONE_LABEL, OvenParameters


def build_floor_stone(params: OvenParameters) -> Part:
    """Slab centred on X/Y with its top face on z = 0."""
    stone = Pos(0, 0, -params.stone_thickness_mm / 2) * Box(
        params.stone_length_mm,
        params.stone_width_mm,
        params.stone_thickness_mm,
    )
    stone.label = FLOOR_STONE_LABEL
    # Display tint only. It does not select a material.
    stone.color = Color(0.76, 0.60, 0.42)
    return stone
