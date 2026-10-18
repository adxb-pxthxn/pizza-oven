#!/usr/bin/env python3
"""
model_generator.py - Parametric CAD Model Generator for Neapolitan Pizza Oven

Generates parametric 2D sheet metal flat patterns (DXF, SVG), 3D interchange meshes (OBJ, STL),
OpenSCAD source scripts, and engineering specifications for 12" and 16" high-performance
portable Neapolitan pizza ovens.

Zero external dependencies required - runs on pure Python 3 standard library.
Compatible with build123d, CadQuery, OpenSCAD, FreeCAD, and CNC laser nesting software.
"""

import sys
import os
import math
import json
import argparse
from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path


# ==============================================================================
# PARAMETRIC CONFIGURATION & MASTER VARIABLES
# ==============================================================================

@dataclass
class OvenParameters:
    """Master parametric dimensions and DFM rules for the pizza oven."""
    # Identification
    name: str = "Neapolitan-Portable-Oven"
    stone_size_nominal_in: int = 12  # 12 or 16

    # Baking Stone Dimensions
    stone_width: float = 330.0       # mm
    stone_depth: float = 330.0       # mm
    stone_thickness: float = 15.0    # mm

    # Inner Hot Chamber (Firebox) - AISI 304 Stainless Steel
    inner_sheet_thickness: float = 1.5   # mm
    chamber_clearance_lateral: float = 20.0  # mm total side clearance
    chamber_rear_burn_zone: float = 110.0   # mm rear combustion intake / flame roller zone
    dome_apex_height: float = 190.0      # mm above stone surface
    mouth_apex_ratio: float = 0.63       # Neapolitan 63% rule
    mouth_width_ratio: float = 0.88      # ratio of chamber width

    # Thermal Barrier & Insulation
    insulation_blanket_thickness: float = 25.0  # mm ceramic fiber blanket
    insulation_clearance_allowance: float = 2.0  # mm blanket expansion / compression relief

    # Outer Shroud Shell - AISI 304 or Powder-Coated Galvannealed
    outer_sheet_thickness: float = 1.2   # mm
    outer_bottom_air_gap: float = 12.0   # mm air gap under base floor

    # Exhaust Flue & Chimney Collar
    flue_diameter: float = 100.0         # mm (100mm for 12", 125mm for 16")
    chimney_collar_height: float = 65.0  # mm

    # Support Legs
    leg_sheet_thickness: float = 2.0     # mm stainless steel
    leg_height: float = 135.0            # mm ground clearance
    leg_deploy_angle_deg: float = 40.0   # splay angle for stability

    # Laser Cutting & DFM Tolerances
    laser_kerf: float = 0.18             # mm
    tab_width: float = 16.0              # mm
    tab_height_ratio: float = 1.0        # tab protrusion = sheet_thickness * ratio
    tab_slot_clearance: float = 0.25     # mm clearance per side
    min_web_thickness: float = 4.0       # mm
    thermal_relief_slot_length: float = 7.0  # mm (exceeds ΔL = α * L * ΔT)

    # Operating Environment
    max_operating_temp_c: float = 500.0
    ambient_temp_c: float = 20.0
    thermal_expansion_coeff: float = 18.0e-6  # 1/K for AISI 304

    # Derived Dimensions (populated by calculate_derived())
    chamber_width: float = field(init=False)
    chamber_depth: float = field(init=False)
    mouth_height: float = field(init=False)
    mouth_width: float = field(init=False)
    cavity_total: float = field(init=False)
    outer_width: float = field(init=False)
    outer_depth: float = field(init=False)
    outer_height: float = field(init=False)
    thermal_expansion_delta_l: float = field(init=False)

    def __post_init__(self):
        self.calculate_derived()

    def calculate_derived(self):
        """Compute all derived parametric dimensions using physical & DFM formulas."""
        self.chamber_width = self.stone_width + self.chamber_clearance_lateral
        self.chamber_depth = self.stone_depth + self.chamber_rear_burn_zone
        self.mouth_height = self.dome_apex_height * self.mouth_apex_ratio
        self.mouth_width = self.chamber_width * self.mouth_width_ratio

        self.cavity_total = self.insulation_blanket_thickness + self.insulation_clearance_allowance
        self.outer_width = self.chamber_width + 2.0 * (self.cavity_total + self.inner_sheet_thickness)
        self.outer_depth = self.chamber_depth + self.cavity_total + 15.0
        self.outer_height = self.dome_apex_height + self.stone_thickness + self.cavity_total + self.outer_bottom_air_gap

        # Thermal expansion calculation: ΔL = α * L * ΔT
        delta_t = max(0.0, self.max_operating_temp_c - self.ambient_temp_c)
        self.thermal_expansion_delta_l = self.thermal_expansion_coeff * self.chamber_depth * delta_t


def get_default_oven_parameters(stone_size_in: int = 12) -> OvenParameters:
    """Return standard parameter sets for 12-inch or 16-inch pizza ovens."""
    if stone_size_in == 16:
        return OvenParameters(
            name="Neapolitan-Portable-Oven-16",
            stone_size_nominal_in=16,
            stone_width=406.0,
            stone_depth=406.0,
            stone_thickness=15.0,
            inner_sheet_thickness=1.5,
            chamber_clearance_lateral=24.0,
            chamber_rear_burn_zone=125.0,
            dome_apex_height=210.0,
            mouth_apex_ratio=0.63,
            mouth_width_ratio=0.88,
            insulation_blanket_thickness=25.0,
            insulation_clearance_allowance=2.0,
            outer_sheet_thickness=1.2,
            flue_diameter=125.0,
            chimney_collar_height=75.0,
            leg_height=145.0,
            leg_sheet_thickness=2.0,
            thermal_relief_slot_length=8.5,
        )
    else:
        return OvenParameters(
            name="Neapolitan-Portable-Oven-12",
            stone_size_nominal_in=12,
            stone_width=330.0,
            stone_depth=330.0,
            stone_thickness=15.0,
            inner_sheet_thickness=1.5,
            chamber_clearance_lateral=20.0,
            chamber_rear_burn_zone=110.0,
            dome_apex_height=190.0,
            mouth_apex_ratio=0.63,
            mouth_width_ratio=0.88,
            insulation_blanket_thickness=25.0,
            insulation_clearance_allowance=2.0,
            outer_sheet_thickness=1.2,
            flue_diameter=100.0,
            chimney_collar_height=65.0,
            leg_height=135.0,
            leg_sheet_thickness=2.0,
            thermal_relief_slot_length=7.0,
        )


