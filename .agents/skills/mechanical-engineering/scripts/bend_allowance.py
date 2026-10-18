#!/usr/bin/env python3
"""
bend_allowance.py - Sheet Metal Bending & Flat Layout Calculator

Calculates Bend Allowance (BA), Outside Setback (OSSB), Bend Deduction (BD),
and flat blank layout sizes for precision CNC sheet metal fabrication.
Includes DFM checks for minimum flange length and hole distances.
"""

import argparse
import math
import sys
import json


DEFAULT_K_FACTORS = {
    "ss304": 0.38,       # AISI 304 Stainless Steel (Air bending)
    "ss316": 0.38,       # AISI 316 Stainless Steel
    "mild_steel": 0.42,  # Carbon / Mild Steel (e.g. Q235, S235JR)
    "al5052": 0.40,      # Aluminum 5052-H32
    "copper": 0.44       # Soft Copper / Brass
}


def calculate_bend_parameters(thickness: float,
                              radius: float,
                              angle_deg: float,
                              k_factor: float):
    """
    Compute BA, OSSB, and BD for a sheet metal bend.

    Parameters:
    - thickness (T): Material thickness in mm
    - radius (R): Inside bend radius in mm
    - angle_deg (A): Bend angle in degrees (e.g., 90 for a right-angle bend)
    - k_factor (K): Neutral axis position ratio t/T (0 < K < 1)

    Formulas:
    - BA = (pi / 180) * angle * (R + K * T)
    - OSSB = tan(angle / 2) * (R + T)
    - BD = 2 * OSSB - BA
    """
    rad = math.radians(angle_deg)
    
    # Bend Allowance
    ba = (math.pi / 180.0) * angle_deg * (radius + k_factor * thickness)
    
    # Outside Setback
    ossb = math.tan(rad / 2.0) * (radius + thickness)
    
    # Bend Deduction
    bd = (2.0 * ossb) - ba
    
    return {
        "thickness_mm": thickness,
        "inside_radius_mm": radius,
        "bend_angle_deg": angle_deg,
        "k_factor": k_factor,
        "bend_allowance_mm": round(ba, 4),
        "outside_setback_mm": round(ossb, 4),
        "bend_deduction_mm": round(bd, 4)
    }


def calculate_flat_blank(flange_lengths: list,
                         thickness: float,
                         radius: float,
                         angle_deg: float,
                         k_factor: float):
    """
    Compute flat blank length from external flange dimensions.
    For N flanges with (N - 1) identical bends:
    Flat Length = sum(flanges) - (N - 1) * BD
    """
    bend_params = calculate_bend_parameters(thickness, radius, angle_deg, k_factor)
    bd = bend_params["bend_deduction_mm"]
    num_bends = max(0, len(flange_lengths) - 1)
    
    total_outside_flanges = sum(flange_lengths)
    total_deduction = num_bends * bd
    flat_length = total_outside_flanges - total_deduction
    
    return {
        "flanges": flange_lengths,
        "num_bends": num_bends,
        "total_flange_length_mm": round(total_outside_flanges, 4),
        "total_bend_deduction_mm": round(total_deduction, 4),
        "flat_blank_length_mm": round(flat_length, 4),
        "bend_parameters": bend_params
    }


