"""Show solids for the three concept mock-ups.

These are visual models of the Argon concepts, not the manufacturing assembly.
Lengths are millimetres. The chosen design is modelled separately in cad/tailgate.
"""

from __future__ import annotations

from build123d import Axis, Box, Cylinder, Pos, Rot, Part

from design.tailgate.geom import cap_shell, cylinder_shell, foot_center, frustum_shell, mouth_cutter, tube_along


def _paint(part: Part, rgb: tuple[float, float, float], label: str) -> Part:
    part.label = label
    part.color = None
    part._render_rgb = rgb  # type: ignore[attr-defined]
    return part


WOOD = (0.42, 0.26, 0.16)
WOOD_DARK = (0.30, 0.18, 0.11)
STEEL = (0.70, 0.72, 0.74)
STEEL_DARK = (0.42, 0.44, 0.46)
BRASS = (0.72, 0.55, 0.28)
STONE = (0.78, 0.62, 0.42)
INTERIOR = (0.16, 0.13, 0.11)
RUBBER = (0.12, 0.12, 0.12)


def cask_430() -> list[Part]:
    """Cooper's Dome. Wood frustum, stainless crown, brass hoops."""
    wood = frustum_shell(382.5, 366.5, 292.0, 276.0, 42.0, 300.0)
    wood = wood - mouth_cutter(200, 52, 158.0, 80, y=-330)
    crown = cap_shell(280.0, 115.0, 305.0, 1.6)
    liner = frustum_shell(241.5, 240.0, 241.5, 240.0, 111.5, 166.5)
    liner = liner - mouth_cutter(198, 48, 156.0, 70, y=-250)
    dome_liner = cap_shell(240.0, 110.0, 166.5, 1.6)
    stone = Pos(0, -15, 101.5) * Cylinder(215, 20)
    interior = cap_shell(236.0, 100.0, 170.0, 8.0)
    base = cylinder_shell(340, 336, 8, 36)
    hoop_lo = cylinder_shell(386, 382.5, 58, 86)
    hoop_hi = cylinder_shell(300, 296, 268, 296)
    boss = Pos(0, 0, 412) * Cylinder(42, 16)
    bezel = mouth_ring(width=200, height=52, z=158, y=-348, depth=16)
    parts = [
        _paint(wood, WOOD, "cask-wood"),
        _paint(crown, STEEL, "cask-crown"),
        _paint(liner, STEEL_DARK, "cask-liner"),
        _paint(dome_liner, STEEL_DARK, "cask-liner-dome"),
        _paint(interior, INTERIOR, "cask-interior"),
        _paint(stone, STONE, "cask-stone"),
        _paint(base, STEEL, "cask-base"),
        _paint(hoop_lo, BRASS, "cask-hoop-lo"),
        _paint(hoop_hi, BRASS, "cask-hoop-hi"),
        _paint(boss, BRASS, "cask-boss"),
        _paint(bezel, BRASS, "cask-bezel"),
        _paint(Pos(0, -300, 158) * Box(360, 30, 80), INTERIOR, "cask-throat"),
    ]
    parts.extend(_handles(z=160, radius=390, length=170, grip=WOOD_DARK))
    parts.extend(_legs(socket_z=10, length=760, splay_deg=12, tube_r=16))
    return parts