# ==============================================================================
# PURE PYTHON DXF GENERATOR (AUTOCAD R12 COMPLIANT)
# ==============================================================================

class DXFWriter:
    """Minimal, self-contained AutoCAD DXF R12 generator with full layer support."""

    def __init__(self):
        self.layers: Dict[str, int] = {
            "CUT": 7,            # White / Laser perimeter cut
            "CUT_INTERIOR": 4,   # Cyan / Internal holes & slots
            "BEND_UP": 3,        # Green / 90 deg bend up
            "BEND_DOWN": 2,      # Yellow / 90 deg bend down
            "ETCH": 1,           # Red / Laser marking & part numbers
        }
        self.entities: List[str] = []

    def add_layer(self, name: str, color: int):
        self.layers[name] = color

    def add_line(self, x1: float, y1: float, x2: float, y2: float, layer: str = "CUT"):
        self.entities.extend([
            "0", "LINE",
            "8", layer,
            "10", f"{x1:.4f}",
            "20", f"{y1:.4f}",
            "30", "0.0",
            "11", f"{x2:.4f}",
            "21", f"{y2:.4f}",
            "31", "0.0"
        ])

    def add_circle(self, cx: float, cy: float, radius: float, layer: str = "CUT_INTERIOR"):
        self.entities.extend([
            "0", "CIRCLE",
            "8", layer,
            "10", f"{cx:.4f}",
            "20", f"{cy:.4f}",
            "30", "0.0",
            "40", f"{radius:.4f}"
        ])

    def add_arc(self, cx: float, cy: float, radius: float, start_deg: float, end_deg: float, layer: str = "CUT"):
        self.entities.extend([
            "0", "ARC",
            "8", layer,
            "10", f"{cx:.4f}",
            "20", f"{cy:.4f}",
            "30", "0.0",
            "40", f"{radius:.4f}",
            "50", f"{start_deg:.4f}",
            "51", f"{end_deg:.4f}"
        ])

    def add_rect(self, x: float, y: float, width: float, height: float, layer: str = "CUT"):
        self.add_line(x, y, x + width, y, layer)
        self.add_line(x + width, y, x + width, y + height, layer)
        self.add_line(x + width, y + height, x, y + height, layer)
        self.add_line(x, y + height, x, y, layer)

    def add_slotted_hole(self, cx: float, cy: float, length: float, width: float, layer: str = "CUT_INTERIOR"):
        """Draw a thermal expansion slot with rounded ends."""
        r = width / 2.0
        dx = (length - width) / 2.0
        if dx <= 0:
            self.add_circle(cx, cy, r, layer)
            return

        x_left = cx - dx
        x_right = cx + dx
        # Top and bottom straight lines
        self.add_line(x_left, cy + r, x_right, cy + r, layer)
        self.add_line(x_right, cy - r, x_left, cy - r, layer)
        # End caps (semi-circles)
        self.add_arc(x_right, cy, r, 270.0, 90.0, layer)
        self.add_arc(x_left, cy, r, 90.0, 270.0, layer)

    def add_text(self, text: str, x: float, y: float, height: float = 5.0, layer: str = "ETCH"):
        self.entities.extend([
            "0", "TEXT",
            "8", layer,
            "10", f"{x:.4f}",
            "20", f"{y:.4f}",
            "30", "0.0",
            "40", f"{height:.4f}",
            "1", text
        ])

    def export(self) -> str:
        """Render complete DXF file contents."""
        out = [
            "0", "SECTION",
            "2", "HEADER",
            "9", "$ACADVER",
            "1", "AC1009",  # AutoCAD R12
            "0", "ENDSEC",
            "0", "SECTION",
            "2", "TABLES",
            "0", "TABLE",
            "2", "LAYER",
            "70", str(len(self.layers)),
        ]
        for name, col in self.layers.items():
            out.extend([
                "0", "LAYER",
                "2", name,
                "70", "0",
                "62", str(col),
                "6", "CONTINUOUS"
            ])
        out.extend([
            "0", "ENDTAB",
            "0", "ENDSEC",
            "0", "SECTION",
            "2", "ENTITIES"
        ])
        out.extend(self.entities)
        out.extend([
            "0", "ENDSEC",
            "0", "EOF"
        ])
        return "\n".join(out) + "\n"


# ==============================================================================
# PURE PYTHON SVG FLAT PATTERN GENERATOR
# ==============================================================================