def check_dfm_rules(thickness: float, radius: float):
    """
    DFM guidelines for sheet metal:
    - Minimum Flange Length: typically b_min = 4 * T + R (or based on standard V-die opening V = 6T to 8T)
    - Minimum Hole-to-Bend Distance: d_min = 2.5 * T + R (to prevent hole stretching/distortion)
    - Minimum Hole-to-Edge Distance: e_min = 2.0 * T
    - Minimum Hole Diameter: d_hole_min = 1.0 * T (stainless), 0.8 * T (mild steel)
    - Minimum Slot-to-Bend Distance: s_min = 3.0 * T + R
    """
    recommended_v_die = 8.0 * thickness
    min_flange = 4.0 * thickness + radius
    min_hole_to_bend = 2.5 * thickness + radius
    min_hole_to_edge = 2.0 * thickness
    min_hole_diameter = 1.0 * thickness
    
    return {
        "recommended_v_die_width_mm": round(recommended_v_die, 2),
        "min_flange_length_mm": round(min_flange, 2),
        "min_hole_to_bend_center_mm": round(min_hole_to_bend, 2),
        "min_hole_to_edge_dist_mm": round(min_hole_to_edge, 2),
        "min_hole_diameter_mm": round(min_hole_diameter, 2)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Sheet Metal Bend Allowance, Deduction & DFM Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 90° bend in 2mm 304 Stainless with 2mm inside radius:
  python3 bend_allowance.py -t 2.0 -r 2.0 -a 90 --material ss304

  # Flat layout for U-channel (flanges: 30mm, 120mm, 30mm):
  python3 bend_allowance.py -t 1.5 -r 1.5 -f 30 120 30 --material ss304
        """
    )
    parser.add_argument("-t", "--thickness", type=float, required=True,
                        help="Sheet thickness in mm (e.g. 1.5, 2.0, 3.0)")
    parser.add_argument("-r", "--radius", type=float, default=None,
                        help="Inside bend radius in mm (default: equals sheet thickness)")
    parser.add_argument("-a", "--angle", type=float, default=90.0,
                        help="Bend angle in degrees (default: 90.0)")
    parser.add_argument("-k", "--k-factor", type=float, default=None,
                        help="Neutral axis K-factor (default: based on material, or 0.40)")
    parser.add_argument("-m", "--material", type=str, default="ss304",
                        choices=list(DEFAULT_K_FACTORS.keys()),
                        help="Material preset for K-factor selection (default: ss304)")
    parser.add_argument("-f", "--flanges", type=float, nargs="+", default=None,
                        help="Outer flange lengths in mm (e.g. -f 50 100 50)")
    parser.add_argument("--json", action="store_true",
                        help="Output results in JSON format")

    args = parser.parse_args()

    # Determine inside radius
    radius = args.radius if args.radius is not None else args.thickness

    # Determine K-factor
    if args.k_factor is not None:
        k_factor = args.k_factor
    else:
        k_factor = DEFAULT_K_FACTORS.get(args.material.lower(), 0.40)

    # DFM checks
    dfm = check_dfm_rules(args.thickness, radius)

    if args.flanges:
        results = calculate_flat_blank(args.flanges, args.thickness, radius, args.angle, k_factor)
        results["dfm_guidelines"] = dfm
        results["material"] = args.material
    else:
        bend_calc = calculate_bend_parameters(args.thickness, radius, args.angle, k_factor)
        results = {
            "material": args.material,
            "bend_parameters": bend_calc,
            "dfm_guidelines": dfm
        }

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # Formatted CLI output
    print("=" * 65)
    print(" SHEET METAL BEND ALLOWANCE & FLAT BLANK CALCULATOR")
    print("=" * 65)
    print(f" Material:           {args.material.upper()} (K-factor: {k_factor:.3f})")
    print(f" Thickness (T):      {args.thickness:.2f} mm")
    print(f" Inside Radius (R):  {radius:.2f} mm (R/T ratio: {radius / args.thickness:.2f})")
    print(f" Bend Angle (A):     {args.angle:.1f}°")
    print("-" * 65)

    bp = results["bend_parameters"] if "bend_parameters" in results else results
    if "bend_parameters" in results and isinstance(results["bend_parameters"], dict):
        bp = results["bend_parameters"]
        
    print(f" Bend Allowance (BA):  {bp['bend_allowance_mm']:8.3f} mm")
    print(f" Outside Setback (OSSB):{bp['outside_setback_mm']:8.3f} mm")
    print(f" Bend Deduction (BD):  {bp['bend_deduction_mm']:8.3f} mm")
    print("-" * 65)

    if args.flanges:
        print(f" Flanges (outside):    {args.flanges} mm")
        print(f" Number of Bends:      {results['num_bends']}")
        print(f" Total Flange Sum:     {results['total_flange_length_mm']:8.3f} mm")
        print(f" Total Bend Deduction: {results['total_bend_deduction_mm']:8.3f} mm")
        print(f" >>> FLAT BLANK SIZE:  {results['flat_blank_length_mm']:8.3f} mm <<<")
        print("-" * 65)

        # Check flanges against min flange
        min_flange = dfm["min_flange_length_mm"]
        for idx, fl in enumerate(args.flanges):
            if fl < min_flange:
                print(f" [WARNING] Flange #{idx+1} ({fl}mm) is smaller than min recommended flange ({min_flange}mm)!")

    print(" DFM DESIGN RULES:")
    print(f"   Recommended V-Die Width:       {dfm['recommended_v_die_width_mm']} mm (8 * T)")
    print(f"   Minimum Flange Length:         {dfm['min_flange_length_mm']} mm (4 * T + R)")
    print(f"   Min Hole-to-Bend Center:       {dfm['min_hole_to_bend_center_mm']} mm (2.5 * T + R)")
    print(f"   Min Hole-to-Edge Distance:     {dfm['min_hole_to_edge_dist_mm']} mm (2.0 * T)")
    print(f"   Min Laser Cut Hole Diameter:   {dfm['min_hole_diameter_mm']} mm (1.0 * T)")
    print("=" * 65)


if __name__ == "__main__":
    main()
