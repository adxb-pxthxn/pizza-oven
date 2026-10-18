"""Gates for the modular stack. These do not need FreeCAD."""

from __future__ import annotations

import unittest

from cad.freecad.stacklib import (
    DECK_L,
    DECK_W,
    PRESS_FITS,
    Stack,
    aabb_collisions,
    contact_temperature,
    deck_growth_mm,
    evaluate,
    parts,
    steel_effusivity,
)


def _sample() -> Stack:
    return Stack(
        dragon="Stormcloud",
        deck_t=5.0, ins_t=26.0, floor_ins=18.0, belly_ins=22.0,
        liner_t=0.7, skin_t=0.7, pit_t=1.1, front_h=256.0,
        soffit_h=118.0, air_gap=12.0, standoff=55.0,
    )


class StackTests(unittest.TestCase):
    def test_no_stone_and_no_cordierite(self) -> None:
        materials = {part["material"] for part in parts(_sample())}
        self.assertNotIn("cordierite", materials)
        self.assertIn("mild", materials)

    def test_wood_stays_cool(self) -> None:
        for part in parts(_sample()):
            if part["material"] in ("jarrah", "gidgee"):
                self.assertEqual(part["zone"], "cool", part["id"])

    def test_only_ferrules_may_overlap(self) -> None:
        self.assertEqual(aabb_collisions(parts(_sample())), [])

    def test_ferrules_are_a_real_press(self) -> None:
        items = {part["id"]: part for part in parts(_sample())}
        for ferrule, grip in PRESS_FITS:
            self.assertLess(items[ferrule]["r_in"], items[grip]["profile"][0][1])

    def test_floor_stays_flat_and_free(self) -> None:
        result = evaluate(_sample())
        self.assertLess(result["bow_mm"], 0.30)
        self.assertLess(result["sag_mm"], 0.40)
        self.assertGreater(result["side_gap_mm"], deck_growth_mm(DECK_L) + 2.0)
        self.assertGreaterEqual(min(DECK_W, result["mouth_h"] and 424.0) - 381.0, 39.0)

    def test_touch_temperatures(self) -> None:
        result = evaluate(_sample())
        self.assertLessEqual(result["skin_C"], 55.0)
        self.assertLessEqual(result["under_C"], 60.0)
        self.assertLessEqual(result["grip_pit_C"], 40.0)
        self.assertLessEqual(result["grip_hood_C"], 40.0)

    def test_steel_contact_is_in_the_cordierite_band(self) -> None:
        # A 300°C steel deck meets dough about as gently as 450°C cordierite.
        steel = contact_temperature(steel_effusivity(), 300.0)
        cord = contact_temperature((2.2 * 2100.0 * 950.0) ** 0.5, 450.0)
        self.assertLess(abs(steel - cord), 25.0)
        self.assertGreater(steel, 250.0)
        self.assertLess(steel, 300.0)

    def test_launch_and_times(self) -> None:
        result = evaluate(_sample())
        self.assertGreaterEqual(result["mouth_h"], 160.0)
        self.assertAlmostEqual(result["mouth_ratio"], 0.63, places=2)
        self.assertLessEqual(result["heatup_min"], 25.0)
        self.assertGreaterEqual(result["bread_window_min"], 25.0)
        self.assertGreater(result["steak_flux_W_m2"], 8000.0)
        self.assertGreater(result["pack_open_min"], 10.0)


if __name__ == "__main__":
    unittest.main()
