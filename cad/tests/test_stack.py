"""Gates for the modular stack. These do not need FreeCAD."""

from __future__ import annotations

import copy
import math
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


class SyraxTests(unittest.TestCase):
    def test_the_damper_shuts_the_flue(self) -> None:
        design = Stack(
            dragon="Syrax",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True, damper_shut=True,
        )
        items = {part["id"]: part for part in parts(design)}
        damper = items["damper"]
        front = items["flue-front"]
        rear = items["flue-rear"]
        self.assertGreater(damper["corner"][1], front["corner"][1] + front["size"][1])
        self.assertLess(damper["corner"][1] + damper["size"][1], rear["corner"][1])
        tang = items["damper-tang"]
        self.assertGreater(tang["corner"][2] + tang["size"][2], front["corner"][2] + front["size"][2])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["bread_window_min"], 25.0)


class SheepstealerTests(unittest.TestCase):
    def _design(self) -> Stack:
        return Stack(
            dragon="Sheepstealer",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True,
        )

    def test_the_rope_sits_clear_in_the_door_gap(self) -> None:
        design = self._design()
        items = {part["id"]: part for part in parts(design)}
        door = items["door-inner"]
        skin = items["skin-lintel"]
        door_face = door["corner"][1] + door["size"][1]
        skin_face = skin["corner"][1]
        for name in ("door-rope-top", "door-rope-bottom", "door-rope-port", "door-rope-starboard"):
            rope = items[name]
            self.assertEqual(rope["material"], "rope")
            self.assertEqual(rope["module"], "brow")
            self.assertGreater(rope["corner"][1], door_face + 0.5)
            self.assertLess(rope["corner"][1] + rope["size"][1], skin_face - 1.0)
        top = items["door-rope-top"]
        port = items["door-rope-port"]
        star = items["door-rope-starboard"]
        opening = star["corner"][0] - (port["corner"][0] + port["size"][0])
        self.assertGreater(opening, 300.0)
        self.assertLess(top["size"][2], 20.0)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["bread_window_min"], 25.0)
        self.assertLessEqual(result["skin_C"], 55.0)


class VermithorTests(unittest.TestCase):
    def test_the_plate_runs_forward_over_the_steak(self) -> None:
        design = Stack(
            dragon="Vermithor",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True,
        )
        items = {part["id"]: part for part in parts(design)}
        plate = items["soffit-broiler"]
        self.assertEqual(plate["corner"][2], 100.0)
        self.assertLessEqual(plate["corner"][1], 264.0)
        self.assertGreaterEqual(plate["corner"][1] + plate["size"][1], 264.0)
        self.assertLess(plate["corner"][1] + plate["size"][1], 454.0)
        rail = items["rail-broiler-0"]
        self.assertLess(rail["corner"][1], plate["corner"][1])
        self.assertGreaterEqual(rail["corner"][1] + rail["size"][1], 640.0)
        self.assertGreater(rail["corner"][2], plate["corner"][2] + plate["size"][2] + 0.4)
        post = items["post-broiler-0"]
        self.assertGreater(post["origin"][1], 540.0)
        tang = items["broiler-tang"]
        self.assertLess(tang["corner"][2] + tang["size"][2], plate["corner"][2] + 0.1)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertLessEqual(result["skin_C"], 55.0)
        self.assertLess(result["modules_kg"]["tunnel"], result["modules_kg"]["pit"])


class SilverwingTests(unittest.TestCase):
    def test_the_rails_are_rods(self) -> None:
        design = Stack(
            dragon="Silverwing",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
        )
        items = {part["id"]: part for part in parts(design)}
        rail = items["rail-broiler-0"]
        self.assertEqual(rail["shape"], "tube")
        self.assertEqual(rail["r_out"], 4.0)
        plate = items["soffit-broiler"]
        self.assertLessEqual(plate["corner"][1], 264.0)
        self.assertGreater(rail["origin"][2] - rail["r_out"], plate["corner"][2] + plate["size"][2] + 0.4)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["ready_kg"], 33.2)
        self.assertLess(result["modules_kg"]["tunnel"], result["modules_kg"]["pit"])
        self.assertLessEqual(result["skin_C"], 55.0)


