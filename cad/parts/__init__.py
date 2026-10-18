"""Placeholder solids. Each builder takes ``OvenParameters`` and returns a labelled part."""

from cad.parts.dome_shell import build_dome_shell
from cad.parts.floor_stone import build_floor_stone
from cad.parts.insulation import build_insulation_layer

__all__ = ["build_dome_shell", "build_floor_stone", "build_insulation_layer"]
