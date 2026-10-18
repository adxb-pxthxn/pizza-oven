#!/usr/bin/env python3
"""Shade the manufacturing assembly from its coloured solids."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
from build123d import export_stl

from cad.tailgate.model import build
from design.tailgate.drawings.render_colored import load_stl, render_bodies

OUT = Path(__file__).resolve().parents[1] / "concepts"


EXTERIOR = {
    "base-pan", "base-lip", "shell-skirt", "shell-joggle", "shell-crown",
    "cinch-band", "handle-port", "handle-starboard",
    "handle-port-ferrule", "handle-starboard-ferrule",
    "badge", "mouth-frame", "peel-landing", "stub-foot",
    "dowel-a", "dowel-b",
}


def _bodies(assembly, labels=None):
    bodies = []
    for part in assembly.children:
        if labels is not None and part.label not in labels:
            continue
        color = part.color
        if color is None:
            rgb = (140, 140, 140)
        else:
            channels = tuple(color)[:3]
            rgb = tuple(int(max(0, min(255, channel * 255))) for channel in channels)
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as handle:
            path = Path(handle.name)
        export_stl(part, path, tolerance=0.55, angular_tolerance=0.15)
        bodies.append((load_stl(path), rgb))
        path.unlink()
    return bodies


def _frame(assembly):
    boxes = [p.bounding_box() for p in assembly.children if p.label and "leg" not in p.label and "stub" not in p.label]
    lo = np.array([min(b.min.X for b in boxes) - 30, min(b.min.Y for b in boxes) - 30, min(b.min.Z for b in boxes) - 10])
    hi = np.array([max(b.max.X for b in boxes) + 30, max(b.max.Y for b in boxes) + 30, max(b.max.Z for b in boxes) + 20])
    return lo, hi


def main() -> None:
    table = build(deployed_legs=False)
    render_bodies(
        _bodies(table, EXTERIOR),
        OUT / "angas-430.png",
        title="Angas 430",
        subtitle="The oven to build. Stainless crown, brass cinch, jarrah handles.",
        frame=_frame(table),
        size=1400,
        azimuth_deg=200,
        elevation_deg=28,
    )
    exploded = build(explode=160, deployed_legs=False)
    exploded_labels = EXTERIOR | {"floor-cordierite", "stone-pan"}
    render_bodies(
        _bodies(exploded, exploded_labels),
        OUT / "angas-430-exploded.png",
        title="Angas 430, crown lifted",
        subtitle="The cinch comes off. The stone comes out from above.",
        frame=_frame(exploded),
        size=1400,
        azimuth_deg=200,
        elevation_deg=26,
    )
    cutaway = build(cutaway=True, deployed_legs=False)
    render_bodies(
        _bodies(cutaway),
        OUT / "angas-430-cutaway.png",
        title="Angas 430, cutaway",
        subtitle="1.2 liner, 75 AES + 25 board in the wall, 100 AES in the crown.",
        frame=_frame(cutaway),
        size=1400,
        azimuth_deg=210,
        elevation_deg=24,
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
