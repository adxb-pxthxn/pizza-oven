#!/usr/bin/env python3
"""
thermal_model.py - Pizza Oven Multi-Layer Thermal & Insulation Modeling Tool

Models:
1. Multi-layer 1D steady-state conductive/convective/radiative heat transfer.
2. Outer shell touch temperature against ISO 13732-1 safety threshold (< 60°C).
3. Total steady-state heat loss through oven dome and floor.
4. Dynamic preheat time to 500°C based on burner input, thermal mass, and flue draft loss.
"""

import argparse
import json
import math
import sys


# Stefan-Boltzmann constant (W / (m^2 * K^4))
SIGMA = 5.670374419e-8

# Typical thermal properties of pizza oven materials
# k: thermal conductivity (W / (m * K))
# density: kg / m^3
# cp: specific heat capacity (J / (kg * K))
MATERIAL_PROPERTIES = {
    "ss304": {
        "name": "AISI 304 Stainless Steel Inner Shell",
        "k": 18.0,
        "density": 7900.0,
        "cp": 500.0,
        "emissivity": 0.65
    },
    "mild_steel_painted": {
        "name": "Powder-Coated Mild Steel Outer Shell",
        "k": 45.0,
        "density": 7850.0,
        "cp": 480.0,
        "emissivity": 0.88  # Powder coat has high emissivity ~0.85-0.92
    },
    "ceramic_fiber": {
        "name": "Ceramic Fiber Blanket (128 kg/m³, e.g. Kaowool)",
        "k": 0.08,          # Mean k across 100°C - 500°C
        "density": 128.0,
        "cp": 1050.0,
        "emissivity": 0.80
    },
    "calcium_silicate": {
        "name": "Calcium Silicate Board (Skamol / Promatect)",
        "k": 0.065,         # Rigid insulation board
        "density": 240.0,
        "cp": 950.0,
        "emissivity": 0.85
    },
    "microporous": {
        "name": "Microporous High-Efficiency Silica Insulation",
        "k": 0.028,
        "density": 320.0,
        "cp": 900.0,
        "emissivity": 0.85
    },
    "cordierite": {
        "name": "Cordierite Ceramic Baking Stone",
        "k": 2.2,           # Ideal moderate conductivity to prevent crust burning
        "density": 2100.0,
        "cp": 950.0,
        "emissivity": 0.88
    },
    "firebrick": {
        "name": "Medium-Duty Firebrick (Refractory Alumina)",
        "k": 1.1,
        "density": 2000.0,
        "cp": 920.0,
        "emissivity": 0.82
    },
    "air_gap": {
        "name": "Still Air Boundary / Stagnant Gap",
        "k": 0.035,
        "density": 1.2,
        "cp": 1005.0,
        "emissivity": 0.50
    }
}