def angas_binnacle() -> list[Part]:
    """Cool stainless cupola standing in a short blackwood ring."""
    wood = cylinder_shell(381.0, 363.0, 0.0, 215.0)
    wood = wood - mouth_cutter(215, 60, 160.0, 50, y=-360)
    vessel = cylinder_shell(347.7, 346.5, 20.0, 180.0)
    vessel = vessel - mouth_cutter(210, 55, 155.0, 40, y=-340)
    crown = cap_shell(347.5, 230.0, 180.0, 1.6)
    liner = cylinder_shell(241.5, 240.0, 123.0, 178.0)
    liner = liner - mouth_cutter(205, 49, 155.0, 40, y=-230)
    stone = Pos(0, 10, 113.0) * Cylinder(225, 20)
    interior = Pos(0, 0, 200) * Cylinder(230, 90)
    hoop_lo = cylinder_shell(384.0, 381.0, 28.0, 63.0)
    hoop_hi = cylinder_shell(384.0, 381.0, 162.0, 197.0)
    hoop_hi = hoop_hi - mouth_cutter(230, 70, 175.0, 40, y=-370)
    bezel = mouth_ring(width=215, height=58, z=160, y=-372, depth=14)
    boss = Pos(0, 0, 407) * Cylinder(28, 8)
    parts = [
        _paint(wood, WOOD, "angas-wood"),
        _paint(vessel, STEEL, "angas-vessel"),
        _paint(crown, STEEL, "angas-crown"),
        _paint(liner, STEEL_DARK, "angas-liner"),
        _paint(interior, INTERIOR, "angas-interior"),
        _paint(stone, STONE, "angas-stone"),
        _paint(hoop_lo, STEEL_DARK, "angas-hoop-lo"),
        _paint(hoop_hi, STEEL_DARK, "angas-hoop-hi"),
        _paint(bezel, BRASS, "angas-bezel"),
        _paint(Pos(0, -300, 158) * Box(390, 36, 90), INTERIOR, "angas-throat"),
        _paint(boss, BRASS, "angas-boss"),
    ]
    for z in (55.0, 175.0):
        for angle in range(0, 360, 45):
            spool = (
                Rot(axis=Axis.Z, angle=angle)
                * Pos(355, 0, z)
                * Rot(axis=Axis.Y, angle=90)
                * Cylinder(8, 16)
            )
            parts.append(_paint(spool, STEEL, "angas-spool"))
    parts.extend(_handles(z=170, radius=400, length=120, grip=WOOD_DARK))
    parts.extend(_legs(socket_z=8, length=680, splay_deg=16, tube_r=13))
    return parts


def hot_skin_placeholder(od: float, height: float, floor_z: float) -> list[Part]:
    """Stand-in until the unconstrained concept arrives. Not exported."""
    raise RuntimeError("replace with the Argon-optimal solids")


def mouth_ring(width: float = 200, height: float = 52, z: float = 158, y: float = -348, depth: float = 18) -> Part:
    """A brass picture-frame around the mouth, in the front face."""
    outer = Pos(0, y, z) * Box(width * 2 + 28, depth, height * 2 + 22)
    inner = Pos(0, y, z) * Box(width * 2 - 8, depth + 8, height * 2 - 6)
    return outer - inner


def _handles(z: float, radius: float, length: float, grip: tuple[float, float, float]) -> list[Part]:
    """A wood grip on each side, sunk a few millimetres into the shell."""
    parts = []
    for sign in (-1, 1):
        bar = Pos(sign * (radius + length / 2 - 18), 0, z) * Rot(axis=Axis.Y, angle=90) * Cylinder(14, length)
        parts.append(_paint(bar, grip, "handle"))
        collar = Pos(sign * radius, 0, z) * Rot(axis=Axis.Y, angle=90) * Cylinder(20, 10)
        parts.append(_paint(collar, BRASS, "handle-collar"))
    return parts


def _legs(socket_z: float, length: float, splay_deg: float, tube_r: float) -> list[Part]:
    parts = []
    for angle in (30, 150, 270):
        leg = tube_along(length, tube_r, splay_deg, angle, socket_z)
        parts.append(_paint(leg, STEEL, "leg"))
        dx, dy, dz = foot_center(length, splay_deg, angle, socket_z)
        parts.append(_paint(Pos(dx, dy, dz) * Cylinder(tube_r + 6, 12), RUBBER, "foot"))
    return parts


def as_meshes(parts: list[Part]):
    from build123d import export_stl
    from pathlib import Path
    import tempfile

    from design.tailgate.drawings.render_colored import load_stl

    bodies = []
    for part in parts:
        rgb = getattr(part, "_render_rgb", (0.5, 0.5, 0.5))
        color = tuple(int(channel * 255) for channel in rgb)
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as handle:
            path = Path(handle.name)
        export_stl(part, path, tolerance=0.45, angular_tolerance=0.15)
        bodies.append((load_stl(path), color))
        path.unlink()
    return bodies