class VhagarTests(unittest.TestCase):
    def test_the_wind_back_stores_under_the_overhang(self) -> None:
        design = Stack(
            dragon="Vhagar",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True, wind=True,
        )
        items = {part["id"]: part for part in parts(design)}
        plate = items["wind-back"]
        self.assertEqual(plate["module"], "pit")
        self.assertGreater(plate["corner"][1], 682.0)
        self.assertLess(plate["corner"][2] + plate["size"][2], 0.0)
        shelf = items["wind-shelf-0"]
        self.assertEqual(shelf["corner"][1], 661.0)
        self.assertLess(shelf["corner"][2] + shelf["size"][2], plate["corner"][2] - 0.4)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["modules_kg"]["pit"], 12.0)
        self.assertLess(result["modules_kg"]["tunnel"], result["modules_kg"]["pit"])
        self.assertLess(result["body_length_mm"], 880.0)


class BalerionTests(unittest.TestCase):
    def test_jarrah_stands_off_the_brow(self) -> None:
        design = Stack(
            dragon="Balerion",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True,
        )
        items = {part["id"]: part for part in parts(design)}
        panel = items["brow-panel-port"]
        skin = items["skin-port-brow"]
        self.assertEqual(panel["material"], "jarrah")
        self.assertEqual(panel["zone"], "cool")
        self.assertEqual(panel["module"], "brow")
        skin_outer = skin["corner"][0]
        panel_inner = panel["corner"][0] + panel["size"][0]
        self.assertLess(panel_inner, skin_outer - 7.0)
        washer = items["brow-washer-port-0"]
        self.assertEqual(washer["material"], "ptfe")
        self.assertAlmostEqual(washer["origin"][0], panel_inner, places=2)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLessEqual(result["skin_C"], 55.0)
        self.assertLess(result["modules_kg"]["brow"], 8.0)
        # Two posts and two washers, panel faces 110 by 130 mm, skin at 55°C.
        import math
        r_post = 0.005 / (16.0 * math.pi * 0.0025 ** 2)
        r_washer = 0.003 / (0.25 * math.pi * 0.004 ** 2)
        r_path = (r_post + r_washer) / 2.0
        r_conv = 1.0 / (10.0 * 2.0 * 0.110 * 0.130)
        face = 20.0 + (55.0 - 20.0) * r_conv / (r_path + r_conv)
        self.assertLess(face, 30.0)
        self.assertAlmostEqual(face, 20.9, delta=0.2)


class MeraxesTests(unittest.TestCase):
    def test_the_door_face_is_cool_enough_to_hold(self) -> None:
        design = Stack(
            dragon="Meraxes",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True,
        )
        items = {part["id"]: part for part in parts(design)}
        skin = items["door-skin"]
        board = items["door-ins"]
        gap = board["corner"][1] - (skin["corner"][1] + skin["size"][1])
        self.assertAlmostEqual(gap, 24.0, places=2)
        grip = items["grip-door"]
        self.assertEqual(grip["material"], "jarrah")
        self.assertEqual(grip["zone"], "cool")
        self.assertEqual(grip["module"], "brow")
        self.assertLess(items["ferrule-door"]["r_in"], grip["profile"][0][1])
        resist = 1.0 / 25.0 + 0.0012 / 45.0 + 0.016 / 0.030 + 0.024 / 0.032 + 0.0008 / 160.0 + 0.1
        face = 20.0 + 480.0 / (resist * 10.0)
        self.assertLessEqual(face, 55.0)
        from cad.freecad.stacklib import grip_temperature
        self.assertLess(grip_temperature(face, 18.0), 40.0)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["body_length_mm"], 880.0)


def _tube(pid: str, r_in: float, r_out: float, origin: list[float]) -> dict:
    return {
        "id": pid,
        "shape": "tube",
        "origin": origin,
        "axis": [0, 0, 1],
        "r_in": r_in,
        "r_out": r_out,
        "length": 40.0,
    }