def solve_steady_state_wall(layers: list,
                            t_inner_c: float,
                            t_ambient_c: float = 20.0,
                            h_inner: float = 30.0,
                            ext_emissivity: float = 0.88):
    """
    Solve iterative 1D steady-state heat flux through multi-layer wall.
    layers: list of dicts with {"material": str, "thickness_mm": float}
    """
    t_in_k = t_inner_c + 273.15
    t_amb_k = t_ambient_c + 273.15

    # Sum conductive thermal resistance: R_cond = sum(t_i / k_i) in (m^2 * K / W)
    r_cond = 0.0
    layer_details = []
    total_thickness_mm = 0.0

    for l in layers:
        mat_key = l["material"]
        th_m = l["thickness_mm"] / 1000.0
        mat = MATERIAL_PROPERTIES[mat_key]
        k = mat["k"]
        r_i = th_m / k
        r_cond += r_i
        total_thickness_mm += l["thickness_mm"]
        layer_details.append({
            "material_key": mat_key,
            "name": mat["name"],
            "thickness_mm": l["thickness_mm"],
            "k_w_mk": k,
            "r_value": r_i
        })

    # Internal convective/radiative resistance
    r_inner = 1.0 / h_inner

    # Iterative solver for exterior surface temperature T_ext_k
    # Natural convection correlation (vertical / curved outer shell):
    # h_conv ~ 1.32 * ((T_ext - T_amb) / L)^0.25, approx h_conv = 1.42 * (delta_T / 0.4)^0.25
    # or empirical outdoor/indoor natural convection: h_conv ~ 1.8 * (T_ext - T_amb)^0.33
    t_ext_k = t_amb_k + 15.0  # Initial guess
    flux = 0.0

    for _ in range(50):
        delta_t_ext = max(0.5, t_ext_k - t_amb_k)
        h_conv = 1.5 * (delta_t_ext ** 0.33)
        h_conv = max(4.0, min(25.0, h_conv))

        # Radiation from exterior surface
        h_rad = ext_emissivity * SIGMA * (t_ext_k + t_amb_k) * (t_ext_k**2 + t_amb_k**2)
        h_ext_total = h_conv + h_rad
        r_ext = 1.0 / h_ext_total

        # Total thermal resistance
        r_total = r_inner + r_cond + r_ext
        flux = (t_in_k - t_amb_k) / r_total

        # Update T_ext
        t_ext_new = t_amb_k + flux * r_ext
        if abs(t_ext_new - t_ext_k) < 1e-4:
            t_ext_k = t_ext_new
            break
        t_ext_k = 0.5 * (t_ext_k + t_ext_new)

    t_ext_c = t_ext_k - 273.15

    # Compute interface temperatures
    # T_surf_inner
    t_curr_k = t_in_k - (flux * r_inner)
    layer_temps = [{"interface": "Inner Gas-to-Wall", "temp_c": round(t_curr_k - 273.15, 1)}]

    for i, ld in enumerate(layer_details):
        t_curr_k -= flux * ld["r_value"]
        layer_temps.append({
            "interface": f"After {ld['name']}",
            "temp_c": round(t_curr_k - 273.15, 1)
        })

    return {
        "heat_flux_w_m2": round(flux, 2),
        "total_wall_thickness_mm": total_thickness_mm,
        "total_r_thermal_m2_k_w": round(r_total, 4),
        "t_exterior_surface_c": round(t_ext_c, 1),
        "exterior_touch_safe": t_ext_c <= 60.0,
        "exterior_h_total_w_m2k": round(h_ext_total, 2),
        "temperature_gradient": layer_temps,
        "layers": layer_details
    }