class SVGWriter:
    """Scalable Vector Graphics (SVG) generator for CAD flat pattern drawings."""

    def __init__(self, width_mm: float, height_mm: float):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.paths: List[str] = []

    def add_line(self, x1: float, y1: float, x2: float, y2: float, stroke: str = "#00d2ff",
                 stroke_width: float = 0.5, dash: str = ""):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        # SVG y-coordinates are inverted from CAD coordinate space
        svg_y1 = self.height_mm - y1
        svg_y2 = self.height_mm - y2
        self.paths.append(
            f'<line x1="{x1:.3f}" y1="{svg_y1:.3f}" x2="{x2:.3f}" y2="{svg_y2:.3f}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr} />'
        )

    def add_rect(self, x: float, y: float, w: float, h: float, stroke: str = "#00d2ff",
                 fill: str = "none", stroke_width: float = 0.5):
        svg_y = self.height_mm - (y + h)
        self.paths.append(
            f'<rect x="{x:.3f}" y="{svg_y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'stroke="{stroke}" fill="{fill}" stroke-width="{stroke_width}" />'
        )

    def add_circle(self, cx: float, cy: float, r: float, stroke: str = "#00d2ff",
                   fill: str = "none", stroke_width: float = 0.5):
        svg_cy = self.height_mm - cy
        self.paths.append(
            f'<circle cx="{cx:.3f}" cy="{svg_cy:.3f}" r="{r:.3f}" '
            f'stroke="{stroke}" fill="{fill}" stroke-width="{stroke_width}" />'
        )

    def add_text(self, text: str, x: float, y: float, font_size: float = 4.0, fill: str = "#ff2a6d"):
        svg_y = self.height_mm - y
        self.paths.append(
            f'<text x="{x:.3f}" y="{svg_y:.3f}" font-family="monospace" '
            f'font-size="{font_size:.2f}px" fill="{fill}">{text}</text>'
        )

    def export(self) -> str:
        margin = 15.0
        v_width = self.width_mm + 2.0 * margin
        v_height = self.height_mm + 2.0 * margin
        header = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{v_width:.1f}mm" height="{v_height:.1f}mm" '
            f'viewBox="{-margin} {-margin} {v_width:.1f} {v_height:.1f}">',
            f'<rect x="{-margin}" y="{-margin}" width="{v_width:.1f}" height="{v_height:.1f}" fill="#12151c"/>',
            '<!-- CAD FLAT PATTERN EXPORT -->',
            '<g id="geometry">'
        ]
        footer = ['</g>', '</svg>']
        return "\n".join(header + self.paths + footer) + "\n"


# ==============================================================================
# PURE PYTHON 3D MESH GENERATOR (OBJ & STL)
# ==============================================================================

class Mesh3D:
    """Indexed 3D triangle mesh for CAD export (OBJ / Binary/ASCII STL)."""

    def __init__(self, name: str = "Assembly"):
        self.name = name
        self.vertices: List[Tuple[float, float, float]] = []
        self.faces: List[Tuple[int, int, int]] = []  # 1-indexed for OBJ

    def add_vertex(self, x: float, y: float, z: float) -> int:
        self.vertices.append((float(x), float(y), float(z)))
        return len(self.vertices)

    def add_triangle(self, v1: int, v2: int, v3: int):
        self.faces.append((v1, v2, v3))

    def add_quad(self, v1: int, v2: int, v3: int, v4: int):
        """Add two triangles forming a planar or near-planar quad."""
        self.add_triangle(v1, v2, v3)
        self.add_triangle(v1, v3, v4)

    def add_box(self, x: float, y: float, z: float, dx: float, dy: float, dz: float):
        """Add a 3D rectangular box solid."""
        # 8 vertices
        v1 = self.add_vertex(x, y, z)
        v2 = self.add_vertex(x + dx, y, z)
        v3 = self.add_vertex(x + dx, y + dy, z)
        v4 = self.add_vertex(x, y + dy, z)
        v5 = self.add_vertex(x, y, z + dz)
        v6 = self.add_vertex(x + dx, y, z + dz)
        v7 = self.add_vertex(x + dx, y + dy, z + dz)
        v8 = self.add_vertex(x, y + dy, z + dz)

        # 6 faces (outward normals)
        self.add_quad(v1, v4, v3, v2)  # Bottom (-Z)
        self.add_quad(v5, v6, v7, v8)  # Top (+Z)
        self.add_quad(v1, v2, v6, v5)  # Front (-Y)
        self.add_quad(v2, v3, v7, v6)  # Right (+X)
        self.add_quad(v3, v4, v8, v7)  # Back (+Y)
        self.add_quad(v4, v1, v5, v8)  # Left (-X)

    def add_extruded_arch(self, w: float, h_apex: float, depth: float, thickness: float,
                           segments: int = 24, z_offset: float = 0.0, y_offset: float = 0.0):
        """Generate a parabolic/catenary arch dome shell."""
        half_w = w / 2.0
        # Calculate arch profile points (outer and inner)
        outer_pts = []
        inner_pts = []
        for i in range(segments + 1):
            t = -1.0 + 2.0 * (i / segments)  # -1 to 1
            x = t * half_w
            # Parabolic arch: z = h * (1 - t^2)
            z_mid = h_apex * (1.0 - (t ** 2))
            outer_pts.append((x, z_mid + thickness / 2.0))
            inner_pts.append((x, max(0.0, z_mid - thickness / 2.0)))

        # Extrude along Y
        y_front = y_offset
        y_back = y_offset + depth

        ring_front_outer = [self.add_vertex(x, y_front, z + z_offset) for x, z in outer_pts]
        ring_back_outer = [self.add_vertex(x, y_back, z + z_offset) for x, z in outer_pts]
        ring_front_inner = [self.add_vertex(x, y_front, z + z_offset) for x, z in inner_pts]
        ring_back_inner = [self.add_vertex(x, y_back, z + z_offset) for x, z in inner_pts]

        for i in range(segments):
            # Outer surface
            self.add_quad(ring_front_outer[i], ring_back_outer[i],
                          ring_back_outer[i+1], ring_front_outer[i+1])
            # Inner surface
            self.add_quad(ring_front_inner[i+1], ring_back_inner[i+1],
                          ring_back_inner[i], ring_front_inner[i])
            # Front rim
            self.add_quad(ring_front_inner[i], ring_front_outer[i],
                          ring_front_outer[i+1], ring_front_inner[i+1])
            # Back rim
            self.add_quad(ring_back_inner[i+1], ring_back_outer[i+1],
                          ring_back_outer[i], ring_back_inner[i])

    def add_cylinder(self, cx: float, cy: float, z_bottom: float, radius: float,
                     height: float, segments: int = 24):
        """Add a vertical cylinder (e.g. flue chimney)."""
        bottom_pts = []
        top_pts = []
        for i in range(segments):
            theta = 2.0 * math.pi * (i / segments)
            x = cx + radius * math.cos(theta)
            y = cy + radius * math.sin(theta)
            bottom_pts.append(self.add_vertex(x, y, z_bottom))
            top_pts.append(self.add_vertex(x, y, z_bottom + height))

        c_bot = self.add_vertex(cx, cy, z_bottom)
        c_top = self.add_vertex(cx, cy, z_bottom + height)

        for i in range(segments):
            nxt = (i + 1) % segments
            # Side wall
            self.add_quad(bottom_pts[i], bottom_pts[nxt], top_pts[nxt], top_pts[i])
            # Top cap
            self.add_triangle(c_top, top_pts[nxt], top_pts[i])
            # Bottom cap
            self.add_triangle(c_bot, bottom_pts[i], bottom_pts[nxt])

    def export_obj(self) -> str:
        """Export Wavefront OBJ format."""
        out = [f"# Wavefront OBJ - {self.name}", f"o {self.name}"]
        for v in self.vertices:
            out.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
        for f in self.faces:
            out.append(f"f {f[0]} {f[1]} {f[2]}")
        return "\n".join(out) + "\n"

    def export_stl_ascii(self) -> str:
        """Export ASCII STL format."""
        out = [f"solid {self.name}"]
        for f in self.faces:
            v1 = self.vertices[f[0] - 1]
            v2 = self.vertices[f[1] - 1]
            v3 = self.vertices[f[2] - 1]
            # Normal calculation: (v2 - v1) x (v3 - v1)
            ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
            bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
            nx = ay * bz - az * by
            ny = az * bx - ax * bz
            nz = ax * by - ay * bx
            norm = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
            nx, ny, nz = nx/norm, ny/norm, nz/norm

            out.append(f"  facet normal {nx:.4e} {ny:.4e} {nz:.4e}")
            out.append("    outer loop")
            out.append(f"      vertex {v1[0]:.4f} {v1[1]:.4f} {v1[2]:.4f}")
            out.append(f"      vertex {v2[0]:.4f} {v2[1]:.4f} {v2[2]:.4f}")
            out.append(f"      vertex {v3[0]:.4f} {v3[1]:.4f} {v3[2]:.4f}")
            out.append("    endloop")
            out.append("  endfacet")
        out.append(f"endsolid {self.name}\n")
        return "\n".join(out)


