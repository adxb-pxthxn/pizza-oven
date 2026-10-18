#!/usr/bin/env python3
"""Centerline and front-elevation drawings from the same spec as the solids.

    python3 research/argon-anatomy/drawings/sections.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from cad.reconstructed.spec import OVENS, OvenSpec  # noqa: E402


HERE = Path(__file__).resolve().parent


def _svg(spec: OvenSpec) -> str:
    """Two views, millimetres, 1 px = 1 mm, with a margin."""
    margin = 36
    gap = 48
    width = margin + spec.ext_d + gap + spec.ext_w + margin
    height = margin + max(spec.installed_h, spec.body_h) + 72
    # Centerline: Y to the right, Z up. Origin at the front underside.
    ox = margin
    oy = margin + spec.installed_h

    def z_up(z: float) -> float:
        return oy - z

    hearth = spec.hearth_z
    apex = hearth + spec.int_h
    roof_top = spec.body_h
    parts: list[str] = []
    parts.append(
        f'<rect x="{ox}" y="{z_up(spec.body_h)}" width="{spec.ext_d}" height="{spec.body_h}" '
        'fill="#e7e1d6" stroke="#1c1a17" stroke-width="1.2"/>'
    )
    # Cavity.
    parts.append(
        f'<rect x="{ox + spec.front_wall}" y="{z_up(apex)}" width="{spec.int_d}" height="{spec.int_h}" '
        'fill="#f7f4ee" stroke="#1c1a17" stroke-width="1"/>'
    )
    # Stone.
    parts.append(
        f'<rect x="{ox + spec.front_wall + 4}" y="{z_up(hearth)}" width="{spec.int_d - 8}" height="{spec.stone_t}" '
        'fill="#8aa0b5" stroke="#1c1a17" stroke-width="0.8"/>'
    )
    # Mouth opening on the front of the centerline is the throat height.
    parts.append(
        f'<rect x="{ox}" y="{z_up(hearth + spec.mouth_h)}" width="{spec.front_wall}" height="{spec.mouth_h}" '
        'fill="#f7f4ee" stroke="#1c1a17" stroke-width="0.8"/>'
    )
    # Lintel callout.
    parts.append(
        f'<line x1="{ox + spec.front_wall}" y1="{z_up(hearth + spec.mouth_h)}" '
        f'x2="{ox + spec.front_wall + 28}" y2="{z_up(apex)}" stroke="#8a3b1a" stroke-width="1.2"/>'
    )
    if spec.flue:
        flue_x = ox + spec.front_wall + 70
        parts.append(
            f'<rect x="{flue_x - 28}" y="{z_up(spec.ext_h_published)}" width="56" '
            f'height="{spec.ext_h_published - roof_top}" fill="#d9d3c8" stroke="#1c1a17" stroke-width="1"/>'
        )
    parts.append(
        f'<text x="{ox}" y="{z_up(spec.installed_h) - 8}" font-family="ui-sans-serif,sans-serif" font-size="13" fill="#1c1a17">'
        f'{spec.oven_id} centerline · {spec.model_no}</text>'
    )
    parts.append(
        f'<text x="{ox}" y="{oy + 18}" font-family="ui-sans-serif,sans-serif" font-size="11" fill="#3c3832">'
        f'ext {spec.ext_w:.0f} × {spec.ext_d:.0f} × {spec.ext_h_published:.0f} mm · '
        f'cavity {spec.int_w:.0f} × {spec.int_d:.0f} × {spec.int_h:.0f} · '
        f'mouth {spec.mouth_w:.0f} × {spec.mouth_h:.0f} · '
        f'h/H {spec.mouth_over_apex:.3f}</text>'
    )
    parts.append(
        f'<text x="{ox}" y="{oy + 34}" font-family="ui-sans-serif,sans-serif" font-size="11" fill="#3c3832">'
        f'hearth z {hearth:.0f} mm inferred · side wall {spec.side_wall:.1f} mm · '
        f'insulation { "+".join(str(int(t)) for t in spec.insulation_mm) } mm · '
        f'air gap {spec.air_gap:.1f} mm</text>'
    )

    # Front elevation, to the right.
    fx = ox + spec.ext_d + gap
    parts.append(
        f'<rect x="{fx}" y="{z_up(spec.body_h)}" width="{spec.ext_w}" height="{spec.body_h}" '
        'fill="#e7e1d6" stroke="#1c1a17" stroke-width="1.2"/>'
    )
    mouth_x = fx + (spec.ext_w - spec.mouth_w) / 2
    parts.append(
        f'<rect x="{mouth_x}" y="{z_up(hearth + spec.mouth_h)}" width="{spec.mouth_w}" height="{spec.mouth_h}" '
        'fill="#f7f4ee" stroke="#1c1a17" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{fx}" y="{z_up(spec.installed_h) - 8}" font-family="ui-sans-serif,sans-serif" font-size="13" fill="#1c1a17">'
        f'front elevation</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="100%" height="100%" fill="#f6f3ec"/>'
        + "".join(parts)
        + "</svg>\n"
    )


def main() -> None:
    for spec in OVENS:
        path = HERE / f"{spec.oven_id}-section.svg"
        path.write_text(_svg(spec), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