def compute_preheat_dynamics(burner_power_kw: float,
                             dome_area_m2: float,
                             floor_area_m2: float,
                             stone_thickness_mm: float,
                             insulation_thickness_mm: float,
                             insulation_type: str = "ceramic_fiber",
                             t_target_c: float = 450.0,
                             t_ambient_c: float = 20.0,
                             flue_draft_efficiency: float = 0.40):
    """
    Estimate preheat time to reach target floor and dome temperature.

    Thermal Mass includes:
    1. Cordierite floor stone: Area * thickness * rho * cp
    2. Stainless inner dome (1.5mm): Area * 0.0015 * rho * cp
    3. Effective participating insulation mass (~30% of insulation layer heats up to mean gradient)
    """
    stone_mat = MATERIAL_PROPERTIES["cordierite"]
    ss_mat = MATERIAL_PROPERTIES["ss304"]
    ins_mat = MATERIAL_PROPERTIES.get(insulation_type, MATERIAL_PROPERTIES["ceramic_fiber"])

    # 1. Cordierite stone thermal mass
    stone_vol = floor_area_m2 * (stone_thickness_mm / 1000.0)
    stone_mass_kg = stone_vol * stone_mat["density"]
    c_stone = stone_mass_kg * stone_mat["cp"]

    # 2. Stainless inner liner (1.5mm dome + floor tray)
    ss_inner_area = dome_area_m2 + floor_area_m2
    ss_mass_kg = ss_inner_area * 0.0015 * ss_mat["density"]
    c_ss = ss_mass_kg * ss_mat["cp"]

    # 3. Insulation participating thermal mass (approx 35% effective heat penetration)
    ins_vol = dome_area_m2 * (insulation_thickness_mm / 1000.0)
    ins_mass_kg = ins_vol * ins_mat["density"]
    c_ins = 0.35 * (ins_mass_kg * ins_mat["cp"])

    total_thermal_mass_j_k = c_stone + c_ss + c_ins

    # Net useful heat input rate
    # Open-mouth pizza ovens vent flue gases at 400-500°C; draft heat capture efficiency ~35-45%
    net_heat_kw = burner_power_kw * flue_draft_efficiency
    net_heat_w = net_heat_kw * 1000.0

    # Temperature rise required
    delta_t = t_target_c - t_ambient_c

    # Thermal energy required to heat the mass
    q_stored_mj = (total_thermal_mass_j_k * delta_t) / 1e6

    # Steady state heat loss during preheat (average at half-temperature)
    # Average flux ~ 350 W/m2
    avg_loss_w = (dome_area_m2 + floor_area_m2) * 350.0
    effective_net_w = max(500.0, net_heat_w - avg_loss_w)

    time_seconds = (total_thermal_mass_j_k * delta_t) / effective_net_w
    time_minutes = time_seconds / 60.0

    return {
        "burner_input_kw": burner_power_kw,
        "burner_input_btu_hr": round(burner_power_kw * 3412.142, 0),
        "draft_capture_efficiency_pct": flue_draft_efficiency * 100.0,
        "net_absorbed_power_kw": round(net_heat_kw, 2),
        "thermal_mass_breakdown": {
            "cordierite_stone_mass_kg": round(stone_mass_kg, 2),
            "stainless_liner_mass_kg": round(ss_mass_kg, 2),
            "insulation_mass_kg": round(ins_mass_kg, 2),
            "total_effective_heat_capacity_kj_k": round(total_thermal_mass_j_k / 1000.0, 2)
        },
        "total_stored_energy_mj": round(q_stored_mj, 2),
        "target_floor_temp_c": t_target_c,
        "estimated_preheat_time_min": round(time_minutes, 1)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Pizza Oven Multi-Layer Thermal & Insulation Modeling Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard 25mm ceramic fiber insulation at 500°C internal:
  python3 thermal_model.py -t 500 --insulation ceramic_fiber --ins-thick 25

  # Premium dual-layer insulation (25mm ceramic fiber + 15mm microporous):
  python3 thermal_model.py -t 500 --layers ss304:1.5 ceramic_fiber:25 microporous:15 mild_steel_painted:1.2

  # Calculate preheat time with 8kW burner:
  python3 thermal_model.py --preheat --burner-kw 8.0 --dome-area 0.45 --floor-area 0.16 --stone-thick 15
        """
    )
    parser.add_argument("-t", "--t-internal", type=float, default=500.0,
                        help="Internal oven chamber temperature in °C (default: 500.0)")
    parser.add_argument("--t-ambient", type=float, default=20.0,
                        help="Ambient air temperature in °C (default: 20.0)")
    parser.add_argument("--insulation", type=str, default="ceramic_fiber",
                        choices=["ceramic_fiber", "calcium_silicate", "microporous"],
                        help="Primary insulation material (default: ceramic_fiber)")
    parser.add_argument("--ins-thick", type=float, default=25.0,
                        help="Insulation thickness in mm (default: 25.0)")
    parser.add_argument("--layers", type=str, default=None,
                        help="Custom layer stack format: mat1:thick1,mat2:thick2,... (e.g. 'ss304:1.5,ceramic_fiber:35,mild_steel_painted:1.2')")
    parser.add_argument("--dome-area", type=float, default=0.48,
                        help="Exterior dome surface area in m² (default: 0.48 m²)")
    parser.add_argument("--floor-area", type=float, default=0.16,
                        help="Floor stone baking surface area in m² (default: 0.16 m² = 400x400mm)")
    parser.add_argument("--preheat", action="store_true",
                        help="Run dynamic preheat time simulation")
    parser.add_argument("--burner-kw", type=float, default=8.0,
                        help="Burner heat input in kW (default: 8.0 kW = 27.3 kBTU/hr)")
    parser.add_argument("--stone-thick", type=float, default=15.0,
                        help="Cordierite baking stone thickness in mm (default: 15.0)")
    parser.add_argument("--json", action="store_true",
                        help="Output results in JSON format")

    args = parser.parse_args()

    # Parse layers
    if args.layers:
        parsed_layers = []
        for item in args.layers.split(","):
            parts = item.strip().split(":")
            if len(parts) == 2:
                parsed_layers.append({"material": parts[0].strip(), "thickness_mm": float(parts[1].strip())})
    else:
        # Default 3-layer architecture:
        # Inner SS304 (1.5mm) + Insulation + Outer coated mild steel shell (1.2mm)
        parsed_layers = [
            {"material": "ss304", "thickness_mm": 1.5},
            {"material": args.insulation, "thickness_mm": args.ins_thick},
            {"material": "mild_steel_painted", "thickness_mm": 1.2}
        ]

    steady_state = solve_steady_state_wall(
        parsed_layers,
        t_inner_c=args.t_internal,
        t_ambient_c=args.t_ambient
    )

    # Calculate total heat loss rate
    total_area = args.dome_area + args.floor_area
    total_heat_loss_w = steady_state["heat_flux_w_m2"] * total_area
    steady_state["total_surface_area_m2"] = total_area
    steady_state["total_heat_loss_watts"] = round(total_heat_loss_w, 1)

    preheat_res = None
    if args.preheat:
        preheat_res = compute_preheat_dynamics(
            burner_power_kw=args.burner_kw,
            dome_area_m2=args.dome_area,
            floor_area_m2=args.floor_area,
            stone_thickness_mm=args.stone_thick,
            insulation_thickness_mm=args.ins_thick,
            insulation_type=args.insulation,
            t_target_c=args.t_internal,
            t_ambient_c=args.t_ambient
        )

    output_payload = {
        "steady_state_thermal_model": steady_state,
        "preheat_dynamics": preheat_res
    }

    if args.json:
        print(json.dumps(output_payload, indent=2))
        return

    # Formatted CLI report
    print("=" * 72)
    print(" PIZZA OVEN THERMAL MODEL & INSULATION SIZING")
    print("=" * 72)
    print(f" Internal Chamber Temp:     {args.t_internal:.1f}°C")
    print(f" Ambient Air Temp:          {args.t_ambient:.1f}°C")
    print(f" Total Wall Thickness:      {steady_state['total_wall_thickness_mm']:.1f} mm")
    print(f" Wall Thermal Resistance:   {steady_state['total_r_thermal_m2_k_w']:.4f} m²·K/W")
    print(f" Conductive Heat Flux:      {steady_state['heat_flux_w_m2']:.1f} W/m²")
    print(f" Total Heat Loss Rate:      {steady_state['total_heat_loss_watts']:.1f} W ({steady_state['total_heat_loss_watts']/1000.0:.2f} kW)")
    print("-" * 72)
    print(" TEMPERATURE GRADIENT THROUGH WALL LAYERS:")
    for tg in steady_state["temperature_gradient"]:
        print(f"   * {tg['interface']:<36}: {tg['temp_c']:6.1f}°C")
    print("-" * 72)
    t_ext = steady_state["t_exterior_surface_c"]
    status_str = "[PASS] TOUCH-SAFE (<60°C ISO 13732-1)" if steady_state["exterior_touch_safe"] else "[FAIL] DANGER: EXCEEDS 60°C TOUCH LIMIT!"
    print(f" EXTERIOR TOUCH TEMPERATURE: {t_ext:.1f}°C  ==> {status_str}")
    if not steady_state["exterior_touch_safe"]:
        print("   >> RECOMMENDATION: Increase insulation thickness to >= 35mm or use dual-layer microporous board.")
    print("=" * 72)

    if preheat_res:
        print(" PREHEAT DYNAMICS SIMULATION:")
        print(f"   Burner Power:              {preheat_res['burner_input_kw']} kW ({preheat_res['burner_input_btu_hr']:,} BTU/hr)")
        print(f"   Draft Thermal Capture Eff: {preheat_res['draft_capture_efficiency_pct']:.1f}%")
        print(f"   Effective Power Ingress:   {preheat_res['net_absorbed_power_kw']} kW")
        print(f"   Baking Stone Mass:         {preheat_res['thermal_mass_breakdown']['cordierite_stone_mass_kg']} kg ({args.stone_thick}mm cordierite)")
        print(f"   Stainless Dome Liner Mass: {preheat_res['thermal_mass_breakdown']['stainless_liner_mass_kg']} kg")
        print(f"   Total Stored Energy to Target: {preheat_res['total_stored_energy_mj']} MJ")
        print(f"   >>> TIME TO REACH {args.t_internal:.0f}°C: {preheat_res['estimated_preheat_time_min']} MINUTES <<<")
        print("=" * 72)


if __name__ == "__main__":
    main()
