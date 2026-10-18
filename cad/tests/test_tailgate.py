"""Envelope and mass checks for the Angas 430. No network."""

from __future__ import annotations

import math
import unittest

from cad.tailgate.model import build, mass_report
from cad.tailgate.spec import SPEC, skin_temperature


class TailgateSpecTest(unittest.TestCase):
    def test_pizza_and_tub(self):
        self.assertGreaterEqual(SPEC.floor_d, 420)
        self.assertGreater(SPEC.pizza_radial_clearance, 20)
        self.assertGreater(SPEC.mouth_side_clearance, 15)
        self.assertLess(SPEC.outer_diameter, 1224)
        self.assertLess(SPEC.body_height, 460)
        self.assertLess(SPEC.handle_span, 1224)

    def test_mouth_ratio_and_joint(self):
        self.assertGreater(SPEC.mouth_over_apex, 0.54)
        self.assertLess(SPEC.mouth_over_apex, 0.63)
        self.assertGreater(SPEC.skirt_h, SPEC.mouth_h + SPEC.joggle_h)

    def test_skin_is_a_short_touch_not_a_lean(self):
        wall = skin_temperature(SPEC.wall_aes, SPEC.wall_casi)
        crown = skin_temperature(SPEC.crown_aes)
        self.assertLess(wall["skin_C"], 70)
        self.assertLess(crown["skin_C"], 56)
        self.assertGreater(wall["skin_C"], 45)

    def test_stone_does_not_pass_the_mouth(self):
        """A tilted disk still needs more height than this arch has."""
        width = SPEC.mouth_w
        if width >= SPEC.floor_d:
            self.skipTest("mouth is as wide as the stone")
        theta = math.acos(width / SPEC.floor_d)
        projected = SPEC.floor_d * math.sin(theta) + SPEC.floor_t * math.cos(theta)
        self.assertGreater(projected, SPEC.mouth_h)

    def test_mass_is_a_one_person_lift_without_the_stone(self):
        report = mass_report(build(deployed_legs=False))
        self.assertLess(report["stone_out_kg"], 36)
        self.assertGreater(report["stone_out_kg"], 18)
        self.assertAlmostEqual(report["stone_kg"], 6.1, delta=0.2)
        labels = {row["label"] for row in report["rows"]}
        self.assertIn("shell-crown", labels)
        self.assertIn("cinch-band", labels)
        self.assertNotIn("wood-stave", labels)


if __name__ == "__main__":
    unittest.main()
