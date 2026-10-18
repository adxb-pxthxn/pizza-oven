#!/usr/bin/env python3
"""
thermal_expansion.py - Thermal Expansion & Joint Clearance Calculator

Calculates thermal expansion, differential movement, and slot/gap clearance
requirements for high-temperature pizza oven components (Stainless Steel 304,
Mild Steel, Cordierite Refractory Stone) across 20°C to 550°C.
"""

import argparse
import json
import sys


# Material thermal properties database
# alpha: linear coefficient of thermal expansion (1/K) over 20°C - 550°C
# E: Young's Modulus in GPa at room temperature
# yield_strength_hot: typical yield strength in MPa at 500°C
MATERIALS = {
    "ss304": {
        "name": "AISI 304 Stainless Steel (1.4301)",
        "alpha": 18.0e-6,           # 18.0 um/(m*K)
        "modulus_gpa": 193.0,
        "yield_strength_20c_mpa": 230.0,
        "yield_strength_500c_mpa": 130.0,
        "poisson": 0.29,
        "food_contact_safe": True
    },
    "ss316": {
        "name": "AISI 316 Stainless Steel (1.4401)",
        "alpha": 17.5e-6,
        "modulus_gpa": 195.0,
        "yield_strength_20c_mpa": 250.0,
        "yield_strength_500c_mpa": 150.0,
        "poisson": 0.30,
        "food_contact_safe": True
    },
    "mild_steel": {
        "name": "Carbon / Structural Mild Steel (S235 / Q235)",
        "alpha": 13.0e-6,           # 13.0 um/(m*K)
        "modulus_gpa": 210.0,
        "yield_strength_20c_mpa": 235.0,
        "yield_strength_500c_mpa": 110.0,
        "poisson": 0.30,
        "food_contact_safe": False  # Rusts / not suitable for direct food contact
    },
    "cordierite": {
        "name": "Cordierite Ceramic Baking Stone (2MgO·2Al2O3·5SiO2)",
        "alpha": 2.8e-6,            # 2.8 um/(m*K) - ultra low thermal shock expansion
        "modulus_gpa": 125.0,
        "compressive_strength_mpa": 350.0,
        "tensile_strength_mpa": 25.0,  # Brittle ceramic
        "poisson": 0.25,
        "food_contact_safe": True
    },
    "firebrick": {
        "name": "Refractory Alumina-Silica Firebrick",
        "alpha": 5.5e-6,
        "modulus_gpa": 80.0,
        "compressive_strength_mpa": 40.0,
        "tensile_strength_mpa": 5.0,
        "poisson": 0.20,
        "food_contact_safe": True
    },
    "aluminum": {
        "name": "Aluminum Alloy 5052 (Exterior chassis only)",
        "alpha": 23.8e-6,
        "modulus_gpa": 70.0,
        "yield_strength_20c_mpa": 190.0,
        "yield_strength_500c_mpa": 15.0,  # Loses all strength above 250°C!
        "poisson": 0.33,
        "food_contact_safe": False
    }
}


def calculate_expansion(initial_length_mm: float,
                        mat_key: str,
                        t_initial: float = 20.0,
                        t_final: float = 500.0):
    """
    Compute linear expansion: delta_L = L * alpha * delta_T
    """
    mat = MATERIALS[mat_key]
    delta_t = t_final - t_initial
    alpha = mat["alpha"]
    delta_l = initial_length_mm * alpha * delta_t
    final_length = initial_length_mm + delta_l

    # Theoretical thermal stress if 100% rigidly constrained:
    # sigma = E * alpha * delta_T
    e_gpa = mat["modulus_gpa"]
    stress_mpa = (e_gpa * 1e3) * alpha * delta_t

    return {
        "material_key": mat_key,
        "material_name": mat["name"],
        "alpha_per_k": alpha,
        "initial_length_mm": initial_length_mm,
        "t_initial_c": t_initial,
        "t_final_c": t_final,
        "delta_t_c": delta_t,
        "delta_length_mm": round(delta_l, 4),
        "final_length_mm": round(final_length, 4),
        "pct_expansion": round((delta_l / initial_length_mm) * 100.0, 4),
        "constrained_thermal_stress_mpa": round(stress_mpa, 2)
    }


