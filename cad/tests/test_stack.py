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
        dragon="Vermax",
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


def _arrax() -> Stack:
    return Stack(
        dragon="Arrax",
        deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
        liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
        soffit_h=110.0, air_gap=16.0, standoff=54.0,
        launch_y=260.0, stepped=True,
    )


class ArraxTests(unittest.TestCase):
    def test_crown_follows_the_soffit(self) -> None:
        design = _arrax()
        items = {part["id"]: part for part in parts(design)}
        brow = items["liner-top-brow"]["corner"][2]
        body = items["liner-top-body"]["corner"][2]
        self.assertGreater(brow - body, 100.0)
        self.assertAlmostEqual(body, design.soffit_h + 8.0, places=2)
        self.assertIn("grate-rod-0", items)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertLess(result["ready_kg"], 34.0)
        self.assertLessEqual(result["skin_C"], 55.0)
        self.assertLessEqual(result["grip_pit_C"], 40.0)
        for part in parts(design):
            if part["material"] in ("jarrah", "gidgee"):
                self.assertEqual(part["zone"], "cool", part["id"])


class ShrykosTests(unittest.TestCase):
    def test_the_cowl_is_a_fold(self) -> None:
        design = Stack(
            dragon="Shrykos",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=110.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True,
        )
        items = {part["id"]: part for part in parts(design)}
        self.assertEqual(items["liner-cowl"]["shape"], "prism")
        self.assertNotIn("liner-step", items)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["ready_kg"], 31.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertLessEqual(result["skin_C"], 55.0)


class MorghulTests(unittest.TestCase):
    def test_the_hood_comes_apart_at_the_fold(self) -> None:
        design = Stack(
            dragon="Morghul",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=110.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
        )
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["modules_kg"]["brow"], 8.0)
        self.assertLess(result["modules_kg"]["tunnel"], 8.0)
        self.assertLess(result["modules_kg"]["pit"], 12.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertLessEqual(result["skin_C"], 55.0)


class SeasmokeTests(unittest.TestCase):
    def test_the_brow_sits_on_a_shelf(self) -> None:
        design = Stack(
            dragon="Seasmoke",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=110.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True,
        )
        items = {part["id"]: part for part in parts(design)}
        foot = items["seat-foot"]
        shelf = items["seat-shelf"]
        gap = foot["corner"][2] - (shelf["corner"][2] + shelf["size"][2])
        self.assertGreater(gap, 0.4)
        self.assertLess(gap, 1.0)
        self.assertIn("seat-leg", items)
        self.assertEqual(items["seat-leg"]["module"], "tunnel")
        self.assertEqual(foot["module"], "brow")
        self.assertEqual(shelf["module"], "tunnel")
        self.assertIn("grate-rail-high-port", items)
        self.assertIn("grip-brow", items)
        self.assertEqual(items["grip-brow"]["zone"], "cool")
        # Rods moved up onto the cooking rails. The low rails stay empty.
        self.assertGreater(items["grate-rod-0"]["origin"][2], items["grate-rail-port"]["corner"][2] + 20.0)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["modules_kg"]["brow"], 8.0)
        self.assertLess(result["modules_kg"]["tunnel"], 8.0)
        self.assertLess(result["modules_kg"]["pit"], 12.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertLessEqual(result["skin_C"], 55.0)
        self.assertLess(items["ferrule-brow"]["r_in"], items["grip-brow"]["profile"][0][1])


class CaraxesTests(unittest.TestCase):
    def test_the_roof_stays_high_and_the_plate_hangs_back(self) -> None:
        design = Stack(
            dragon="Caraxes",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True,
        )
        items = {part["id"]: part for part in parts(design)}
        plate = items["soffit-broiler"]
        self.assertGreaterEqual(plate["corner"][1], 460.0)
        self.assertAlmostEqual(plate["corner"][2], 100.0, places=2)
        self.assertAlmostEqual(items["soffit"]["corner"][2], 150.0, places=2)
        self.assertLess(items["rack-rod-0"]["origin"][2], plate["corner"][2])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertLessEqual(result["skin_C"], 55.0)
        self.assertLess(result["modules_kg"]["tunnel"], 8.5)
        self.assertLess(result["modules_kg"]["pit"], 12.0)
        self.assertLess(result["heatup_min"], 25.0)


class MeleysTests(unittest.TestCase):
    def test_the_hearth_lifts_by_wood(self) -> None:
        design = Stack(
            dragon="Meleys",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
        )
        items = {part["id"]: part for part in parts(design)}
        grip = items["grip-hearth"]
        self.assertEqual(grip["material"], "jarrah")
        self.assertEqual(grip["zone"], "cool")
        self.assertEqual(grip["module"], "hearth")
        self.assertLess(items["ferrule-hearth"]["r_in"], grip["profile"][0][1])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["modules_kg"]["hearth"], 11.0)
        self.assertLess(result["modules_kg"]["hearth"], result["modules_kg"]["pit"])
        self.assertLessEqual(result["skin_C"], 55.0)


if __name__ == "__main__":
    unittest.main()