class DreamfyreTests(unittest.TestCase):
    def _design(self) -> Stack:
        return Stack(
            dragon="Dreamfyre",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True, door_hinge=True,
        )

    def test_a_pin_in_a_bore_is_not_a_hit(self) -> None:
        pin = _tube("pin", 0.0, 3.6, [0.0, 0.0, 0.0])
        bore = _tube("bore", 4.2, 7.0, [0.0, 0.0, 0.0])
        self.assertEqual(aabb_collisions([pin, bore]), [])
        wall = _tube("wall", 3.0, 7.0, [0.0, 0.0, 0.0])
        self.assertEqual(aabb_collisions([pin, wall]), [("pin", "wall")])

    def test_the_pintle_clears_the_barrel_and_bolts_to_the_skin(self) -> None:
        design = self._design()
        items = {part["id"]: part for part in parts(design)}
        pin = items["hinge-pin"]
        barrel = items["hinge-barrel-0"]
        self.assertLess(pin["r_out"] + 0.4, barrel["r_in"])
        self.assertEqual(pin["origin"][0], barrel["origin"][0])
        self.assertEqual(pin["origin"][1], barrel["origin"][1])
        upper = items["hinge-barrel-1"]
        head = items["hinge-head"]
        play = head["origin"][2] - (upper["origin"][2] + upper["length"])
        self.assertGreater(play, 0.3)
        self.assertLess(play, 1.0)
        skin = items["skin-port-brow"]
        leaf = items["hinge-leaf-low"]
        self.assertAlmostEqual(leaf["corner"][0] + leaf["size"][0], skin["corner"][0], places=2)
        self.assertEqual(leaf["material"], "mild")
        ear = items["hinge-ear-0"]
        door = items["door-skin"]
        self.assertAlmostEqual(ear["corner"][1] + ear["size"][1], door["corner"][1], places=2)
        self.assertGreater(barrel["origin"][2], items["hinge-arm-low"]["corner"][2] + items["hinge-arm-low"]["size"][2])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["skin_C"], 55.01)
        self.assertLess(result["body_length_mm"], 880.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        for part in parts(design):
            if part["material"] in ("jarrah", "gidgee"):
                self.assertEqual(part["zone"], "cool", part["id"])


class CannibalTests(unittest.TestCase):
    def test_the_spacers_tie_the_inner_plate_to_the_skin(self) -> None:
        design = Stack(
            dragon="Cannibal",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True, door_hinge=True, door_tie=True,
        )
        items = {part["id"]: part for part in parts(design)}
        skin = items["door-skin"]
        plate = items["door-inner"]
        board = items["door-ins"]
        tie = items["tie-door-0"]
        skin_inner = skin["corner"][1] + skin["size"][1]
        plate_outer = plate["corner"][1]
        self.assertAlmostEqual(tie["origin"][1], skin_inner, places=2)
        self.assertAlmostEqual(tie["origin"][1] + tie["length"], plate_outer, places=2)
        self.assertGreater(tie["length"], 30.0)
        # The board gave up a border. The spacer sits in it.
        self.assertGreater(board["corner"][0], skin["corner"][0] + tie["r_out"])
        self.assertGreater(tie["origin"][0] - tie["r_out"], skin["corner"][0])
        self.assertLess(tie["origin"][0] + tie["r_out"], board["corner"][0])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertLess(result["body_length_mm"], 880.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertEqual(items["tie-door-0"]["module"], "brow")
        self.assertGreaterEqual(result["wood_hot_gap_mm"], 2.0)


class QuicksilverTests(unittest.TestCase):
    def _design(self) -> Stack:
        return Stack(
            dragon="Quicksilver",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True, door_hinge=True,
            door_tie=True, door_swing=True,
        )

    def test_the_arms_leave_the_door_and_the_brow_lifts_off(self) -> None:
        design = self._design()
        items = {part["id"]: part for part in parts(design)}
        door = items["door-skin"]
        door_z0 = door["corner"][2]
        door_z1 = door_z0 + door["size"][2]
        low = items["hinge-arm-low"]
        high = items["hinge-arm-high"]
        self.assertLess(low["corner"][2] + low["size"][2], door_z0)
        self.assertGreater(high["corner"][2], door_z1)
        wall = items["pit-wall-front"]
        self.assertAlmostEqual(low["corner"][1] + low["size"][1], wall["corner"][1], places=2)
        self.assertEqual(low["module"], "pit")
        self.assertEqual(low["material"], "mild")
        skin = items["skin-port-brow"]
        leaf = items["hinge-leaf-high"]
        self.assertAlmostEqual(leaf["corner"][0] + leaf["size"][0], skin["corner"][0], places=2)
        self.assertGreater(leaf["corner"][2], door_z1)
        pin = items["hinge-pin"]
        bore = items["hinge-barrel-high"]
        self.assertLess(pin["r_out"] + 0.4, bore["r_in"])
        self.assertEqual(pin["origin"][0], bore["origin"][0])
        self.assertEqual(pin["origin"][1], bore["origin"][1])
        pin_top = pin["origin"][2] + pin["length"]
        bore_top = bore["origin"][2] + bore["length"]
        self.assertGreater(bore_top - pin_top, 0.2)
        self.assertLess(bore_top - pin_top, 0.6)
        self.assertNotIn("hinge-head", items)
        collar = items["hinge-collar"]
        barrel = items["hinge-barrel-0"]
        play = barrel["origin"][2] - (collar["origin"][2] + collar["length"])
        self.assertGreater(play, 0.3)
        self.assertLess(play, 0.6)
        # Fixed steel that shares the door's height stays inside the skin's swing.
        axis_x, axis_y = pin["origin"][0], pin["origin"][1]
        skin_r = min(
            math.hypot(x - axis_x, y - axis_y)
            for x in (door["corner"][0], door["corner"][0] + door["size"][0])
            for y in (door["corner"][1], door["corner"][1] + door["size"][1])
        )
        for pid in ("hinge-pin", "hinge-pin-low", "hinge-collar"):
            part = items[pid]
            top = part["origin"][2] + part["length"]
            if top <= door_z0 or part["origin"][2] >= door_z1:
                continue
            reach = part["r_out"] * math.sqrt(2.0)
            self.assertLess(reach, skin_r - 0.4, pid)
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["wood_hot_gap_mm"], 2.0)
        self.assertLess(result["skin_C"], 55.01)
        self.assertLess(result["body_length_mm"], 880.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertEqual(items["hinge-barrel-high"]["module"], "brow")
        for part in parts(design):
            if part["material"] in ("jarrah", "gidgee"):
                self.assertEqual(part["zone"], "cool", part["id"])


class UrraxTests(unittest.TestCase):
    def test_the_hood_grip_stands_on_steel(self) -> None:
        design = Stack(
            dragon="Urrax",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True, door_hinge=True,
            door_tie=True, door_swing=True, hood_pad=True,
        )
        items = {part["id"]: part for part in parts(design)}
        skin = items["skin-top-body"]
        outer = items["hood-pad-outer"]
        inner = items["hood-pad-inner"]
        post = items["post-hood-0"]
        skin_top = skin["corner"][2] + skin["size"][2]
        skin_inner = skin["corner"][2]
        self.assertAlmostEqual(outer["corner"][2], skin_top, places=2)
        self.assertAlmostEqual(inner["corner"][2] + inner["size"][2], skin_inner, places=2)
        self.assertAlmostEqual(post["origin"][2], outer["corner"][2] + outer["size"][2], places=2)
        self.assertGreater(post["origin"][2], skin_top)
        self.assertEqual(outer["material"], "mild")
        self.assertEqual(outer["module"], "tunnel")
        # Both posts land inside the pad.
        for pid in ("post-hood-0", "post-hood-1"):
            tube = items[pid]
            self.assertGreater(tube["origin"][0] - tube["r_out"], outer["corner"][0])
            self.assertLess(tube["origin"][0] + tube["r_out"], outer["corner"][0] + outer["size"][0])
            self.assertGreater(tube["origin"][1] - tube["r_out"], outer["corner"][1])
            self.assertLess(tube["origin"][1] + tube["r_out"], outer["corner"][1] + outer["size"][1])
        # The pad sits on the body skin, not past its edge.
        self.assertGreaterEqual(outer["corner"][1], skin["corner"][1])
        self.assertLessEqual(outer["corner"][1] + outer["size"][1], skin["corner"][1] + skin["size"][1])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["wood_hot_gap_mm"], 2.0)
        self.assertLess(result["skin_C"], 55.01)
        self.assertLess(result["body_length_mm"], 880.0)
        self.assertGreaterEqual(result["mouth_h"], 180.0)
        self.assertNotIn("door-pad-outer", items)


class TerraxTests(unittest.TestCase):
    def test_the_brow_grip_stands_on_steel(self) -> None:
        design = Stack(
            dragon="Terrax",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True, door_hinge=True,
            door_tie=True, door_swing=True, hood_pad=True, brow_pad=True,
            door_pad=True,
        )
        items = {part["id"]: part for part in parts(design)}
        skin = items["skin-top-brow"]
        outer = items["brow-pad-outer"]
        inner = items["brow-pad-inner"]
        post = items["post-brow-0"]
        skin_top = skin["corner"][2] + skin["size"][2]
        self.assertAlmostEqual(outer["corner"][2], skin_top, places=2)
        self.assertAlmostEqual(inner["corner"][2] + inner["size"][2], skin["corner"][2], places=2)
        self.assertAlmostEqual(post["origin"][2], outer["corner"][2] + outer["size"][2], places=2)
        self.assertGreater(post["origin"][2], skin_top)
        self.assertEqual(outer["module"], "brow")
        self.assertGreaterEqual(outer["corner"][1], skin["corner"][1])
        self.assertLessEqual(outer["corner"][1] + outer["size"][1], skin["corner"][1] + skin["size"][1])
        # The tunnel pad from Urrax is still there.
        self.assertIn("hood-pad-outer", items)
        door = items["door-skin"]
        outer_pad = items["door-pad-outer"]
        inner_pad = items["door-pad-inner"]
        door_post = items["post-door-0"]
        skin_outer = door["corner"][1]
        skin_inner = door["corner"][1] + door["size"][1]
        self.assertAlmostEqual(outer_pad["corner"][1] + outer_pad["size"][1], skin_outer, places=2)
        self.assertAlmostEqual(inner_pad["corner"][1], skin_inner, places=2)
        self.assertAlmostEqual(door_post["origin"][1] + door_post["length"], outer_pad["corner"][1], places=2)
        self.assertLess(door_post["origin"][1] + door_post["length"], skin_outer)
        self.assertEqual(outer_pad["material"], "mild")
        self.assertEqual(outer_pad["module"], "brow")
        board = items["door-ins"]
        self.assertLess(inner_pad["corner"][1] + inner_pad["size"][1], board["corner"][1])
        for pid in ("post-door-0", "post-door-1"):
            tube = items[pid]
            self.assertGreater(tube["origin"][0] - tube["r_out"], outer_pad["corner"][0])
            self.assertLess(tube["origin"][0] + tube["r_out"], outer_pad["corner"][0] + outer_pad["size"][0])
            self.assertGreater(tube["origin"][2] - tube["r_out"], outer_pad["corner"][2])
            self.assertLess(tube["origin"][2] + tube["r_out"], outer_pad["corner"][2] + outer_pad["size"][2])
        result = evaluate(design)
        self.assertEqual(result["aabb_hits"], 0)
        self.assertGreaterEqual(result["wood_hot_gap_mm"], 2.0)
        self.assertLess(result["skin_C"], 55.01)
        self.assertLess(result["body_length_mm"], 880.0)

    def test_coal_hooks_high_and_the_pit_packs(self) -> None:
        design = Stack(
            dragon="Terrax",
            deck_t=4.0, ins_t=22.0, floor_ins=12.0, belly_ins=12.0,
            liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=294.0,
            soffit_h=150.0, air_gap=16.0, standoff=54.0,
            launch_y=150.0, stepped=True, sloped=True, split=True,
            seated=True, grill=True, broiler=True, bail=True,
            damper_shut=True, gasket=True, slide=True, rod_rail=True,
            wind=True, panel=True, door_air=True, door_hinge=True,
            door_tie=True, door_swing=True, hood_pad=True, brow_pad=True,
            door_pad=True,
        )
        built = parts(design)
        items = {part["id"]: part for part in built}
        low = items["grate-rail-port"]["corner"][2]
        high = items["grate-rail-high-port"]["corner"][2]
        self.assertAlmostEqual(high - low, 32.0, places=2)
        rod = items["grate-rod-0"]
        self.assertAlmostEqual(rod["origin"][2] - rod["r_out"], high, places=2)
        self.assertLess(rod["length"], 460.0)
        wood = []
        for part in built:
            moved = copy.deepcopy(part)
            if part["id"].startswith("grate-rod-"):
                moved["origin"][2] -= 32.0
            wood.append(moved)
        self.assertEqual(aabb_collisions(wood), [])
        plate = items["soffit-broiler"]["size"]
        wind = items["wind-back"]["size"]
        self.assertLess(max(plate[0], plate[1]), 464.0)
        self.assertLess(max(wind[0], wind[2]), 464.0)
        inner = items["door-inner"]
        grip = items["grip-door"]
        radii = [pair[1] for pair in grip["profile"]]
        door_depth = (inner["corner"][1] + inner["size"][1]) - (grip["origin"][1] - max(radii))
        self.assertLess(door_depth, 120.0)


if __name__ == "__main__":
    unittest.main()