def calculate_differential_interface(length_mm: float,
                                     mat_a_key: str,
                                     mat_b_key: str,
                                     t_a_final: float,
                                     t_b_final: float,
                                     t_initial: float = 20.0,
                                     safety_factor: float = 1.5):
    """
    Calculate differential movement between two mating parts.
    Example: Cordierite stone in SS304 tray, or SS304 hot liner inside mild steel cold skin.
    """
    res_a = calculate_expansion(length_mm, mat_a_key, t_initial, t_a_final)
    res_b = calculate_expansion(length_mm, mat_b_key, t_initial, t_b_final)

    diff_movement = abs(res_a["delta_length_mm"] - res_b["delta_length_mm"])
    recommended_clearance = diff_movement * safety_factor

    # Fastener slot length calculation:
    # If a bolt secures part A to part B, slot must accommodate the relative thermal slide
    recommended_slot_extra_length = recommended_clearance

    return {
        "nominal_dimension_mm": length_mm,
        "ambient_temp_c": t_initial,
        "part_a": res_a,
        "part_b": res_b,
        "absolute_differential_movement_mm": round(diff_movement, 4),
        "safety_factor": safety_factor,
        "recommended_thermal_gap_mm": round(recommended_clearance, 3),
        "recommended_slot_expansion_travel_mm": round(recommended_slot_extra_length, 3)
    }


