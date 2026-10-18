"""Axisymmetric profiles. The rz plane has r along X and z along Y for the sketch."""

from __future__ import annotations

import math

from build123d import Axis, BuildLine, BuildPart, BuildSketch, Line, Plane, make_face, revolve


def ellipse_points(radius: float, rise: float, z0: float, count: int = 48) -> list[tuple[float, float]]:
    """Inner dome profile from the apex (r=0) down to the springing (r=radius, z=z0).

    z0 is the height of the spring line. The apex is at z0 + rise.
    """
    if radius <= 0 or rise <= 0:
        raise ValueError("ellipse needs a positive radius and rise")
    points = []
    for index in range(count + 1):
        theta = math.pi / 2 * (1 - index / count)  # pi/2 at apex, 0 at spring
        r = radius * math.cos(theta)
        z = z0 + rise * math.sin(theta)
        points.append((r, z))
    return points


def offset_open(points: list[tuple[float, float]], distance: float) -> list[tuple[float, float]]:
    """Offset an open polyline to the right of its direction by `distance`.

    For a profile that walks from the apex down toward the floor, the right-hand
    side is outside the chamber.
    """
    if len(points) < 2:
        raise ValueError("need at least two points")
    normals = []
    for index, (r, z) in enumerate(points):
        if index == 0:
            dr = points[1][0] - r
            dz = points[1][1] - z
        elif index == len(points) - 1:
            dr = r - points[index - 1][0]
            dz = z - points[index - 1][1]
        else:
            dr = points[index + 1][0] - points[index - 1][0]
            dz = points[index + 1][1] - points[index - 1][1]
        length = math.hypot(dr, dz)
        if length == 0:
            raise ValueError("duplicate profile point")
        # Left-hand normal. Walking from the apex down to the spring line,
        # this points out of the chamber: up at the crown, out at the equator.
        normals.append((-dz / length, dr / length))
    offset = []
    for (r, z), (nr, nz) in zip(points, normals):
        rr = r + distance * nr
        if rr < 0:
            rr = 0.0
        offset.append((rr, z + distance * nz))
    return offset


def revolve_loop(loop: list[tuple[float, float]]):
    """Revolve a closed rz loop around Z. Consecutive points must differ."""
    cleaned = [loop[0]]
    for point in loop[1:]:
        if math.hypot(point[0] - cleaned[-1][0], point[1] - cleaned[-1][1]) > 1e-6:
            cleaned.append(point)
    if math.hypot(cleaned[0][0] - cleaned[-1][0], cleaned[0][1] - cleaned[-1][1]) > 1e-6:
        cleaned.append(cleaned[0])
    with BuildPart() as part:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                for start, end in zip(cleaned, cleaned[1:]):
                    Line(start, end)
            make_face()
        revolve(axis=Axis.Z)
    return part.part


def cylinder_shell(r_in: float, r_out: float, z0: float, z1: float):
    """Closed cylindrical wall. r_out > r_in, z1 > z0."""
    if r_out <= r_in or z1 <= z0:
        raise ValueError("cylinder shell is inside out")
    return revolve_loop([
        (r_in, z0),
        (r_out, z0),
        (r_out, z1),
        (r_in, z1),
        (r_in, z0),
    ])


def shell_between(inner: list[tuple[float, float]], outer: list[tuple[float, float]]):
    """Closed loop: up the inner profile (reversed), across, down the outer profile."""
    loop = list(reversed(inner)) + list(outer)
    loop.append(loop[0])
    return revolve_loop(loop)
