"""Small solids shared by the concept mock-ups. Millimetres."""

from __future__ import annotations

import math

from build123d import Axis, Box, BuildLine, BuildPart, BuildSketch, Cylinder, Line, Plane, Pos, Rot, Sphere, make_face, revolve


def _revolve_loop(points: list[tuple[float, float]]):
    with BuildPart() as part:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                for start, end in zip(points, points[1:]):
                    Line(start, end)
            make_face()
        revolve(axis=Axis.Z)
    return part.part


def frustum_shell(r_outer_bot: float, r_inner_bot: float, r_outer_top: float, r_inner_top: float,
                  z_bot: float, z_top: float):
    """Closed radial wall between two heights. All radii are from the Z axis."""
    return _revolve_loop([
        (r_inner_bot, z_bot),
        (r_outer_bot, z_bot),
        (r_outer_top, z_top),
        (r_inner_top, z_top),
        (r_inner_bot, z_bot),
    ])


def cylinder_shell(r_outer: float, r_inner: float, z_bot: float, z_top: float):
    return frustum_shell(r_outer, r_inner, r_outer, r_inner, z_bot, z_top)


def cap_shell(chord_radius: float, rise: float, z_base: float, thickness: float):
    """Shallow spherical cap shell. chord_radius is the opening radius at z_base."""
    radius = (chord_radius ** 2 + rise ** 2) / (2 * rise)
    center_z = z_base + rise - radius
    outer = Pos(0, 0, center_z) * Sphere(radius)
    inner = Pos(0, 0, center_z) * Sphere(max(radius - thickness, 1.0))
    # Keep the cap above the chord, plus a little so the shell meets the wall.
    keeper = Pos(0, 0, z_base + rise) * Box(chord_radius * 4, chord_radius * 4, rise * 2 + 4)
    return (outer - inner) & keeper


def mouth_cutter(half_width: float, half_height: float, z_center: float, reach: float, y: float = -340):
    """Shallow box through the front wall only. `reach` is the Y thickness."""
    return Pos(0, y, z_center) * Box(half_width * 2, reach, half_height * 2)


def tube_along(length: float, radius: float, splay_deg: float, yaw_deg: float, z0: float):
    """A leg whose top is at the origin height z0 and whose foot is down and out."""
    return (
        Pos(0, 0, z0)
        * Rot(axis=Axis.Z, angle=yaw_deg)
        * Rot(axis=Axis.X, angle=splay_deg)
        * Pos(0, 0, -length / 2)
        * Cylinder(radius, length)
    )


def foot_center(length: float, splay_deg: float, yaw_deg: float, z0: float) -> tuple[float, float, float]:
    splay = math.radians(splay_deg)
    yaw = math.radians(yaw_deg)
    dx = math.sin(yaw) * math.sin(splay) * length
    dy = math.cos(yaw) * math.sin(splay) * length
    dz = -math.cos(splay) * length
    return dx, dy, z0 + dz
