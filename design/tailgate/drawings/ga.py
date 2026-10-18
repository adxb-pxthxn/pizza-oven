#!/usr/bin/env python3
"""General-arrangement sheets for the Angas 430. Units on the sheet are millimetres.

    PYTHONPATH=. python3 design/tailgate/drawings/ga.py
"""

from __future__ import annotations

import math
from pathlib import Path

from cad.tailgate.spec import SPEC, skin_temperature

OUT = Path(__file__).resolve().parent
SHEET_W = 420
SHEET_H = 297


def _header(title: str, sheet: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" height="{SHEET_H}mm" viewBox="0 0 {SHEET_W} {SHEET_H}">
<rect width="{SHEET_W}" height="{SHEET_H}" fill="#f7f4ee"/>
<rect x="8" y="8" width="404" height="281" fill="none" stroke="#1c1a17" stroke-width="0.6"/>
<rect x="8" y="252" width="404" height="37" fill="none" stroke="#1c1a17" stroke-width="0.4"/>
<text x="14" y="266" font-family="Georgia, serif" font-size="5.2" fill="#1c1a17">{title}</text>
<text x="14" y="274" font-family="Georgia, serif" font-size="3.2" fill="#5c5348">Angas 430 · Adib's tailgate oven · gas, circular dome · sheet {sheet}</text>
<text x="14" y="282" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Dimensions mm. Scale as noted. Hardware CERN-OHL-P v2. This sheet CC-BY-4.0. 18 Oct 2026.</text>
<text x="300" y="266" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Do not scale the drawing.</text>
<text x="300" y="274" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Certified burner, FFD, regulator, hose: bought.</text>
<text x="300" y="282" font-family="Georgia, serif" font-size="2.8" fill="#5c5348">Crown lifts at the brass cinch. Stone does not pass the mouth.</text>
"""


def _footer() -> str:
    return "</svg>\n"


def _dim(x1, y1, x2, y2, text, tx, ty):
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#1c1a17" stroke-width="0.25"/>'
        f'<text x="{tx:.2f}" y="{ty:.2f}" font-family="Georgia, serif" font-size="3.1" fill="#1c1a17">{text}</text>'
    )


def arrangement() -> str:
    """Front, side and top at 1:8, which keeps the handle span on an A3 sheet."""
    s = SPEC
    k = 1 / 8
    parts = [_header("General arrangement — front, side, top", "1 of 4"),
             '<text x="14" y="20" font-family="Georgia, serif" font-size="3.4" fill="#1c1a17">Scale 1:8</text>']

    # Front. Origin of the view at the oven centreline, underside of the pan.
    ox, oy = 78, 200
    r = s.outer_radius * k
    # Paper Y grows down, model Z grows up.
    def fz(z):
        return oy - z * k

    parts.append(
        f'<rect x="{ox - r}" y="{fz(s.spring_z)}" width="{2*r:.2f}" height="{(s.spring_z - s.base_t)*k:.2f}" '
        f'fill="#efe6d6" stroke="#1c1a17" stroke-width="0.45"/>'
    )
    # Dome as an arc sitting on the skirt.
    rise = s.dome_rise * k
    parts.append(
        f'<path d="M {ox - r:.2f} {fz(s.spring_z):.2f} '
        f'A {r:.2f} {rise:.2f} 0 0 1 {ox + r:.2f} {fz(s.spring_z):.2f}" '
        f'fill="#e4e2de" stroke="#1c1a17" stroke-width="0.45"/>'
    )
    # Mouth
    mw, mh = s.mouth_w * k, s.mouth_h * k
    parts.append(
        f'<rect x="{ox - mw/2:.2f}" y="{fz(s.hearth_z + s.mouth_h):.2f}" width="{mw:.2f}" height="{mh:.2f}" '
        f'fill="#1c1a17" stroke="#c4a46a" stroke-width="0.8"/>'
    )
    # Handles
    for sign in (-1, 1):
        hx = ox + sign * (s.outer_radius + s.handle_standoff) * k
        parts.append(
            f'<rect x="{hx - (0 if sign > 0 else s.handle_len * k):.2f}" y="{fz(s.hearth_z + 40 + s.handle_od/2):.2f}" '
            f'width="{s.handle_len * k:.2f}" height="{s.handle_od * k:.2f}" rx="1.2" fill="#6b3e28" stroke="#1c1a17" stroke-width="0.25"/>'
        )
    # Band
    by = fz(s.spring_z - s.joggle_h)
    parts.append(f'<line x1="{ox - r:.2f}" y1="{by:.2f}" x2="{ox + r:.2f}" y2="{by:.2f}" stroke="#8a6a32" stroke-width="1.3"/>')
    parts.append('<text x="16" y="108" font-family="Georgia, serif" font-size="3.6" fill="#1c1a17">Front, mouth toward you</text>')
    parts.append(_dim(ox - r, fz(-8), ox + r, fz(-8), f"Ø {s.outer_diameter:.0f}", ox - 8, fz(-12)))
    parts.append(_dim(ox + r + 8, fz(0), ox + r + 8, fz(s.body_height), f"{s.body_height:.0f} high", ox + r + 10, fz(s.body_height / 2)))
    parts.append(_dim(ox - mw/2, fz(s.hearth_z - 6), ox + mw/2, fz(s.hearth_z - 6), f"mouth {s.mouth_w:.0f} × {s.mouth_h:.0f}", ox - 16, fz(s.hearth_z - 10)))

    # Side. Mouth to the left.
    sx, sy = 250, 200
    def sz(z):
        return sy - z * k
    depth = s.outer_diameter * k
    parts.append(
        f'<rect x="{sx}" y="{sz(s.spring_z)}" width="{depth:.2f}" height="{(s.spring_z)*k:.2f}" '
        f'fill="#efe6d6" stroke="#1c1a17" stroke-width="0.45"/>'
    )
    parts.append(
        f'<path d="M {sx:.2f} {sz(s.spring_z):.2f} Q {sx + depth/2:.2f} {sz(s.outer_apex_z):.2f} {sx + depth:.2f} {sz(s.spring_z):.2f}" '
        f'fill="#e4e2de" stroke="#1c1a17" stroke-width="0.45"/>'
    )
    parts.append(f'<rect x="{sx - 6:.2f}" y="{sz(s.hearth_z + s.mouth_h):.2f}" width="8" height="{mh:.2f}" fill="#1c1a17"/>')
    parts.append('<text x="248" y="36" font-family="Georgia, serif" font-size="3.6" fill="#1c1a17">Side, mouth at left</text>')
    parts.append(_dim(sx, sz(-8), sx + depth, sz(-8), f"Ø {s.outer_diameter:.0f} deep", sx + 20, sz(-12)))

    # Top
    tx, ty = 78, 78
    parts.append(f'<circle cx="{tx}" cy="{ty}" r="{r}" fill="#efe6d6" stroke="#1c1a17" stroke-width="0.45"/>')
    parts.append(f'<circle cx="{tx + 2}" cy="{ty}" r="{(s.floor_d/2)*k:.2f}" fill="none" stroke="#8a6a32" stroke-width="0.3" stroke-dasharray="1.2 0.8"/>')
    for sign in (-1, 1):
        parts.append(
            f'<rect x="{tx + sign * r + (0 if sign > 0 else -s.handle_len*k):.2f}" y="{ty - 2:.2f}" '
            f'width="{s.handle_len * k:.2f}" height="4" fill="#6b3e28"/>'
        )
    parts.append('<text x="16" y="34" font-family="Georgia, serif" font-size="3.6" fill="#1c1a17">Top. Dashed circle is the 430 stone. Handles left and right.</text>')
    parts.append(
        f'<text x="200" y="70" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">'
        f'Floor Ø{s.floor_d:.0f}. Chamber Ø{s.chamber_id:.0f}. Apex {s.apex_h:.0f}. Mouth/apex {s.mouth_over_apex:.3f}.</text>'
    )
    parts.append(
        f'<text x="200" y="78" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">'
        f'Handle span {s.handle_span:.0f}. Fits between the arches (1224) with the handles on.</text>'
    )
    parts.append(
        '<text x="200" y="90" font-family="Georgia, serif" font-size="3.2" fill="#5c5348">'
        'Plan is wider than the lowered tailgate is deep (517). It stands on the ground or a table.</text>'
    )
    parts.append(_footer())
    return "\n".join(parts)


def section() -> str:
    s = SPEC
    k = 1 / 4.5
    ox, oy = 150, 230

    def z(value):
        return oy - value * k

    def x(radius):
        return ox + radius * k

    wall = skin_temperature(s.wall_aes, s.wall_casi)
    crown = skin_temperature(s.crown_aes)
    parts = [_header("Section through the centreline — insulation and the cinch", "2 of 4"),
             '<text x="14" y="20" font-family="Georgia, serif" font-size="3.4" fill="#1c1a17">Scale 1:4.5. Right half shown. Mouth is to the left of this view.</text>']
    # Layers as closed shapes, axis at ox.
    r_liner_out = s.chamber_r + s.liner_t
    r_aes = r_liner_out + s.wall_aes
    r_ins = r_liner_out + s.insulation_t
    r_skin = s.outer_radius
    # Skirt block
    def block(r0, r1, z0, z1, fill):
        return (
            f'<rect x="{x(r0):.2f}" y="{z(z1):.2f}" width="{(r1-r0)*k:.2f}" height="{(z1-z0)*k:.2f}" '
            f'fill="{fill}" stroke="#1c1a17" stroke-width="0.2"/>'
        )
    parts.append(block(0, s.outer_radius, 0, s.base_t, "#8d9398"))
    parts.append(block(0, s.chamber_r, s.base_t, s.base_t + s.floor_aes, "#e6d7a8"))
    parts.append(block(0, s.chamber_r, s.base_t + s.floor_aes, s.base_t + s.floor_aes + s.floor_casi, "#d9d3c8"))
    parts.append(block(0, s.floor_d / 2, s.hearth_z - s.floor_t, s.hearth_z, "#c4a46a"))
    parts.append(block(s.chamber_r, r_liner_out, s.hearth_z, s.spring_z, "#8d9398"))
    parts.append(block(r_liner_out, r_aes, s.hearth_z, s.spring_z, "#e6d7a8"))
    parts.append(block(r_aes, r_ins, s.hearth_z, s.spring_z, "#d9d3c8"))
    parts.append(block(r_ins, r_skin, s.base_t, s.spring_z - s.joggle_h, "#b7bcc1"))
    # Joggle: the crown lip sits inboard of the skin and meets it.
    parts.append(block(joggle_in := r_ins - s.skin_t, r_ins, s.spring_z - s.joggle_h, s.spring_z, "#9aa0a6"))
    # Brass cinch over the joint, slightly proud of the skin.
    parts.append(block(r_skin, r_skin + s.band_t, s.spring_z - s.joggle_h - 4, s.spring_z - s.joggle_h - 4 + s.band_w, "#8a6a32"))
    # Dome quads share the spring line with the wall, so there is no white gap.
    apex_in = s.inner_apex_z
    parts.append(
        f'<polygon points="'
        f'{x(0):.2f},{z(apex_in):.2f} '
        f'{x(s.chamber_r):.2f},{z(s.spring_z):.2f} '
        f'{x(r_liner_out):.2f},{z(s.spring_z):.2f} '
        f'{x(0):.2f},{z(apex_in + s.liner_t):.2f}" '
        f'fill="#8d9398" stroke="#1c1a17" stroke-width="0.2"/>'
    )
    parts.append(
        f'<polygon points="'
        f'{x(0):.2f},{z(apex_in + s.liner_t):.2f} '
        f'{x(r_liner_out):.2f},{z(s.spring_z):.2f} '
        f'{x(r_ins):.2f},{z(s.spring_z):.2f} '
        f'{x(0):.2f},{z(s.outer_apex_z - s.skin_t):.2f}" '
        f'fill="#e6d7a8" stroke="#1c1a17" stroke-width="0.2"/>'
    )
    parts.append(
        f'<polygon points="'
        f'{x(0):.2f},{z(s.outer_apex_z - s.skin_t):.2f} '
        f'{x(r_ins):.2f},{z(s.spring_z):.2f} '
        f'{x(r_skin):.2f},{z(s.spring_z - s.joggle_h):.2f} '
        f'{x(0):.2f},{z(s.outer_apex_z):.2f}" '
        f'fill="#b7bcc1" stroke="#1c1a17" stroke-width="0.2"/>'
    )
    # Axis
    parts.append(f'<line x1="{ox:.2f}" y1="{z(s.outer_apex_z)-4:.2f}" x2="{ox:.2f}" y2="{z(-6):.2f}" stroke="#8a6a32" stroke-width="0.25" stroke-dasharray="2 1"/>')
    notes = [
        (18, 40, "Stack at the wall, gas outward"),
        (18, 48, f"1.2 liner · {s.wall_aes:.0f} AES · {s.wall_casi:.0f} calcium silicate · 1.2 skin"),
        (18, 56, f"Skin about {wall['skin_C']:.0f}°C. A short touch, not a lean."),
        (18, 68, "Stack at the crown"),
        (18, 76, f"1.2 liner · {s.crown_aes:.0f} AES · 1.2 skin. No board."),
        (18, 84, f"Skin about {crown['skin_C']:.0f}°C. Same total thickness, so one outer surface."),
        (18, 96, "Cinch"),
        (18, 104, f"Brass band {s.band_w:.0f} × {s.band_t:.0f}. Joggle {s.joggle_h:.0f} above the mouth."),
        (18, 112, "Two dowels lock the crown for the drive. Lift the band, lift the crown, lift the stone."),
        (18, 124, "Floor"),
        (18, 132, f"Ø{s.floor_d:.0f} × {s.floor_t:.0f} cordierite, offset 8 mm to leave a burner crescent."),
        (18, 140, "Under it: 25 calcium silicate, 25 AES, 1.5 pan."),
        (250, 40, "What a hand holds"),
        (250, 48, "Jarrah bars, 32 × 220, on 35 mm stands."),
        (250, 56, "The shell is not a touch surface."),
        (250, 68, "Gas"),
        (250, 76, f"{s.burner_kw:.1f} kW bought burner, FFD, LCC27 at 2.75 kPa."),
        (250, 84, "No jet is drawn. No wood fire."),
        (250, 96, "Colours"),
        (250, 104, "Grey steel. Cream AES. Pale board. Tan stone. Brass band."),
    ]
    for px, py, text in notes:
        parts.append(f'<text x="{px}" y="{py}" font-family="Georgia, serif" font-size="3.3" fill="#1c1a17">{text}</text>')
    parts.append(_footer())
    return "\n".join(parts)


def exploded() -> str:
    s = SPEC
    parts = [_header("Exploded crown — the cinch is the joint", "3 of 4")]
    # Five disks stacked, labelled, not to a false scale of separation.
    labels = [
        (200, 40, 70, "#6b3e28", "Jarrah handles and brass ferrules, off to the side"),
        (150, 58, 150, "#c4a46a", "Brass cinch band, 35 × 3, and two road dowels"),
        (130, 78, 180, "#b7bcc1", "304 crown, 1.2 skin, lifts off the joggle"),
        (120, 100, 200, "#e6d7a8", "75 mm AES crown blanket, lifts with the crown"),
        (110, 124, 220, "#8d9398", "304 liner dome, lifts with the crown"),
        (100, 150, 240, "#efe6d6", "Skirt, wall insulation, floor, stone — stays put"),
        (90, 178, 260, "#5c5348", "Base pan, stub feet or the 750 mm tripod"),
    ]
    for width, y, span, fill, text in labels:
        parts.append(f'<rect x="{(210-span/2):.1f}" y="{y}" width="{span}" height="14" rx="2" fill="{fill}" stroke="#1c1a17" stroke-width="0.3"/>')
        parts.append(f'<text x="24" y="{y+9}" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">{text}</text>')
    parts.append('<text x="24" y="214" font-family="Georgia, serif" font-size="3.3" fill="#1c1a17">Order of the evening: legs or table, crown stays on, burner lights. Order of a clean: band off, crown off, stone out.</text>')
    parts.append('<text x="24" y="222" font-family="Georgia, serif" font-size="3.3" fill="#1c1a17">On the road the two dowels and the band bolt keep the crown from walking. They are finger parts, not a tool kit.</text>')
    parts.append(_footer())
    return "\n".join(parts)


def stowed() -> str:
    """Plan of the Shark tub between the arches, oven and legs."""
    s = SPEC
    # Tub floor we can use: 1520 long, 1224 between arches. Scale to fit.
    tub_l, tub_w = 1520.0, 1224.0
    k = 200 / tub_l
    ox, oy = 30, 36
    parts = [_header("Stowed in the BYD Shark 6 tub, between the wheel arches", "4 of 4"),
             '<text x="14" y="22" font-family="Georgia, serif" font-size="3.2" fill="#1c1a17">Plan. Scale about 1:7.6. Cab is to the left. Tailgate to the right.</text>']
    parts.append(
        f'<rect x="{ox}" y="{oy}" width="{tub_l*k:.1f}" height="{tub_w*k:.1f}" fill="#e7e2d8" stroke="#1c1a17" stroke-width="0.6"/>'
    )
    # Wheel arch notches, schematic,  (1500-1224)/2 = 138 mm each side, drawn as the tub we already clipped.
    cx = ox + 360 * k
    cy = oy + tub_w * k / 2
    r = s.outer_radius * k
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#efe6d6" stroke="#1c1a17" stroke-width="0.5"/>')
    parts.append(f'<text x="{cx-12:.1f}" y="{cy:.1f}" font-family="Georgia, serif" font-size="3" fill="#1c1a17">oven</text>')
    # Legs alongside, 750 long
    for index in range(3):
        lx = cx + r + 8 + index * 6
        parts.append(
            f'<rect x="{lx:.1f}" y="{cy - s.leg_len*k/2:.1f}" width="3.2" height="{s.leg_len*k:.1f}" fill="#8d9398" stroke="#1c1a17" stroke-width="0.2"/>'
        )
    parts.append(f'<text x="{cx + r + 4:.1f}" y="{cy - s.leg_len*k/2 - 3:.1f}" font-family="Georgia, serif" font-size="2.8" fill="#1c1a17">3 legs</text>')
    # Height note
    parts.append(
        f'<text x="250" y="230" font-family="Georgia, serif" font-size="3.3" fill="#1c1a17">'
        f'Body {s.body_height:.0f} high, stub feet 65, stowed about 385. Tub is 517 deep.</text>'
    )
    parts.append(
        '<text x="250" y="238" font-family="Georgia, serif" font-size="3.3" fill="#1c1a17">'
        'Tie to the factory points. Stone can ride in the oven; it is the heavy loose part.</text>'
    )
    parts.append(
        '<text x="250" y="250" font-family="Georgia, serif" font-size="3.3" fill="#5c5348">'
        'The lowered tailgate is 517 deep. This plan is 625. Cook beside the ute, prep on the tailgate.</text>'
    )
    parts.append(_footer())
    return "\n".join(parts)


def main() -> None:
    sheets = {
        "ga-arrangement.svg": arrangement(),
        "ga-section.svg": section(),
        "ga-exploded.svg": exploded(),
        "ga-stowed.svg": stowed(),
    }
    for name, svg in sheets.items():
        path = OUT / name
        path.write_text(svg, encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
