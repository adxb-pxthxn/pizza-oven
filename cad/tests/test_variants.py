"""Mass, temperature, and file checks for Morning and Moondancer."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from cad.freecad.masslib import APEX_H, MOUTH_H, MOUTH_W, revolve_volume_mm3, cylinder_shell_mm3
from cad.freecad.optimize import MASS_CAP

ROOT = Path(__file__).resolve().parents[2]
VARIANTS = ROOT / "design" / "variants"


def _load(name: str) -> dict:
    return json.loads((VARIANTS / "optimizer.json").read_text(encoding="utf-8"))[name]


class OptimiserTest(unittest.TestCase):
    def test_both_close_under_the_cap(self):
        for name in ("morning", "moondancer"):
            item = _load(name)
            self.assertTrue(item["success"], item["message"])
            ready = item["result"]["ready_kg"]
            self.assertLessEqual(ready, MASS_CAP)
            self.assertGreater(ready, 12.0)
            parts = sum(item["result"]["parts"].values())
            self.assertAlmostEqual(parts, ready, delta=0.02)

    def test_names_are_the_young_dragons(self):
        self.assertEqual(_load("morning")["design"]["dragon"], "Morning")
        self.assertEqual(_load("moondancer")["design"]["dragon"], "Moondancer")
        self.assertEqual(_load("morning")["design"]["skin"], "blackwood")
        self.assertEqual(_load("moondancer")["design"]["skin"], "al")

    def test_pizza_still_turns_and_the_mouth_is_the_angas_mouth(self):
        for name in ("morning", "moondancer"):
            result = _load(name)["result"]
            self.assertGreaterEqual(result["pizza_clearance"], 19.0)
            self.assertAlmostEqual(result["mouth_over_apex"], MOUTH_H / APEX_H, places=3)
            self.assertEqual(MOUTH_W, 420.0)
            self.assertLess(result["outer_diameter"], 1224)
            self.assertLess(result["body_height"], 460)
            # Wider than the lowered tailgate, on purpose.
            self.assertGreater(result["outer_diameter"], 480)

    def test_skin_and_grip_constraints(self):
        morning = _load("morning")["result"]
        self.assertLessEqual(morning["wall_outer_C"], 50.05)
        self.assertLessEqual(morning["wall_inner_face_C"], 75.0)
        dancer = _load("moondancer")["result"]
        self.assertLessEqual(dancer["wall_outer_C"], 55.05)
        for result in (morning, dancer):
            self.assertLessEqual(result["under_C"], 60.05)
            self.assertLessEqual(result["grip_C"], 40.0)


class SolidAndMeshTest(unittest.TestCase):
    def test_freecad_mass_tracks_the_solver(self):
        for name, ceiling in (("morning", 20.0), ("moondancer", 20.0)):
            report = json.loads((VARIANTS / name / "freecad-mass.json").read_text(encoding="utf-8"))
            analytical = _load(name)["result"]["ready_kg"] - 1.85
            self.assertAlmostEqual(report["freecad_kg"], analytical, delta=0.25)
            self.assertLessEqual(report["ready_with_burner_kg"], ceiling)
            self.assertTrue((VARIANTS / name / f"{name}.FCStd").exists())
            self.assertTrue((VARIANTS / name / f"{name}.step").exists())
            self.assertIn("<svg", (VARIANTS / name / "ga-arrangement.svg").read_text(encoding="utf-8")[:200])

    def test_calculix_recovers_the_skin(self):
        thermal = json.loads((VARIANTS / "thermal-fea.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(thermal["slab"]["outer_C"], thermal["slab"]["expected_C"], delta=0.2)
        for name in ("morning", "moondancer"):
            wall = thermal["walls"][name]
            self.assertAlmostEqual(wall["outer_C"], wall["oned_C"], delta=1.0)
            grip = thermal["handles"][name]
            self.assertLess(grip["grip_max_C"], 40.0)
            self.assertLess(abs(grip["grip_C"] - grip["oned_C"]), 8.0)


class VolumeHelperTest(unittest.TestCase):
    def test_cylinder_shell(self):
        # r 100 to 102, height 50. pi*(102^2-100^2)*50.
        volume = cylinder_shell_mm3(100.0, 102.0, 0.0, 50.0)
        self.assertAlmostEqual(volume, 3.1415926535 * 404.0 * 50.0, delta=1e-3)

    def test_revolve_matches_the_cylinder(self):
        loop = [(100, 0), (102, 0), (102, 50), (100, 50), (100, 0)]
        self.assertAlmostEqual(revolve_volume_mm3(loop), cylinder_shell_mm3(100, 102, 0, 50), delta=1e-2)


if __name__ == "__main__":
    unittest.main()
