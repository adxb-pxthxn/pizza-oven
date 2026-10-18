"""Envelope checks for the reconstructed ovens.

These do not claim a measured teardown. They lock the published numbers the
solids are required to reproduce, and the inferred splits the spec already
checks in __post_init__.
"""

from __future__ import annotations

import unittest

from cad.reconstructed.model import build_oven
from cad.reconstructed.spec import OVENS


class ReconstructedEnvelopeTest(unittest.TestCase):
    def test_published_envelopes(self) -> None:
        for spec in OVENS:
            assembly = build_oven(spec)
            box = assembly.bounding_box()
            width = box.max.X - box.min.X
            depth = box.max.Y - box.min.Y
            height = box.max.Z - box.min.Z
            self.assertAlmostEqual(width, spec.ext_w, delta=1.0, msg=spec.oven_id)
            self.assertAlmostEqual(depth, spec.ext_d, delta=1.0, msg=spec.oven_id)
            self.assertAlmostEqual(height, spec.installed_h if spec.flue else spec.body_h, delta=1.0, msg=spec.oven_id)
            self.assertGreater(spec.mouth_over_apex, 0.55)
            self.assertLess(spec.mouth_over_apex, 0.63)
            self.assertEqual(len(spec.insulation_mm), 3 if spec.flue else 1)

    def test_dome_body_is_the_520_mm_inference(self) -> None:
        dome = OVENS[2]
        self.assertEqual(dome.body_h, 520)
        self.assertEqual(dome.hearth_z, 187)
        self.assertAlmostEqual(dome.roof_space, 95, places=3)
        self.assertAlmostEqual(dome.ext_h_published - dome.body_h, 477, places=3)

    def test_mouth_width_split(self) -> None:
        arc, tread, dome = OVENS
        self.assertAlmostEqual(arc.mouth_over_width, 1.0, places=2)
        self.assertAlmostEqual(tread.mouth_over_width, 1.0, places=2)
        self.assertAlmostEqual(dome.mouth_over_width, 470 / 724, places=3)

    def test_cutaway_keeps_the_stone(self) -> None:
        dome = OVENS[2]
        cut = build_oven(dome, cutaway=True)
        labels = [child.label for child in cut.children]
        self.assertTrue(any(label and label.endswith("-stone") for label in labels))
        self.assertTrue(any(label and "blanket-3" in label for label in labels))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
