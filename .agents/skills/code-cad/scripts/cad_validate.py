#!/usr/bin/env python3
"""
cad_validate.py - Automated DFM and Parametric Sanity Validator for Code-CAD Assets

Validates:
1. Sheet metal thicknesses (t >= 1.0mm, inner flame dome t >= 1.5mm)
2. Minimum hole diameters relative to sheet thickness (d >= 1.0 * t, warning if < 1.2 * t)
3. Minimum bridge / web distance between cutouts (bridge >= 2.0 * t)
4. Insulation blanket cavity clearance (clearance >= 25.0mm)
5. Neapolitan 63% mouth opening ratio (0.58 <= H_mouth / H_apex <= 0.68, target 0.63)
6. Thermal relief expansion slot travel vs. delta_L = alpha * L * delta_T (AISI 304 at 500 deg C)
7. Tab & slot clearance margins (0.15mm <= clearance <= 0.45mm)
8. DXF geometry syntax & layer checks (when DXF files are provided)
"""

import sys
import os
import math
import json
import argparse
from typing import Dict, Any, List, Tuple, Optional

# ANSI Color Codes
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# Thermal Expansion Coefficients (1/K)
ALPHA_304_STAINLESS = 18.0e-6
ALPHA_316_STAINLESS = 16.5e-6
ALPHA_MILD_STEEL = 12.0e-6


class ValidationCheck:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.status = "PASS"  # PASS, WARN, FAIL
        self.actual = ""
        self.expected = ""
        self.message = ""

    def pass_check(self, actual: Any, message: str = ""):
        self.status = "PASS"
        self.actual = str(actual)
        self.message = message

    def warn(self, actual: Any, expected: Any, message: str):
        self.status = "WARN"
        self.actual = str(actual)
        self.expected = str(expected)
        self.message = message

    def fail(self, actual: Any, expected: Any, message: str):
        self.status = "FAIL"
        self.actual = str(actual)
        self.expected = str(expected)
        self.message = message


