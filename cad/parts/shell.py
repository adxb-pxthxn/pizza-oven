"""Shared half-cylinder shell for the placeholder dome and insulation.

build123d ``Cylinder`` is centred on Z. ``split`` on ``Plane.XZ`` with
``Keep.TOP`` keeps the negative-Y half of that tube. A -90 degree
rotation about X then lays the axis along Y and points the crown at +Z,
with the flat face on z = 0.
"""

from __future__ import annotations

from build123d import Compound, Cylinder, Keep, Plane, Rot, split


def half_cylinder_shell(inner_radius_mm: float, outer_radius_mm: float, length_mm: float) -> Compound:
    """Return one solid half-tube. Radii and length are millimetres."""
    if outer_radius_mm <= inner_radius_mm:
        raise ValueError(
            f"outer radius ({outer_radius_mm} mm) must be greater than "
            f"inner radius ({inner_radius_mm} mm)"
        )
    if length_mm <= 0:
        raise ValueError(f"length must be positive millimetres, got {length_mm}")

    tube = Cylinder(outer_radius_mm, length_mm) - Cylinder(inner_radius_mm, length_mm)
    negative_y_half = split(tube, bisect_by=Plane.XZ, keep=Keep.TOP)
    return Rot(-90, 0, 0) * negative_y_half
