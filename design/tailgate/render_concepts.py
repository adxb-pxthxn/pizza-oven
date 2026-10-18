#!/usr/bin/env python3
"""Render the concept mock-ups. Run after the third concept exists too.

    PYTHONPATH=. .venv/bin/python design/tailgate/render_concepts.py cask
    PYTHONPATH=. .venv/bin/python design/tailgate/render_concepts.py angas
    PYTHONPATH=. .venv/bin/python design/tailgate/render_concepts.py optimal
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from design.tailgate.concepts_model import angas_binnacle, as_meshes, cask_430
from design.tailgate.drawings.render_colored import render_bodies

OUT = Path(__file__).resolve().parent / "concepts"
def _frame(parts):
    boxes = [p.bounding_box() for p in parts if p.label not in {"leg", "foot"}]
    lo = np.array([min(b.min.X for b in boxes), min(b.min.Y for b in boxes), min(b.min.Z for b in boxes)])
    hi = np.array([max(b.max.X for b in boxes), max(b.max.Y for b in boxes), max(b.max.Z for b in boxes)])
    pad = np.array([40.0, 40.0, 30.0])
    return lo - pad, hi + pad


def _one(name: str, parts, title: str, subtitle: str) -> None:
    print(f"meshing {name} ({len(parts)} solids)")
    bodies = as_meshes(parts)
    dest = OUT / f"{name}.png"
    render_bodies(
        bodies,
        dest,
        title=title,
        subtitle=subtitle,
        frame=_frame(parts),
        size=1400,
        azimuth_deg=198,
        elevation_deg=22,
    )
    print("wrote", dest)


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in {"cask", "all"}:
        _one(
            "cask-430",
            cask_430(),
            "Cooper's Dome  ·  Cask-430",
            "Turned-wood body, stainless crown. Concept, not the manufacturing model.",
        )
    if which in {"angas", "all"}:
        _one(
            "angas-binnacle",
            angas_binnacle(),
            "Angas Binnacle",
            "Cool stainless cupola in a blackwood ring. Concept, not the manufacturing model.",
        )
    if which == "optimal":
        from design.tailgate.concepts_model import optimal_concept
        _one("argon-optimal", optimal_concept(), "Argon optimal", "Unconstrained by the wood look.")


if __name__ == "__main__":
    main()
