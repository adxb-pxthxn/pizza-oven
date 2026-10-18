"""Fast checks for the placeholder oven model.

Geometry tests skip when build123d is not installed. Parameter and
gitignore checks use the standard library only.

    python3 -m unittest cad.tests.test_placeholder_assembly
"""

from __future__ import annotations

import math
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cad.parameters import (  # noqa: E402
    ASSEMBLY_LABEL,
    DEFAULT_PARAMETERS,
    DOME_SHELL_LABEL,
    FLOOR_STONE_LABEL,
    INSULATION_LAYER_LABEL,
    OvenParameters,
)

try:
    import build123d  # noqa: F401
except ImportError:
    build123d = None


def _half_tube_volume_mm3(inner_radius_mm: float, outer_radius_mm: float, length_mm: float) -> float:
    return 0.5 * math.pi * (outer_radius_mm**2 - inner_radius_mm**2) * length_mm


def _expected_volume_mm3(params: OvenParameters) -> float:
    stone = params.stone_length_mm * params.stone_width_mm * params.stone_thickness_mm
    dome = _half_tube_volume_mm3(
        params.dome_inner_radius_mm,
        params.dome_outer_radius_mm,
        params.dome_length_mm,
    )
    insulation = _half_tube_volume_mm3(
        params.insulation_inner_radius_mm,
        params.insulation_outer_radius_mm,
        params.dome_length_mm,
    )
    return stone + dome + insulation


@unittest.skipUnless(build123d is not None, "build123d is not installed")
class PlaceholderGeometryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cad.assemblies.placeholder import build_placeholder_assembly
        from cad.build import export_assembly

        cls.build = staticmethod(build_placeholder_assembly)
        cls.export = staticmethod(export_assembly)

    def test_model_builds_with_sane_volume_and_bounds(self):
        params = DEFAULT_PARAMETERS
        assembly = self.build(params)
        labels = {child.label for child in assembly.children}

        self.assertEqual(assembly.label, ASSEMBLY_LABEL)
        self.assertEqual(
            labels,
            {FLOOR_STONE_LABEL, DOME_SHELL_LABEL, INSULATION_LAYER_LABEL},
        )
        self.assertAlmostEqual(assembly.volume, _expected_volume_mm3(params), delta=1e-2)

        by_label = {child.label: child for child in assembly.children}
        stone = by_label[FLOOR_STONE_LABEL]
        dome = by_label[DOME_SHELL_LABEL]
        insulation = by_label[INSULATION_LAYER_LABEL]
        self.assertAlmostEqual(
            stone.volume,
            params.stone_length_mm * params.stone_width_mm * params.stone_thickness_mm,
            delta=1e-6,
        )
        self.assertAlmostEqual(
            dome.volume,
            _half_tube_volume_mm3(
                params.dome_inner_radius_mm,
                params.dome_outer_radius_mm,
                params.dome_length_mm,
            ),
            delta=1e-2,
        )
        self.assertAlmostEqual(
            insulation.volume,
            _half_tube_volume_mm3(
                params.insulation_inner_radius_mm,
                params.insulation_outer_radius_mm,
                params.dome_length_mm,
            ),
            delta=1e-2,
        )

        box = assembly.bounding_box()
        half_x = max(params.stone_length_mm / 2, params.insulation_outer_radius_mm)
        half_y = max(params.stone_width_mm / 2, params.dome_length_mm / 2)
        self.assertAlmostEqual(box.min.X, -half_x, delta=1e-4)
        self.assertAlmostEqual(box.max.X, half_x, delta=1e-4)
        self.assertAlmostEqual(box.min.Y, -half_y, delta=1e-4)
        self.assertAlmostEqual(box.max.Y, half_y, delta=1e-4)
        self.assertAlmostEqual(box.min.Z, -params.stone_thickness_mm, delta=1e-4)
        self.assertAlmostEqual(box.max.Z, params.insulation_outer_radius_mm, delta=1e-4)
        self.assertAlmostEqual(stone.bounding_box().max.Z, 0.0, delta=1e-4)
        self.assertAlmostEqual(dome.bounding_box().min.Z, 0.0, delta=1e-4)
        self.assertGreater(dome.volume, 0)
        self.assertGreater(insulation.volume, 0)

    def test_stone_thickness_propagates(self):
        base = self.build(DEFAULT_PARAMETERS)
        extra = 25.0
        thicker = replace(
            DEFAULT_PARAMETERS,
            stone_thickness_mm=DEFAULT_PARAMETERS.stone_thickness_mm + extra,
        )
        modified = self.build(thicker)
        expected_delta = (
            DEFAULT_PARAMETERS.stone_length_mm * DEFAULT_PARAMETERS.stone_width_mm * extra
        )
        self.assertAlmostEqual(modified.volume - base.volume, expected_delta, delta=1e-2)
        self.assertAlmostEqual(
            modified.bounding_box().min.Z,
            base.bounding_box().min.Z - extra,
            delta=1e-4,
        )

    def test_insulation_thickness_propagates(self):
        base = self.build(DEFAULT_PARAMETERS)
        extra = 15.0
        thicker = replace(
            DEFAULT_PARAMETERS,
            insulation_thickness_mm=DEFAULT_PARAMETERS.insulation_thickness_mm + extra,
        )
        modified = self.build(thicker)
        self.assertGreater(modified.volume, base.volume)
        self.assertAlmostEqual(
            modified.bounding_box().max.X,
            base.bounding_box().max.X + extra,
            delta=1e-4,
        )
        self.assertAlmostEqual(
            modified.bounding_box().max.Z,
            base.bounding_box().max.Z + extra,
            delta=1e-4,
        )

    def test_export_writes_step_ap214_and_stl(self):
        assembly = self.build(DEFAULT_PARAMETERS)
        with tempfile.TemporaryDirectory() as tmp:
            step_path, stl_path = self.export(assembly, Path(tmp))
            step_text = step_path.read_text(encoding="utf-8", errors="replace")
            self.assertTrue(step_path.is_file())
            self.assertGreater(step_path.stat().st_size, 1000)
            self.assertIn("ISO-10303-21", step_text)
            self.assertIn("AUTOMOTIVE_DESIGN { 1 0 10303 214", step_text)
            self.assertIn("SI_UNIT(.MILLI.,.METRE.)", step_text)
            self.assertIn(ASSEMBLY_LABEL, step_text)
            self.assertIn(FLOOR_STONE_LABEL, step_text)
            self.assertIn(DOME_SHELL_LABEL, step_text)
            self.assertIn(INSULATION_LAYER_LABEL, step_text)
            stl_bytes = stl_path.read_bytes()
            self.assertGreater(len(stl_bytes), 84)
            triangle_count = int.from_bytes(stl_bytes[80:84], "little")
            self.assertGreater(triangle_count, 0)
            self.assertEqual(len(stl_bytes), 84 + triangle_count * 50)


