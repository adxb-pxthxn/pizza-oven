"""Shop numbers for the long-vault prototypes. FreeCAD is not required."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from cad.freecad.stream_physics import Vault, evaluate

ROOT = Path(__file__).resolve().parents[2]


def stormcloud() -> Vault:
    return Vault(
        name="stormcloud",
        dragon="Stormcloud",
        fibre_t=75.0,
        floor_fibre=50.0,
        air_gap=8.0,
        skin_t=1.0,
        steel_t=6.0,
        plate_t=1.2,
        standoff=20.0,
    )


class StormcloudPhysicsTest(unittest.TestCase):
    def test_shop_stack_holds_the_limits(self):
        result = evaluate(stormcloud())
        self.assertLessEqual(result["skin_C"], 60.0)
        self.assertLess(result["skin_C"], 56.0)
        self.assertLessEqual(result["under_C"], 60.0)
        self.assertLessEqual(result["grip_C"], 40.0)
        self.assertLessEqual(result["floor_C"], 315.0)
        self.assertGreaterEqual(result["scorch_s"], 110.0)
        self.assertLessEqual(result["camber_mm"], 0.3)
        self.assertLessEqual(result["sag_mm"], 0.3)
        self.assertGreater(result["side_gap_mm"], result["growth_mm"] + 1.0)
        self.assertGreaterEqual(result["broil_W_m2"], 8000.0)
        self.assertLessEqual(result["cooldown_ratio"], 1.35)
        self.assertGreater(result["pizza_clearance"], 25.0)
        self.assertAlmostEqual(result["mouth_over_crown"], 0.632, places=3)
        self.assertTrue(result["free_floating"])
        self.assertGreater(result["outer_length"], 750.0)
        self.assertGreater(result["body_height"], 320.0)
        self.assertLess(abs(result["balance_floor"]), 1.0)
        self.assertNotIn("cordierite", result["parts"])
        self.assertNotIn("floor-cordierite", result["parts"])

    def test_wood_is_only_on_the_cool_parts(self):
        parts = evaluate(stormcloud())["parts"]
        wood = {"grips", "gidgee-ferrules", "peel-rest", "door-pull"}
        self.assertTrue(wood <= set(parts))
        self.assertLess(sum(parts[name] for name in wood), 0.5)

    def test_saved_optimizer_matches_the_shop_vault(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        if not path.exists():
            self.skipTest("optimizer json not written")
        saved = json.loads(path.read_text(encoding="utf-8"))["stormcloud"]
        live = evaluate(stormcloud())
        self.assertTrue(saved["success"])
        self.assertEqual(saved["design"]["dragon"], "Stormcloud")
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        self.assertAlmostEqual(saved["result"]["floor_C"], live["floor_C"], delta=0.2)

    def test_calculix_matches_the_one_d_sum(self):
        path = ROOT / "design" / "stream-1" / "thermal-fea.json"
        if not path.exists():
            self.skipTest("thermal fea not written")
        thermal = json.loads(path.read_text(encoding="utf-8"))
        self.assertAlmostEqual(thermal["slab"]["outer_C"], thermal["slab"]["expected_C"], delta=0.2)
        self.assertAlmostEqual(thermal["wall"]["outer_C"], thermal["wall"]["oned_C"], delta=1.0)
        self.assertAlmostEqual(thermal["floor"]["outer_C"], thermal["floor"]["oned_C"], delta=1.0)
        self.assertEqual(thermal["dragon"], "Stormcloud")
        live = evaluate(stormcloud())
        self.assertAlmostEqual(thermal["wall"]["oned_C"], live["skin_C"], delta=0.2)
        self.assertAlmostEqual(thermal["floor"]["oned_C"], live["under_C"], delta=0.2)

    def test_rails_span_the_slide(self):
        raw = json.loads((ROOT / "design" / "stream-1" / "optimizer.json").read_text(encoding="utf-8"))
        for name, length in (("stormcloud", 590.0), ("vermax", 690.0)):
            vault = Vault(**raw[name]["design"])
            rail_l = (vault.length - 20.0) - (vault.landing + 30.0)
            self.assertAlmostEqual(rail_l, length, delta=1.0)
            expected = round(rail_l * 2.0 * 12.0 * 1.2 * 1e-9 * 7900.0, 3)
            self.assertAlmostEqual(evaluate(vault)["parts"]["sky-rails"], expected, delta=0.01)


class TyraxesPhysicsTest(unittest.TestCase):
    def test_pizza_pose_is_cooler_and_lighter(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["tyraxes"]
        self.assertEqual(saved["design"]["door_pose"], "open")
        self.assertEqual(saved["design"]["box_d"], 48.0)
        self.assertEqual(saved["design"]["pizza_gas"], 360.0)
        live = evaluate(Vault(**saved["design"]))
        self.assertTrue(saved["success"])
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        self.assertAlmostEqual(saved["result"]["floor_C"], live["floor_C"], delta=0.2)
        self.assertLessEqual(live["floor_C"], 305.0)
        self.assertGreaterEqual(live["scorch_s"], 125.0)
        self.assertLess(live["heatup_shut_min"], 16.0)
        self.assertLess(live["ready_kg"], evaluate(stormcloud())["ready_kg"])
        self.assertLessEqual(live["under_C"], 60.0)
        self.assertGreaterEqual(live["broil_W_m2"], 8000.0)


class ArraxPhysicsTest(unittest.TestCase):
    def test_wider_floor_still_clears_its_growth(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["arrax"]
        self.assertEqual(saved["design"]["steel_w"], 480.0)
        self.assertEqual(saved["design"]["sill_d"], 90.0)
        self.assertEqual(saved["design"]["stop_gap"], 4.0)
        self.assertEqual(saved["design"]["door_pose"], "open")
        live = evaluate(Vault(**saved["design"]))
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        self.assertAlmostEqual(saved["result"]["floor_C"], live["floor_C"], delta=0.2)
        self.assertGreater(live["side_gap_mm"], live["growth_mm"] + 5.0)
        self.assertGreater(live["parts"]["plate-stops"], 0.05)
        self.assertGreater(saved["design"]["stop_gap"], live["growth_mm"])
        self.assertGreater(live["pizza_clearance"], 45.0)
        self.assertLessEqual(live["floor_C"], 315.0)
        self.assertGreaterEqual(live["scorch_s"], 120.0)
        self.assertGreater(live["parts"]["launch-sill"], 0.2)
        self.assertLess(live["parts"]["launch-sill"], 0.6)


class VermaxPhysicsTest(unittest.TestCase):
    def test_rear_plate_leaves_a_broil_bay(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["vermax"]
        self.assertEqual(saved["design"]["length"], 780.0)
        self.assertEqual(saved["design"]["plate_pose"], "rear")
        self.assertEqual(saved["design"]["stop_gap"], 4.0)
        live = evaluate(Vault(**saved["design"]))
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        self.assertLessEqual(live["floor_C"], 315.0)
        self.assertGreaterEqual(live["scorch_s"], 120.0)
        self.assertLessEqual(live["skin_C"], 60.0)
        self.assertLessEqual(live["cooldown_ratio"], 0.8)
        plate_l = min(saved["design"]["steel_l"] - 20.0, saved["design"]["length"] - saved["design"]["landing"] - 80.0)
        bay = (saved["design"]["length"] - 20.0 - plate_l) - saved["design"]["landing"]
        self.assertGreater(bay, 200.0)


class TessarionPhysicsTest(unittest.TestCase):
    def test_bread_pose_keeps_vermax_heat(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["tessarion"]
        self.assertEqual(saved["design"]["door_pose"], "shut")
        self.assertEqual(saved["design"]["plate_pose"], "in")
        self.assertEqual(saved["design"]["length"], 780.0)
        live = evaluate(Vault(**saved["design"]))
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        # Shut door, gas 230 C, 75 mm under the floor.
        self.assertAlmostEqual(live["bread_floor_C"], 216.0, delta=2.0)
        self.assertLess(live["bread_floor_C"], 230.0)
        self.assertLessEqual(live["floor_C"], 310.0)
        self.assertGreaterEqual(live["scorch_s"], 125.0)
        gate = json.loads((ROOT / "design" / "stream-1" / "tessarion" / "gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["solids"], 48)
        self.assertEqual(gate["interference"], [])
        self.assertGreater(gate["door_zmin"], gate["sill_zmax"] + 2.0)


class SunfyrePhysicsTest(unittest.TestCase):
    def test_bread_gas_holds_a_hearth_not_a_scorch(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["sunfyre"]
        self.assertEqual(saved["design"]["bread_gas"], 230.0)
        self.assertEqual(saved["design"]["door_pose"], "shut")
        live = evaluate(Vault(**saved["design"]))
        self.assertAlmostEqual(saved["result"]["bread_floor_C"], live["bread_floor_C"], delta=0.5)
        self.assertAlmostEqual(live["bread_floor_C"], 216.0, delta=2.0)
        self.assertLess(live["bread_floor_C"], 230.0)
        self.assertGreater(live["scorch_s"], 120.0)
        self.assertAlmostEqual(live["floor_C"], 305.1, delta=1.0)


class GreyGhostPhysicsTest(unittest.TestCase):
    def test_broil_bay_underside_stays_touchable(self):
        from cad.freecad.stream_physics import bay_underside

        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["grey-ghost"]
        self.assertEqual(saved["design"]["floor_fibre"], 75.0)
        self.assertEqual(saved["design"]["length"], 780.0)
        self.assertEqual(saved["design"]["plate_pose"], "rear")
        live = evaluate(Vault(**saved["design"]))
        bay = bay_underside(Vault(**saved["design"]))
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        self.assertLessEqual(live["floor_C"], 315.0)
        self.assertGreaterEqual(live["scorch_s"], 120.0)
        self.assertLessEqual(live["under_C"], 60.0)
        self.assertLessEqual(bay["under_C"], 60.0)
        growth_bay = 13.0e-6 * (bay["floor_C"] - 20.0) * saved["design"]["steel_w"]
        self.assertGreater(saved["design"]["stop_gap"], growth_bay)
        self.assertLess(live["bread_floor_C"], 230.0)
        self.assertLessEqual(live["cooldown_ratio"], 0.8)


class SeasmokePhysicsTest(unittest.TestCase):
    def test_handles_land_on_straps_and_the_tray_clears_the_grate(self):
        path = ROOT / "design" / "stream-1" / "optimizer.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["seasmoke"]
        self.assertEqual(saved["design"]["module"], 20.0)
        self.assertEqual(saved["design"]["frame_strap"], 2.0)
        self.assertEqual(saved["design"]["swing_arm"], 1.0)
        live = evaluate(Vault(**saved["design"]))
        self.assertAlmostEqual(saved["result"]["ready_kg"], live["ready_kg"], delta=0.05)
        self.assertGreater(live["parts"]["cheek-straps"], 0.3)
        self.assertGreater(live["parts"]["swing-tray"], 0.2)
        gate = json.loads((ROOT / "design" / "stream-1" / "seasmoke" / "gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["interference"], [])
        self.assertGreater(gate["rod_zmin"], gate["tray_zmax"] + 20.0)
        self.assertLess(gate["swing_park"]["xmax"], gate["skin_xmin"])


if __name__ == "__main__":
    unittest.main()