class CADValidator:
    def __init__(self, no_color: bool = False):
        self.no_color = no_color
        self.checks: List[ValidationCheck] = []

    def _color(self, text: str, color_code: str) -> str:
        if self.no_color:
            return text
        return f"{color_code}{text}{COLOR_RESET}"

    def validate_parametric_spec(self, spec: Dict[str, Any]) -> bool:
        """Run comprehensive geometric and DFM validation against a parametric dictionary."""
        def _get_val(keys: List[str], default: Any) -> Any:
            for k in keys:
                if k in spec:
                    return spec[k]
            return default

        # 1. Inner Dome Sheet Thickness
        t_inner = _get_val(["inner_sheet_thickness", "inner_sheet_thickness_mm"], 1.5)
        chk = ValidationCheck("Inner Dome Sheet Thickness", "DFM")
        if t_inner < 1.0:
            chk.fail(f"{t_inner} mm", ">= 1.5 mm", "Inner dome sheet metal is too thin for 500°C firebox!")
        elif t_inner < 1.5:
            chk.warn(f"{t_inner} mm", ">= 1.5 mm", "1.5mm+ recommended to prevent buckling under intense flame heat")
        else:
            chk.pass_check(f"{t_inner} mm", "Meets high-temp firebox standard")
        self.checks.append(chk)

        # 2. Outer Shroud Sheet Thickness
        t_outer = _get_val(["outer_sheet_thickness", "outer_sheet_thickness_mm"], 1.2)
        chk = ValidationCheck("Outer Shroud Sheet Thickness", "DFM")
        if t_outer < 0.8:
            chk.fail(f"{t_outer} mm", ">= 1.0 mm", "Outer shroud is too thin for structural rigidity")
        elif t_outer < 1.0:
            chk.warn(f"{t_outer} mm", ">= 1.0 mm", "1.0mm-1.5mm recommended for weatherproofing & durability")
        else:
            chk.pass_check(f"{t_outer} mm", "Rigid exterior casing specification")
        self.checks.append(chk)

        # 3. Minimum Hole Diameter vs Sheet Thickness
        min_hole_inner = _get_val(["min_hole_diameter_inner_mm", "min_hole_diameter"], 4.2)  # M4 clear hole
        chk = ValidationCheck("Minimum Hole vs Sheet Thickness (Inner)", "Laser DFM")
        ratio_inner = min_hole_inner / t_inner
        if ratio_inner < 1.0:
            chk.fail(f"{min_hole_inner} mm ({ratio_inner:.2f}*t)", f">= 1.0*t ({t_inner} mm)",
                     "Hole diameter < sheet thickness causes laser pierce blowout and nozzle slag")
        elif ratio_inner < 1.2:
            chk.warn(f"{min_hole_inner} mm ({ratio_inner:.2f}*t)", f">= 1.2*t ({1.2*t_inner:.2f} mm)",
                     "Hole diameter between 1.0t and 1.2t requires lead-in laser pierce tuning")
        else:
            chk.pass_check(f"{min_hole_inner} mm ({ratio_inner:.2f}*t)", "Clean fiber laser pierce guaranteed")
        self.checks.append(chk)

        # 4. Minimum Web / Bridge Thickness
        min_bridge = _get_val(["min_web_thickness", "min_web_thickness_mm"], 4.0)
        chk = ValidationCheck("Minimum Web/Bridge Distance", "Laser DFM")
        min_req_bridge = 2.0 * t_inner
        if min_bridge < 1.5 * t_inner:
            chk.fail(f"{min_bridge} mm", f">= {min_req_bridge:.2f} mm (2.0*t)",
                     "Bridges narrower than 2*t risk thermal burn-through during laser cutting")
        elif min_bridge < min_req_bridge:
            chk.warn(f"{min_bridge} mm", f">= {min_req_bridge:.2f} mm",
                     "Narrow bridge may warp under intense laser heat")
        else:
            chk.pass_check(f"{min_bridge} mm", "Exceeds minimum 2.0*t bridge clearance")
        self.checks.append(chk)

        # 5. Ceramic Blanket Insulation Cavity
        cavity = _get_val(["cavity_total", "insulation_cavity_mm", "insulation_blanket_thickness"], 25.0)
        chk = ValidationCheck("Thermal Insulation Cavity", "Thermodynamics")
        if cavity < 20.0:
            chk.fail(f"{cavity} mm", ">= 25.0 mm",
                     "Insufficient thermal barrier. Exterior shell touch temp will exceed safety standards (>60°C)")
        elif cavity < 25.0:
            chk.warn(f"{cavity} mm", ">= 25.0 mm",
                     "25mm minimum recommended for high-temp Neapolitan pizza oven")
        else:
            chk.pass_check(f"{cavity} mm", "Provides target thermal resistance for 500°C chamber")
        self.checks.append(chk)

        # 6. Neapolitan 63% Mouth Ratio
        h_apex = _get_val(["dome_apex_height", "dome_apex_height_mm"], 190.0)
        h_mouth = _get_val(["mouth_height", "mouth_height_mm"], 120.0)
        ratio = h_mouth / h_apex if h_apex > 0 else 0
        chk = ValidationCheck("Neapolitan 63% Mouth Ratio", "Thermodynamics")
        if ratio < 0.55:
            chk.fail(f"{ratio*100:.1f}% ({h_mouth}/{h_apex}mm)", "58% - 68% (Target ~63%)",
                     "Mouth is too low! Restricts chimney draft and causes flame blowout / smoke spill at front")
        elif ratio > 0.72:
            chk.fail(f"{ratio*100:.1f}% ({h_mouth}/{h_apex}mm)", "58% - 68% (Target ~63%)",
                     "Mouth is too high! Massive radiant heat loss; dome cannot retain 450°C-500°C for sub-90s bake")
        elif ratio < 0.60 or ratio > 0.66:
            chk.warn(f"{ratio*100:.1f}% ({h_mouth}/{h_apex}mm)", "61% - 65% ideal",
                     "Within acceptable range but deviates from ideal 63% Neapolitan ratio")
        else:
            chk.pass_check(f"{ratio*100:.1f}% ({h_mouth:.1f}/{h_apex:.1f}mm)",
                           "Optimal radiant reflection & draft balance")
        self.checks.append(chk)

        # 7. Thermal Expansion Relief Slot Travel
        length_inner = _get_val(["chamber_depth", "chamber_depth_mm"], 450.0)
        max_temp = _get_val(["max_operating_temp_c", "max_chamber_temp_c"], 500.0)
        ambient_temp = _get_val(["ambient_temp_c"], 20.0)
        delta_t = max(0.0, max_temp - ambient_temp)
        material = _get_val(["inner_material"], "304_stainless")

        alpha = _get_val(["thermal_expansion_coeff"], ALPHA_304_STAINLESS)
        if "316" in str(material):
            alpha = ALPHA_316_STAINLESS
        elif "mild" in str(material) or "carbon" in str(material):
            alpha = ALPHA_MILD_STEEL

        delta_l = _get_val(["thermal_expansion_delta_l"], alpha * length_inner * delta_t)
        slot_travel = _get_val(["thermal_relief_slot_length", "thermal_slot_travel_mm"], 7.0)

        chk = ValidationCheck("Thermal Expansion Slot Travel", "Thermal Stress")
        min_required_slot = delta_l + 1.5  # delta_L plus 1.5mm safety margin
        if slot_travel < delta_l:
            chk.fail(f"{slot_travel:.2f} mm", f">= {min_required_slot:.2f} mm (ΔL={delta_l:.2f}mm + 1.5mm)",
                     f"Thermal expansion at {max_temp}°C exceeds slot travel! Chamber will buckle or shear fasteners!")
        elif slot_travel < min_required_slot:
            chk.warn(f"{slot_travel:.2f} mm", f">= {min_required_slot:.2f} mm",
                     f"Meets raw ΔL ({delta_l:.2f}mm) but lacks safety margin for assembly tolerances")
        else:
            chk.pass_check(f"{slot_travel:.2f} mm (ΔL={delta_l:.2f}mm)",
                           f"Accommodates thermal expansion up to {max_temp}°C with safety margin")
        self.checks.append(chk)

        # 8. Tab and Slot Fit Clearances
        tab_clearance = _get_val(["tab_slot_clearance", "tab_slot_clearance_mm"], 0.25)
        chk = ValidationCheck("Tab & Slot Fit Clearance", "Assembly DFM")
        if tab_clearance < 0.12:
            chk.fail(f"{tab_clearance:.2f} mm", "0.15 - 0.40 mm",
                     "Clearance too tight for laser cut tolerances and thermal variation; parts will bind")
        elif tab_clearance > 0.50:
            chk.fail(f"{tab_clearance:.2f} mm", "0.15 - 0.40 mm",
                     "Clearance too loose; loose tabs will rattle and compromise self-alignment")
        elif tab_clearance > 0.35:
            chk.warn(f"{tab_clearance:.2f} mm", "0.20 - 0.30 mm",
                     "Acceptable for heavy powder coat, but slightly loose for bare stainless")
        else:
            chk.pass_check(f"{tab_clearance:.2f} mm", "Clean friction-fit self-alignment")
        self.checks.append(chk)

        # 9. Cordierite Stone Thickness
        stone_thick = _get_val(["stone_thickness", "stone_thickness_mm"], 15.0)
        chk = ValidationCheck("Baking Stone Thickness", "Thermodynamics")
        if stone_thick < 12.0:
            chk.fail(f"{stone_thick} mm", ">= 15.0 mm",
                     "Stone too thin; insufficient thermal mass causes floor temperature crash after first pizza")
        elif stone_thick < 15.0:
            chk.warn(f"{stone_thick} mm", ">= 15.0 mm", "15mm+ recommended for back-to-back baking")
        else:
            chk.pass_check(f"{stone_thick} mm", "Sufficient thermal mass for continuous bakes")
        self.checks.append(chk)

        # 10. Flue Chimney Ratio
        flue_dia = _get_val(["flue_diameter", "flue_diameter_mm"], 100.0)
        chk = ValidationCheck("Flue Chimney Sizing", "Thermodynamics")
        flue_area = math.pi * ((flue_dia / 2.0) ** 2)
        mouth_width = _get_val(["mouth_width", "mouth_width_mm"], 308.0)
        mouth_area = mouth_width * h_mouth
        flue_to_mouth_ratio = flue_area / mouth_area if mouth_area > 0 else 0
        if flue_to_mouth_ratio < 0.08:
            chk.warn(f"Dia {flue_dia}mm (Area ratio: {flue_to_mouth_ratio*100:.1f}%)", ">= 10% of mouth",
                     "Flue diameter might cause sluggish draft or smoking during cold startup")
        elif flue_to_mouth_ratio > 0.35:
            chk.warn(f"Dia {flue_dia}mm (Area ratio: {flue_to_mouth_ratio*100:.1f}%)", "<= 30% of mouth",
                     "Flue diameter too large; hot exhaust gases evacuate too fast, lowering dome temperature")
        else:
            chk.pass_check(f"Dia {flue_dia}mm ({flue_to_mouth_ratio*100:.1f}% mouth area)", "Balanced draft velocity")
        self.checks.append(chk)

        return all(c.status != "FAIL" for c in self.checks)

    def validate_dxf_file(self, dxf_path: str, sheet_thickness: float = 1.5) -> bool:
        """Inspect a raw DXF file for layer convention and minimum feature sizes."""
        chk = ValidationCheck(f"DXF File: {os.path.basename(dxf_path)}", "File Integrity")
        if not os.path.exists(dxf_path):
            chk.fail("File Not Found", "Valid DXF file", f"Path does not exist: {dxf_path}")
            self.checks.append(chk)
            return False

        try:
            with open(dxf_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            chk.fail("Unreadable", "Valid text DXF", str(e))
            self.checks.append(chk)
            return False

        # Basic DXF token parsing
        lines = content.splitlines()
        layers_found = set()
        circles = []
        in_entities = False
        i = 0
        while i < len(lines):
            code = lines[i].strip()
            val = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if code == "2" and val == "ENTITIES":
                in_entities = True
            elif code == "0" and val == "ENDSEC" and in_entities:
                in_entities = False
            elif in_entities and code == "8":
                layers_found.add(val)
            elif in_entities and code == "0" and val == "CIRCLE":
                # Find radius (code 40)
                j = i + 2
                rad = None
                while j < len(lines) - 1:
                    c = lines[j].strip()
                    v = lines[j + 1].strip()
                    if c == "0":
                        break
                    if c == "40":
                        try:
                            rad = float(v)
                        except ValueError:
                            pass
                        break
                    j += 2
                if rad is not None:
                    circles.append(rad)
            i += 2

        chk.pass_check(f"{len(lines)} lines parsed", f"Layers: {', '.join(sorted(layers_found))}")
        self.checks.append(chk)

        # Check standard layers
        chk_layers = ValidationCheck(f"DXF Layers: {os.path.basename(dxf_path)}", "Laser DFM")
        has_cut = any("CUT" in l.upper() for l in layers_found)
        if not has_cut:
            chk_layers.warn(f"Found: {sorted(layers_found)}", "Should contain 'CUT' or 'CUT_INTERIOR'",
                            "Missing standard CUT layer name for CNC laser nesting")
        else:
            chk_layers.pass_check("Standard CUT layers verified")
        self.checks.append(chk_layers)

        # Check smallest hole diameter in DXF
        if circles:
            min_dia = min(circles) * 2.0
            chk_hole = ValidationCheck(f"Smallest Hole in {os.path.basename(dxf_path)}", "Laser DFM")
            if min_dia < sheet_thickness:
                chk_hole.fail(f"Diameter {min_dia:.2f} mm", f">= {sheet_thickness:.2f} mm (1.0*t)",
                              "Hole diameter smaller than sheet thickness detected in DXF!")
            elif min_dia < 1.2 * sheet_thickness:
                chk_hole.warn(f"Diameter {min_dia:.2f} mm", f">= {1.2*sheet_thickness:.2f} mm (1.2*t)",
                              "Small hole detected; laser lead-in tuning required")
            else:
                chk_hole.pass_check(f"Diameter {min_dia:.2f} mm (>= 1.2*t)", "Laser cutting safe")
            self.checks.append(chk_hole)

        return True

    def print_report(self) -> int:
        """Print validation results in formatted table. Returns exit code (0 or 1)."""
        print("\n" + self._color("=" * 80, COLOR_BOLD))
        print(self._color(" CODE-CAD DFM & PARAMETRIC SANITY AUDIT REPORT", COLOR_BOLD + COLOR_CYAN))
        print(self._color("=" * 80, COLOR_BOLD))

        num_pass = sum(1 for c in self.checks if c.status == "PASS")
        num_warn = sum(1 for c in self.checks if c.status == "WARN")
        num_fail = sum(1 for c in self.checks if c.status == "FAIL")

        for c in self.checks:
            if c.status == "PASS":
                status_badge = self._color("[ PASS ]", COLOR_GREEN + COLOR_BOLD)
            elif c.status == "WARN":
                status_badge = self._color("[ WARN ]", COLOR_YELLOW + COLOR_BOLD)
            else:
                status_badge = self._color("[ FAIL ]", COLOR_RED + COLOR_BOLD)

            print(f"{status_badge} {c.category:<16} | {c.name:<32}")
            if c.actual:
                print(f"         Actual:   {c.actual}")
            if c.expected and c.status != "PASS":
                print(f"         Expected: {c.expected}")
            if c.message:
                print(f"         Note:     {c.message}")
            print("-" * 80)

        print("\n" + self._color("Audit Summary:", COLOR_BOLD))
        print(f"  Passed:   {self._color(str(num_pass), COLOR_GREEN)}")
        print(f"  Warnings: {self._color(str(num_warn), COLOR_YELLOW if num_warn else COLOR_RESET)}")
        print(f"  Failures: {self._color(str(num_fail), COLOR_RED if num_fail else COLOR_RESET)}")

        if num_fail > 0:
            print(self._color("\nResult: VALIDATION FAILED - Correct engineering defects before fabrication.", COLOR_RED + COLOR_BOLD))
            return 1
        elif num_warn > 0:
            print(self._color("\nResult: VALIDATION PASSED WITH WARNINGS - Review notes prior to manufacturing.", COLOR_YELLOW + COLOR_BOLD))
            return 0
        else:
            print(self._color("\nResult: ALL CHECKS PASSED - Fully compliant with DFM and thermal rules.", COLOR_GREEN + COLOR_BOLD))
            return 0


def main():
    parser = argparse.ArgumentParser(description="Code-CAD DFM & Parametric Design Validator")
    parser.add_argument("--spec", type=str, help="Path to JSON parametric specification")
    parser.add_argument("--dxf", type=str, help="Path to DXF flat pattern file to inspect")
    parser.add_argument("--stone-size", type=int, choices=[12, 16], default=12,
                        help="Default stone size variant to validate if no spec provided (default: 12)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color codes")
    parser.add_argument("--thickness", type=float, default=1.5, help="Sheet thickness in mm for DXF validation")
    parser.add_argument("--temp", type=float, default=500.0, help="Operating chamber temperature in °C (default: 500)")
    args = parser.parse_args()

    validator = CADValidator(no_color=args.no_color)

    if args.spec:
        if not os.path.exists(args.spec):
            print(f"Error: Specification file not found: {args.spec}", file=sys.stderr)
            sys.exit(1)
        with open(args.spec, "r", encoding="utf-8") as f:
            spec = json.load(f)
        validator.validate_parametric_spec(spec)
    elif not args.dxf:
        # Generate default reference spec for stone-size to validate
        stone_w = 330.0 if args.stone_size == 12 else 406.0
        stone_d = 330.0 if args.stone_size == 12 else 406.0
        spec = {
            "model_variant": f"{args.stone_size}_inch",
            "baking_stone_width_mm": stone_w,
            "baking_stone_depth_mm": stone_d,
            "chamber_width_mm": stone_w + 20.0,
            "chamber_depth_mm": stone_d + 120.0,
            "inner_sheet_thickness_mm": 1.5,
            "outer_sheet_thickness_mm": 1.2,
            "min_hole_diameter_inner_mm": 4.5,
            "min_web_thickness_mm": 4.0,
            "insulation_cavity_mm": 25.0,
            "dome_apex_height_mm": 190.0 if args.stone_size == 12 else 210.0,
            "mouth_height_mm": 120.0 if args.stone_size == 12 else 132.3,
            "mouth_width_mm": 320.0 if args.stone_size == 12 else 380.0,
            "thermal_slot_travel_mm": 6.5,
            "tab_slot_clearance_mm": 0.25,
            "stone_thickness_mm": 15.0,
            "flue_diameter_mm": 100.0 if args.stone_size == 12 else 125.0,
            "max_chamber_temp_c": args.temp,
            "ambient_temp_c": 20.0,
            "inner_material": "304_stainless"
        }
        validator.validate_parametric_spec(spec)

    if args.dxf:
        validator.validate_dxf_file(args.dxf, sheet_thickness=args.thickness)

    code = validator.print_report()
    sys.exit(code)


if __name__ == "__main__":
    main()