def main():
    parser = argparse.ArgumentParser(
        description="High-Temperature Thermal Expansion & Clearance Gap Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check 400mm SS304 oven tray expanding from 20°C to 500°C:
  python3 thermal_expansion.py -l 400 -m ss304 -t1 20 -t2 500

  # Check differential expansion between 350mm Cordierite stone and SS304 tray:
  python3 thermal_expansion.py -l 350 -m ss304 --mat2 cordierite -t1 20 -t2 500

  # Check SS304 hot inner shell (500°C) vs Mild Steel outer chassis (60°C):
  python3 thermal_expansion.py -l 500 -m ss304 --mat2 mild_steel --temp-a 500 --temp-b 60
        """
    )
    parser.add_argument("-l", "--length", type=float, required=True,
                        help="Nominal dimension / length at ambient temperature (mm)")
    parser.add_argument("-m", "--material", type=str, default="ss304",
                        choices=list(MATERIALS.keys()),
                        help="Primary material (default: ss304)")
    parser.add_argument("--mat2", type=str, default=None,
                        choices=list(MATERIALS.keys()),
                        help="Secondary mating material for differential analysis")
    parser.add_argument("-t1", "--t-initial", type=float, default=20.0,
                        help="Initial ambient temperature in °C (default: 20.0)")
    parser.add_argument("-t2", "--t-final", type=float, default=500.0,
                        help="Operating temperature in °C (default: 500.0)")
    parser.add_argument("--temp-a", type=float, default=None,
                        help="Operating temp of primary material (overrides -t2)")
    parser.add_argument("--temp-b", type=float, default=None,
                        help="Operating temp of secondary material (overrides -t2)")
    parser.add_argument("-s", "--safety-factor", type=float, default=1.5,
                        help="Safety factor for thermal clearance gaps (default: 1.5)")
    parser.add_argument("--json", action="store_true",
                        help="Output results in JSON format")

    args = parser.parse_args()

    t_a = args.temp_a if args.temp_a is not None else args.t_final
    t_b = args.temp_b if args.temp_b is not None else args.t_final

    if args.mat2:
        results = calculate_differential_interface(
            args.length, args.material, args.mat2, t_a, t_b, args.t_initial, args.safety_factor
        )
    else:
        results = calculate_expansion(args.length, args.material, args.t_initial, t_a)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # CLI Output
    print("=" * 72)
    print(" THERMAL EXPANSION & JOINT CLEARANCE CALCULATOR")
    print("=" * 72)

    if args.mat2:
        pa = results["part_a"]
        pb = results["part_b"]
        print(f" Component 1:      {pa['material_name']}")
        print(f"   Alpha:          {pa['alpha_per_k']*1e6:.1f} µm/(m·K)  |  Temp: {pa['t_initial_c']}°C -> {pa['t_final_c']}°C")
        print(f"   Delta L:        +{pa['delta_length_mm']:.3f} mm  ({pa['pct_expansion']:.3f}%)  -> Final: {pa['final_length_mm']:.3f} mm")
        print("-" * 72)
        print(f" Component 2:      {pb['material_name']}")
        print(f"   Alpha:          {pb['alpha_per_k']*1e6:.1f} µm/(m·K)  |  Temp: {pb['t_initial_c']}°C -> {pb['t_final_c']}°C")
        print(f"   Delta L:        +{pb['delta_length_mm']:.3f} mm  ({pb['pct_expansion']:.3f}%)  -> Final: {pb['final_length_mm']:.3f} mm")
        print("=" * 72)
        print(f" DIFFERENTIAL DISPLACEMENT:        {results['absolute_differential_movement_mm']:8.3f} mm")
        print(f" RECOMMENDED MINIMUM CLEARANCE:    {results['recommended_thermal_gap_mm']:8.3f} mm  (Safety Factor: {results['safety_factor']}x)")
        print(f" RECOMMENDED FASTENER SLOT TRAVEL: {results['recommended_slot_expansion_travel_mm']:8.3f} mm")
        print("=" * 72)
        print(" ENGINEERING DESIGN NOTES:")
        if args.material == "ss304" and args.mat2 == "cordierite":
            print(" * Cordierite Stone Fit: SS304 expands >6x more than cordierite.")
            print("   DO NOT mechanically clamp cordierite edges. Provide floating corner brackets")
            print(f"   with minimum {results['recommended_thermal_gap_mm']} mm perimeter perimeter expansion gap.")
            print("   Direct clamping will shatter the brittle stone when heated or cooled.")
        elif args.material == "ss304" and args.mat2 == "mild_steel":
            print(" * Bi-Metallic Thermal Strain: Rigidly bolting hot SS304 to cooler mild steel")
            print("   will induce severe thermal warping and shear bolt fatigue.")
            print(f"   Use slotted holes (min extra slot length {results['recommended_slot_expansion_travel_mm']} mm)")
            print("   fitted with Belleville spring washers to allow controlled slip without loose rattles.")
    else:
        print(f" Material:         {results['material_name']}")
        print(f" Nominal Length:   {results['initial_length_mm']:.2f} mm")
        print(f" Temperature:      {results['t_initial_c']:.1f}°C -> {results['t_final_c']:.1f}°C (Delta T: {results['delta_t_c']:.1f}°C)")
        print(f" Alpha (CTE):      {results['alpha_per_k']*1e6:.2f} µm/(m·K)")
        print("-" * 72)
        print(f" Thermal Expansion (Delta L): {results['delta_length_mm']:8.3f} mm")
        print(f" Final Heated Length:         {results['final_length_mm']:8.3f} mm")
        print(f" Percentage Expansion:        {results['pct_expansion']:8.3f} %")
        print("-" * 72)
        print(f" Constrained Stress (if fully held): {results['constrained_thermal_stress_mpa']:8.1f} MPa")
        mat_info = MATERIALS[args.material]
        hot_yield = mat_info.get("yield_strength_500c_mpa", 100.0)
        print(f" Material Hot Yield Strength (500°C): {hot_yield:.1f} MPa")
        if results['constrained_thermal_stress_mpa'] > hot_yield:
            print(" [CRITICAL WARNING] Constrained thermal stress exceeds yield strength!")
            print(" Parts WILL buckle or plastically deform without thermal expansion relief joints!")
        print("=" * 72)


if __name__ == "__main__":
    main()