# ==============================================================================
# PARAMETRIC MODEL GENERATOR LOGIC
# ==============================================================================

class PizzaOvenModelGenerator:
    """Orchestrates generation of all CAD deliverables."""

    def __init__(self, params: OvenParameters):
        self.p = params

    def generate_inner_dome_flat(self) -> Tuple[DXFWriter, SVGWriter]:
        """
        Unfolded flat pattern of the inner 304 stainless hot dome arch.
        Includes tab ears, bend reference lines, and thermal expansion relief slots.
        """
        # Arc length of parabolic arch: L_arc ≈ 2 * integral sqrt(1 + (dz/dx)^2) dx
        # For parabola z = h * (1 - 4x^2 / w^2), a very accurate approximation:
        w = self.p.chamber_width
        h = self.p.dome_apex_height
        # Ramanujan-style perimeter approximation for semi-ellipse / parabola
        arc_len = 0.5 * math.pi * math.sqrt(2 * ((w/2)**2 + h**2))
        depth = self.p.chamber_depth

        dxf = DXFWriter()
        svg = SVGWriter(arc_len + 40.0, depth + 40.0)

        # Main rectangular sheet blank
        x0, y0 = 10.0, 10.0
        dxf.add_rect(x0, y0, arc_len, depth, layer="CUT")
        svg.add_rect(x0, y0, arc_len, depth, stroke="#00d2ff")

        # Longitudinal bend / forming guide etches
        for i in range(1, 6):
            frac = i / 6.0
            x_etch = x0 + arc_len * frac
            dxf.add_line(x_etch, y0 + 15.0, x_etch, y0 + depth - 15.0, layer="BEND_UP")
            svg.add_line(x_etch, y0 + 15.0, x_etch, y0 + depth - 15.0, stroke="#ffb800", dash="4,4")

        # Thermal expansion slotted mounting holes along side flanges
        # Inner dome expands by ΔL axially, so slotted holes are longitudinal (parallel to Y axis)
        slot_len = self.p.thermal_relief_slot_length
        slot_w = 4.5  # M4 clear
        for y_pos in [y0 + 30.0, y0 + depth / 2.0, y0 + depth - 30.0]:
            # Left side slots
            dxf.add_slotted_hole(x0 + 8.0, y_pos, slot_len, slot_w, layer="CUT_INTERIOR")
            svg.add_circle(x0 + 8.0, y_pos, slot_w / 2.0, stroke="#00ffcc")
            # Right side slots
            dxf.add_slotted_hole(x0 + arc_len - 8.0, y_pos, slot_len, slot_w, layer="CUT_INTERIOR")
            svg.add_circle(x0 + arc_len - 8.0, y_pos, slot_w / 2.0, stroke="#00ffcc")

        # Flue exhaust chimney cutout on front top centerline
        cx_flue = x0 + arc_len / 2.0
        cy_flue = y0 + 55.0
        dxf.add_circle(cx_flue, cy_flue, self.p.flue_diameter / 2.0, layer="CUT_INTERIOR")
        svg.add_circle(cx_flue, cy_flue, self.p.flue_diameter / 2.0, stroke="#00ffcc")

        # Part identification etching
        label = f"P101-INNER-DOME-{self.p.stone_size_nominal_in}IN-304SS-{self.p.inner_sheet_thickness}MM"
        dxf.add_text(label, x0 + 15.0, y0 + depth - 12.0, height=4.0, layer="ETCH")
        svg.add_text(label, x0 + 15.0, y0 + depth - 12.0, font_size=4.0, fill="#ff2a6d")

        return dxf, svg

    def generate_base_floor_flat(self) -> Tuple[DXFWriter, SVGWriter]:
        """
        Inner floor and baking stone support base plate (AISI 304).
        Features side flanges, tab receivers, and rear burner bracket mounts.
        """
        w = self.p.chamber_width
        d = self.p.chamber_depth
        flange = 20.0

        # Unfolded width has left and right upward flanges: W + 2 * flange
        total_w = w + 2.0 * flange
        total_d = d + flange  # Rear upward flange

        dxf = DXFWriter()
        svg = SVGWriter(total_w + 20.0, total_d + 20.0)

        x0, y0 = 10.0, 10.0
        # Perimeter boundary cut
        dxf.add_rect(x0, y0, total_w, total_d, layer="CUT")
        svg.add_rect(x0, y0, total_w, total_d, stroke="#00d2ff")

        # Bend lines (Green dashed)
        # Left bend line
        dxf.add_line(x0 + flange, y0, x0 + flange, y0 + total_d, layer="BEND_UP")
        svg.add_line(x0 + flange, y0, x0 + flange, y0 + total_d, stroke="#ffb800", dash="5,5")
        # Right bend line
        dxf.add_line(x0 + total_w - flange, y0, x0 + total_w - flange, y0 + total_d, layer="BEND_UP")
        svg.add_line(x0 + total_w - flange, y0, x0 + total_w - flange, y0 + total_d, stroke="#ffb800", dash="5,5")
        # Rear bend line
        dxf.add_line(x0 + flange, y0 + total_d - flange, x0 + total_w - flange, y0 + total_d - flange, layer="BEND_UP")
        svg.add_line(x0 + flange, y0 + total_d - flange, x0 + total_w - flange, y0 + total_d - flange, stroke="#ffb800", dash="5,5")

        # Tab receiver slots for inner dome mating
        tab_w = self.p.tab_width + 2.0 * self.p.tab_slot_clearance
        tab_t = self.p.inner_sheet_thickness + 2.0 * self.p.tab_slot_clearance
        for y_slot in [y0 + 35.0, y0 + total_d / 2.0, y0 + total_d - 45.0]:
            # Left slot
            dxf.add_rect(x0 + flange - tab_t / 2.0, y_slot - tab_w / 2.0, tab_t, tab_w, layer="CUT_INTERIOR")
            svg.add_rect(x0 + flange - tab_t / 2.0, y_slot - tab_w / 2.0, tab_t, tab_w, stroke="#00ffcc")
            # Right slot
            dxf.add_rect(x0 + total_w - flange - tab_t / 2.0, y_slot - tab_w / 2.0, tab_t, tab_w, layer="CUT_INTERIOR")
            svg.add_rect(x0 + total_w - flange - tab_t / 2.0, y_slot - tab_w / 2.0, tab_t, tab_w, stroke="#00ffcc")

        # Stone positioning guide marks (etched)
        stone_x = x0 + flange + (w - self.p.stone_width) / 2.0
        stone_y = y0 + 10.0
        dxf.add_rect(stone_x, stone_y, self.p.stone_width, self.p.stone_depth, layer="ETCH")
        svg.add_rect(stone_x, stone_y, self.p.stone_width, self.p.stone_depth, stroke="#ff2a6d", stroke_width=0.3)

        label = f"P102-BASE-FLOOR-{self.p.stone_size_nominal_in}IN-304SS-{self.p.inner_sheet_thickness}MM"
        dxf.add_text(label, x0 + flange + 15.0, y0 + 20.0, height=4.0, layer="ETCH")
        svg.add_text(label, x0 + flange + 15.0, y0 + 20.0, font_size=4.0, fill="#ff2a6d")

        return dxf, svg

    def generate_outer_shroud_flat(self) -> Tuple[DXFWriter, SVGWriter]:
        """
        Unfolded flat pattern of the outer protective shroud (1.2mm powder-coated / brushed SS).
        Encloses 25mm ceramic blanket, stays safe-to-touch (<60°C).
        """
        w_outer = self.p.outer_width
        h_outer = self.p.outer_height
        arc_outer = 0.5 * math.pi * math.sqrt(2 * ((w_outer/2)**2 + h_outer**2))
        depth_outer = self.p.outer_depth

        dxf = DXFWriter()
        svg = SVGWriter(arc_outer + 40.0, depth_outer + 40.0)

        x0, y0 = 10.0, 10.0
        dxf.add_rect(x0, y0, arc_outer, depth_outer, layer="CUT")
        svg.add_rect(x0, y0, arc_outer, depth_outer, stroke="#00d2ff")

        # Flue collar penetration cutout
        cx = x0 + arc_outer / 2.0
        cy = y0 + 55.0
        dxf.add_circle(cx, cy, (self.p.flue_diameter / 2.0) + 1.0, layer="CUT_INTERIOR")
        svg.add_circle(cx, cy, (self.p.flue_diameter / 2.0) + 1.0, stroke="#00ffcc")

        # Flue collar mounting fastener holes (4x M4 at 90 deg)
        bolt_pcd = self.p.flue_diameter + 18.0
        for angle_deg in [0, 90, 180, 270]:
            rad = math.radians(angle_deg)
            bx = cx + (bolt_pcd / 2.0) * math.cos(rad)
            by = cy + (bolt_pcd / 2.0) * math.sin(rad)
            dxf.add_circle(bx, by, 2.2, layer="CUT_INTERIOR")  # 4.4mm dia
            svg.add_circle(bx, by, 2.2, stroke="#00ffcc")

        # Folding leg attachment pivot & detent holes along bottom skirts
        for x_leg in [x0 + 12.0, x0 + arc_outer - 12.0]:
            for y_leg in [y0 + 40.0, y0 + depth_outer - 50.0]:
                dxf.add_circle(x_leg, y_leg, 3.2, layer="CUT_INTERIOR")  # M6 pivot hole
                svg.add_circle(x_leg, y_leg, 3.2, stroke="#00ffcc")
                # Detent locking notch
                dxf.add_circle(x_leg + 10.0, y_leg, 2.2, layer="CUT_INTERIOR")
                svg.add_circle(x_leg + 10.0, y_leg, 2.2, stroke="#00ffcc")

        # Part label
        label = f"P103-OUTER-SHROUD-{self.p.stone_size_nominal_in}IN-{self.p.outer_sheet_thickness}MM"
        dxf.add_text(label, x0 + 20.0, y0 + depth_outer - 15.0, height=4.0, layer="ETCH")
        svg.add_text(label, x0 + 20.0, y0 + depth_outer - 15.0, font_size=4.0, fill="#ff2a6d")

        return dxf, svg

    def generate_folding_leg_flat(self) -> Tuple[DXFWriter, SVGWriter]:
        """
        Heavy-duty laser-cut folding support leg (2.0mm AISI 304).
        Features 40° splay stance, pivot hole, spring plunger locking detent,
        and high-temp silicone foot mounting hole.
        """
        leg_len = self.p.leg_height + 30.0
        leg_w = 40.0

        dxf = DXFWriter()
        svg = SVGWriter(leg_w + 30.0, leg_len + 30.0)

        x0, y0 = 10.0, 10.0
        # Tapered leg profile
        p1 = (x0, y0 + 15.0)
        p2 = (x0 + 5.0, y0 + leg_len)
        p3 = (x0 + leg_w - 5.0, y0 + leg_len)
        p4 = (x0 + leg_w, y0 + 15.0)
        p5 = (x0 + leg_w / 2.0, y0)

        dxf.add_line(p1[0], p1[1], p2[0], p2[1], layer="CUT")
        dxf.add_line(p2[0], p2[1], p3[0], p3[1], layer="CUT")
        dxf.add_line(p3[0], p3[1], p4[0], p4[1], layer="CUT")
        dxf.add_line(p4[0], p4[1], p5[0], p5[1], layer="CUT")
        dxf.add_line(p5[0], p5[1], p1[0], p1[1], layer="CUT")

        svg.add_line(p1[0], p1[1], p2[0], p2[1], stroke="#00d2ff")
        svg.add_line(p2[0], p2[1], p3[0], p3[1], stroke="#00d2ff")
        svg.add_line(p3[0], p3[1], p4[0], p4[1], stroke="#00d2ff")
        svg.add_line(p4[0], p4[1], p5[0], p5[1], stroke="#00d2ff")
        svg.add_line(p5[0], p5[1], p1[0], p1[1], stroke="#00d2ff")

        # Pivot hole (M6)
        dxf.add_circle(x0 + leg_w / 2.0, y0 + leg_len - 15.0, 3.2, layer="CUT_INTERIOR")
        svg.add_circle(x0 + leg_w / 2.0, y0 + leg_len - 15.0, 3.2, stroke="#00ffcc")

        # Splay lock detent slot (for positive 40 deg deployment)
        dxf.add_circle(x0 + leg_w / 2.0 - 8.0, y0 + leg_len - 22.0, 2.2, layer="CUT_INTERIOR")
        svg.add_circle(x0 + leg_w / 2.0 - 8.0, y0 + leg_len - 22.0, 2.2, stroke="#00ffcc")

        # Silicone foot mounting hole (M5)
        dxf.add_circle(x0 + leg_w / 2.0, y0 + 15.0, 2.7, layer="CUT_INTERIOR")
        svg.add_circle(x0 + leg_w / 2.0, y0 + 15.0, 2.7, stroke="#00ffcc")

        label = f"P104-LEG-304SS-{self.p.leg_sheet_thickness}MM"
        dxf.add_text(label, x0 + 2.0, y0 + 40.0, height=3.0, layer="ETCH")
        svg.add_text(label, x0 + 2.0, y0 + 40.0, font_size=3.0, fill="#ff2a6d")

        return dxf, svg

    def generate_3d_assembly_mesh(self) -> Mesh3D:
        """Construct full 3D multi-body polygonal assembly for 3D viewers and CAD interchange."""
        mesh = Mesh3D(f"PizzaOven_{self.p.stone_size_nominal_in}in")

        # 1. Cordierite Baking Stone
        stone_x = -self.p.stone_width / 2.0
        stone_y = 15.0
        stone_z = 0.0
        mesh.add_box(stone_x, stone_y, stone_z,
                     self.p.stone_width, self.p.stone_depth, self.p.stone_thickness)

        # 2. Inner Base Floor Plate
        base_x = -self.p.chamber_width / 2.0
        base_y = 0.0
        base_z = -self.p.inner_sheet_thickness
        mesh.add_box(base_x, base_y, base_z,
                     self.p.chamber_width, self.p.chamber_depth, self.p.inner_sheet_thickness)

        # 3. Inner Chamber Dome Arch (304 Stainless)
        mesh.add_extruded_arch(
            w=self.p.chamber_width,
            h_apex=self.p.dome_apex_height,
            depth=self.p.chamber_depth,
            thickness=self.p.inner_sheet_thickness,
            segments=24,
            z_offset=0.0,
            y_offset=0.0
        )

        # 4. Outer Shroud Shell (Enclosing Insulation Cavity)
        mesh.add_extruded_arch(
            w=self.p.outer_width,
            h_apex=self.p.outer_height,
            depth=self.p.outer_depth,
            thickness=self.p.outer_sheet_thickness,
            segments=24,
            z_offset=-self.p.outer_bottom_air_gap,
            y_offset=-10.0
        )

        # 5. Flue Chimney Collar
        flue_r = self.p.flue_diameter / 2.0
        flue_cy = 45.0
        flue_z = self.p.outer_height - self.p.outer_bottom_air_gap
        mesh.add_cylinder(
            cx=0.0, cy=flue_cy, z_bottom=flue_z,
            radius=flue_r, height=self.p.chimney_collar_height,
            segments=24
        )

        # 6. Folding Legs (4 corners)
        leg_w = 35.0
        leg_t = self.p.leg_sheet_thickness
        leg_h = self.p.leg_height
        half_ow = self.p.outer_width / 2.0
        for lx in [-half_ow - 2.0, half_ow - leg_t + 2.0]:
            for ly in [30.0, self.p.outer_depth - 40.0]:
                mesh.add_box(lx, ly, -self.p.outer_bottom_air_gap - leg_h,
                             leg_t, leg_w, leg_h)

        return mesh

    def generate_openscad_source(self) -> str:
        """Generate parametric OpenSCAD source code for live interactive 3D rendering."""
        return f"""// OpenSCAD Parametric Neapolitan Pizza Oven Model
// Generated automatically by cad/model_generator.py

$fn = 60;

// Master Parameters
stone_width = {self.p.stone_width};
stone_depth = {self.p.stone_depth};
stone_thickness = {self.p.stone_thickness};

chamber_width = {self.p.chamber_width};
chamber_depth = {self.p.chamber_depth};
dome_apex_height = {self.p.dome_apex_height};
inner_sheet_t = {self.p.inner_sheet_thickness};

mouth_height = {self.p.mouth_height};
mouth_width = {self.p.mouth_width};

insulation_cavity = {self.p.cavity_total};
outer_sheet_t = {self.p.outer_sheet_thickness};
outer_width = {self.p.outer_width};
outer_depth = {self.p.outer_depth};
outer_height = {self.p.outer_height};

flue_diameter = {self.p.flue_diameter};
chimney_collar_h = {self.p.chimney_collar_height};
leg_height = {self.p.leg_height};

module baking_stone() {{
    color([0.85, 0.75, 0.65])
    translate([-stone_width/2, 15, 0])
    cube([stone_width, stone_depth, stone_thickness]);
}}

module inner_dome() {{
    color([0.85, 0.88, 0.90])
    difference() {{
        // Outer arch
        translate([0, 0, 0])
        rotate([-90, 0, 0])
        linear_extrude(chamber_depth)
        scale([chamber_width/2, dome_apex_height])
        circle(r=1);

        // Hollow interior
        translate([0, -1, 0])
        rotate([-90, 0, 0])
        linear_extrude(chamber_depth + 2)
        scale([(chamber_width/2) - inner_sheet_t, dome_apex_height - inner_sheet_t])
        circle(r=1);

        // Flat bottom floor cut
        translate([-chamber_width, -1, -dome_apex_height])
        cube([2 * chamber_width, chamber_depth + 2, dome_apex_height]);

        // Front mouth opening (Neapolitan 63% rule)
        translate([-mouth_width/2, -1, 0])
        cube([mouth_width, 10, mouth_height]);

        // Flue chimney exhaust hole
        translate([0, 45, dome_apex_height - 20])
        cylinder(r=flue_diameter/2, h=50);
    }}
}}

module outer_shroud() {{
    color([0.2, 0.2, 0.22, 0.85])
    difference() {{
        translate([0, -10, -12])
        rotate([-90, 0, 0])
        linear_extrude(outer_depth)
        scale([outer_width/2, outer_height])
        circle(r=1);

        // Inner cavity
        translate([0, -12, -12])
        rotate([-90, 0, 0])
        linear_extrude(outer_depth + 4)
        scale([(outer_width/2) - outer_sheet_t, outer_height - outer_sheet_t])
        circle(r=1);

        // Bottom cut
        translate([-outer_width, -15, -outer_height - 12])
        cube([2 * outer_width, outer_depth + 10, outer_height]);

        // Front face opening
        translate([-mouth_width/2 - 10, -15, -12])
        cube([mouth_width + 20, 20, mouth_height + 25]);

        // Flue collar penetration
        translate([0, 45, outer_height - 30])
        cylinder(r=(flue_diameter/2) + 1, h=60);
    }}
}}

module chimney_collar() {{
    color([0.9, 0.9, 0.92])
    translate([0, 45, outer_height - 12])
    difference() {{
        cylinder(r=flue_diameter/2, h=chimney_collar_h);
        translate([0, 0, -1])
        cylinder(r=(flue_diameter/2) - 1.5, h=chimney_collar_h + 2);
    }}
}}

module folding_legs() {{
    color([0.7, 0.7, 0.72])
    for (lx = [-outer_width/2, outer_width/2 - 2]) {{
        for (ly = [30, outer_depth - 40]) {{
            translate([lx, ly, -12 - leg_height])
            cube([2.0, 35.0, leg_height]);
        }}
    }}
}}

// Full Assembly
baking_stone();
inner_dome();
outer_shroud();
chimney_collar();
folding_legs();
"""

    def export_all(self, output_dir: str) -> Dict[str, str]:
        """Generate all CAD formats and save to output directory. Returns manifest."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        manifest = {}

        # 1. Specification JSON
        spec_dict = asdict(self.p)
        spec_file = out_path / f"pizza_oven_{self.p.stone_size_nominal_in}in_spec.json"
        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(spec_dict, f, indent=2)
        manifest["spec_json"] = str(spec_file)

        # 2. 2D DXF & SVG Flat Patterns
        parts = {
            "inner_dome": self.generate_inner_dome_flat(),
            "base_floor": self.generate_base_floor_flat(),
            "outer_shroud": self.generate_outer_shroud_flat(),
            "folding_leg": self.generate_folding_leg_flat(),
        }

        for part_name, (dxf_obj, svg_obj) in parts.items():
            dxf_filename = out_path / f"{part_name}_{self.p.stone_size_nominal_in}in.dxf"
            svg_filename = out_path / f"{part_name}_{self.p.stone_size_nominal_in}in.svg"
            with open(dxf_filename, "w", encoding="utf-8") as f:
                f.write(dxf_obj.export())
            with open(svg_filename, "w", encoding="utf-8") as f:
                f.write(svg_obj.export())
            manifest[f"{part_name}_dxf"] = str(dxf_filename)
            manifest[f"{part_name}_svg"] = str(svg_filename)

        # 3. 3D Meshes (OBJ and STL)
        mesh = self.generate_3d_assembly_mesh()
        obj_file = out_path / f"pizza_oven_{self.p.stone_size_nominal_in}in_assembly.obj"
        stl_file = out_path / f"pizza_oven_{self.p.stone_size_nominal_in}in_assembly.stl"
        with open(obj_file, "w", encoding="utf-8") as f:
            f.write(mesh.export_obj())
        with open(stl_file, "w", encoding="utf-8") as f:
            f.write(mesh.export_stl_ascii())
        manifest["assembly_obj"] = str(obj_file)
        manifest["assembly_stl"] = str(stl_file)

        # 4. OpenSCAD Parametric Script
        scad_file = out_path / f"pizza_oven_{self.p.stone_size_nominal_in}in.scad"
        with open(scad_file, "w", encoding="utf-8") as f:
            f.write(self.generate_openscad_source())
        manifest["openscad"] = str(scad_file)

        return manifest


# ==============================================================================
# CLI ENTRYPOINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Parametric Code-CAD Generator for Neapolitan Pizza Oven"
    )
    parser.add_argument("--stone", type=int, choices=[12, 16], default=12,
                        help="Stone size variant in inches: 12 or 16 (default: 12)")
    parser.add_argument("--format", choices=["all", "dxf", "svg", "stl", "obj", "scad", "spec"],
                        default="all", help="Output format to generate (default: all)")
    parser.add_argument("--out-dir", type=str, default="cad/exports",
                        help="Output directory for generated assets (default: cad/exports)")
    args = parser.parse_args()

    params = get_default_oven_parameters(args.stone)
    generator = PizzaOvenModelGenerator(params)

    print(f"=== Generating Parametric CAD for {params.name} ===")
    print(f"Baking Stone: {params.stone_width} x {params.stone_depth} x {params.stone_thickness} mm")
    print(f"Inner Chamber: {params.chamber_width}W x {params.chamber_depth}D x {params.dome_apex_height}H mm")
    print(f"Mouth Ratio: {params.mouth_apex_ratio*100:.1f}% (Height: {params.mouth_height:.1f} mm)")
    print(f"Insulation Cavity: {params.cavity_total} mm")
    print(f"Thermal Expansion ΔL at {params.max_operating_temp_c}°C: {params.thermal_expansion_delta_l:.2f} mm")

    out_path = Path(args.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if args.format == "all":
        manifest = generator.export_all(args.out_dir)
        print(f"\nGenerated {len(manifest)} assets in {args.out_dir}/:")
        for k, v in manifest.items():
            print(f"  [+] {k:<20}: {v}")
    elif args.format == "dxf":
        for name, gen_fn in [
            ("inner_dome", generator.generate_inner_dome_flat),
            ("base_floor", generator.generate_base_floor_flat),
            ("outer_shroud", generator.generate_outer_shroud_flat),
            ("folding_leg", generator.generate_folding_leg_flat),
        ]:
            dxf, _ = gen_fn()
            fname = out_path / f"{name}_{args.stone}in.dxf"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(dxf.export())
            print(f"  [+] DXF written: {fname}")
    elif args.format == "svg":
        for name, gen_fn in [
            ("inner_dome", generator.generate_inner_dome_flat),
            ("base_floor", generator.generate_base_floor_flat),
            ("outer_shroud", generator.generate_outer_shroud_flat),
            ("folding_leg", generator.generate_folding_leg_flat),
        ]:
            _, svg = gen_fn()
            fname = out_path / f"{name}_{args.stone}in.svg"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(svg.export())
            print(f"  [+] SVG written: {fname}")
    elif args.format == "stl":
        mesh = generator.generate_3d_assembly_mesh()
        fname = out_path / f"pizza_oven_{args.stone}in_assembly.stl"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(mesh.export_stl_ascii())
        print(f"  [+] STL written: {fname}")
    elif args.format == "obj":
        mesh = generator.generate_3d_assembly_mesh()
        fname = out_path / f"pizza_oven_{args.stone}in_assembly.obj"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(mesh.export_obj())
        print(f"  [+] OBJ written: {fname}")
    elif args.format == "scad":
        scad_code = generator.generate_openscad_source()
        fname = out_path / f"pizza_oven_{args.stone}in.scad"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(scad_code)
        print(f"  [+] OpenSCAD written: {fname}")
    elif args.format == "spec":
        fname = out_path / f"pizza_oven_{args.stone}in_spec.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(asdict(params), f, indent=2)
        print(f"  [+] Spec JSON written: {fname}")


if __name__ == "__main__":
    main()