class ParameterTest(unittest.TestCase):
    def test_defaults_are_positive_finite_millimetre_placeholders(self):
        params = DEFAULT_PARAMETERS
        self.assertEqual(params.stone_length_mm, 300.0)
        self.assertEqual(params.stone_width_mm, 300.0)
        self.assertEqual(params.stone_thickness_mm, 20.0)
        self.assertEqual(params.dome_inner_radius_mm, 160.0)
        self.assertEqual(params.dome_wall_thickness_mm, 12.0)
        self.assertEqual(params.dome_length_mm, 320.0)
        self.assertEqual(params.insulation_thickness_mm, 40.0)
        self.assertEqual(params.dome_outer_radius_mm, 172.0)
        self.assertEqual(params.insulation_outer_radius_mm, 212.0)

    def test_rejects_non_positive_dimensions(self):
        with self.assertRaises(ValueError):
            replace(DEFAULT_PARAMETERS, dome_wall_thickness_mm=0)
        with self.assertRaises(ValueError):
            replace(DEFAULT_PARAMETERS, stone_length_mm=float("nan"))
        with self.assertRaises(ValueError):
            OvenParameters(insulation_thickness_mm=-5)


class OutputPathTest(unittest.TestCase):
    def test_build_output_is_gitignored_and_part_source_is_not(self):
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "cad/output/placeholder_oven_assembly.step"],
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(ignored.returncode, 0)
        tracked = subprocess.run(
            ["git", "check-ignore", "-q", "cad/parts/dome_shell.py"],
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(tracked.returncode, 1)


if __name__ == "__main__":
    unittest.main()
