# Engineering Specifications: Open-Source High-Performance Pizza Oven

**Document Revision**: 1.0.0  
**Classification**: Mechanical Engineering & DFM Specification  
**Standard Compliance**: ISO 2768-mK, ISO 273, ISO 13732-1, FDA 21 CFR 175.300, EU 1935/2004, NSF/ANSI 51  

---

## 1. System Overview & Physical Dimensions

The system is a high-temperature ($500^\circ\text{C}$ / $932^\circ\text{F}$) portable outdoor Neapolitan pizza oven designed for sheet metal laser cutting, CNC press brake bending, and bolt-together modular assembly.

| Subsystem / Dimension | Specification | Engineering Rationale |
|---|---|---|
| **Cooking Chamber Footprint** | $405 \times 405 \text{ mm}$ interior clear | Accommodates standard $350 \text{ mm}$ to $400 \text{ mm}$ (14"–16") pizza peels and round/square baking stones. |
| **Dome Apex Height ($H_{\text{dome}}$)** | $250.0 \text{ mm}$ above hearth | Optimal catenary parabolic curve for radiant view factor ($F \ge 0.80$). |
| **Chamber Mouth Opening Height ($h_{\text{mouth}}$)** | $158.0 \text{ mm}$ | Implements classic $63.2\%$ mouth-to-dome draft ratio ($\frac{158}{250} = 0.632$). |
| **Chamber Mouth Width ($w_{\text{mouth}}$)** | $420.0 \text{ mm}$ | Sufficient clearance for turning peel insertion with pizza centered. |
| **Flue / Chimney Exhaust Diameter** | $\varnothing 101.6 \text{ mm}$ (4.0" OD) | Low-restriction natural convective draft for exhaust combustion stream. |
| **Total Assembly Mass** | $\sim 24.5 \text{ kg}$ | Portable backyard unit; heavy enough for stable thermal inertia. |

---

## 2. Bill of Materials & Subsystem Breakdown

```
+---------------------------------------------------------------------------------------+
|                                    OUTER CHASSIS                                      |
|  1.2mm Mild Steel (Powder Coated) or 1.2mm SS304 #4 Brushed Finish                   |
|  +---------------------------------------------------------------------------------+  |
|  |                             AIR CONVECTION BREAK                                |  |
|  |  8mm - 10mm Standoff Air Shield                                                 |  |
|  |  +---------------------------------------------------------------------------+  |  |
|  |  |                         THERMAL INSULATION                                |  |  |
|  |  |  25mm - 35mm Ceramic Fiber Blanket / Calcium Silicate Board               |  |  |
|  |  |  +---------------------------------------------------------------------+  |  |  |
|  |  |  |                         HOT INNER DOME LINER                       |  |  |  |
|  |  |  |  1.5mm AISI 304 Stainless Steel (Food Contact Certified)           |  |  |  |
|  |  |  |                                                                     |  |  |  |
|  |  |  |  [ FLAME ROLL ENVELOPE ]                                            |  |  |  |
|  |  |  |                                                                     |  |  |  |
|  |  |  |  ================== CORDIERITE HEARTH STONE ======================  |  |  |  |
|  |  |  |  15mm Thick Ceramic (Floating Mount with 4mm Thermal Gap)           |  |  |  |
|  |  |  +---------------------------------------------------------------------+  |  |  |
|  |  +---------------------------------------------------------------------------+  |  |
|  +---------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------+
```

### 2.1 Material Selection Schedule

| Part Name | Material Grade | Gauge / Thickness | Surface Finish | Food Contact? |
|---|---|---|---|---|
| **Inner Dome Ceiling** | AISI 304 Stainless Steel (EN 1.4301) | $1.5 \text{ mm}$ (16 ga) | 2B / Mill Finish (Passivated) | **YES** (Direct hot gas/radiation) |
| **Flame Diffuser / Baffle** | AISI 310S or 304 Stainless Steel | $2.0 \text{ mm}$ (14 ga) | 2B / Mill Finish | **YES** |
| **Hearth Stone Tray** | AISI 304 Stainless Steel | $1.5 \text{ mm}$ (16 ga) | 2B Finish | **YES** |
| **Baking Hearth Floor** | Cordierite Ceramic Stone | $15.0 \text{ mm}$ | Fine Vitrified Matte | **YES** (Direct food contact) |
| **Sub-Floor Board** | Calcium Silicate (Skamol 240) | $25.0 \text{ mm}$ | Raw Board | NO (Sealed under tray) |
| **Dome Insulation** | Ceramic Fiber Blanket ($128\text{ kg/m}^3$) | $30.0 \text{ mm}$ | Needle punched mat | NO (Enclosed inside cavity) |
| **Outer Top Shell** | Carbon Steel (S235JR) / SS304 | $1.2 \text{ mm}$ (18 ga) | High-Temp Polyester Powder Coat | NO (Exterior touch surface) |
| **Base Chassis / Legs** | Carbon Steel (S235JR) | $2.0 \text{ mm}$ (14 ga) | Outdoor Textured Powder Coat | NO (Cold zone) |
| **Fasteners (Hot Zone)** | A2-70 Stainless Steel (DIN 912 / 933) | M5, M6 | Uncoated + Nickel Anti-Seize | NO |

---

## 3. Sheet Metal Design for Manufacturing (DFM) Guidelines

### 3.1 Laser Cutting Specifications
* **Laser Assist Gas**: High-pressure Nitrogen ($N_2 \ge 16 \text{ bar}$) for all stainless steel components to prevent oxide formation and edge discoloration. Clean cut edges require no secondary deburring.
* **Minimum Laser Piercing Hole Diameter**:
  $$d_{\text{hole, min}} \ge 1.0 \times T \quad (\text{e.g., } \varnothing 1.5\text{ mm in } 1.5\text{ mm SS304})$$
* **Minimum Slot Width**: $w_{\text{slot}} \ge 1.0 \times T$.
* **Laser Kerf Compensation**: Nominal kerf allowance $0.18 \text{ mm}$ programmed in CAM post-processor.
* **Corner Reliefs**:
  * All right-angle flange intersections must incorporate circular or rectangular corner reliefs.
  * Rectangular relief depth: $D_{\text{relief}} \ge R + T = 3.5 \text{ mm}$.
  * Corner relief diameter: $D_{\text{circular}} \ge 2.0 \times T = 3.0 \text{ mm}$.

### 3.2 Press Brake Bending Rules
* **Tooling Standard**:
  * Punch radius: $R_{\text{punch}} = 1.5 \text{ mm}$ to $2.0 \text{ mm}$.
  * V-Die opening: $V = 8 \times T = 12.0 \text{ mm}$ (for $1.5 \text{ mm}$ sheet) and $V = 16.0 \text{ mm}$ (for $2.0 \text{ mm}$ sheet).
* **Bending Calculation Presets (Air Bending)**:
  * Stainless Steel 304 ($T = 1.5 \text{ mm}$, $R = 1.5 \text{ mm}$, $A = 90^\circ$):
    * K-factor: $K = 0.380$
    * Bend Allowance: $BA = 3.251 \text{ mm}$
    * Outside Setback: $OSSB = 3.000 \text{ mm}$
    * Bend Deduction: $BD = 2.749 \text{ mm}$
  * Stainless Steel 304 ($T = 2.0 \text{ mm}$, $R = 2.0 \text{ mm}$, $A = 90^\circ$):
    * K-factor: $K = 0.380$
    * Bend Allowance: $BA = 4.335 \text{ mm}$
    * Outside Setback: $OSSB = 4.000 \text{ mm}$
    * Bend Deduction: $BD = 3.665 \text{ mm}$
* **Minimum Flange Length ($b_{\text{min}}$)**:
  $$b_{\text{min}} = 4.0 \times T + R = 4(1.5) + 1.5 = \mathbf{7.5 \text{ mm}}$$
  *(All flanges in design are specified at $\ge 12.0 \text{ mm}$ to ensure full support across V-die shoulders).*
* **Minimum Hole-to-Bend Tangent Distance**:
  $$d_{\text{min}} = 2.5 \times T + R = 2.5(1.5) + 1.5 = \mathbf{5.25 \text{ mm}}$$

---

## 4. High-Temperature Fastener & Joint Engineering

### 4.1 Thermal Expansion Calculation ($20^\circ\text{C} \to 500^\circ\text{C}$, $\Delta T = 480 \text{ K}$)
Linear expansion formula:
$$\Delta L = L_0 \cdot \alpha \cdot \Delta T$$

1. **Inner SS304 Liner Tray ($L_0 = 405 \text{ mm}$)**:
   $$\Delta L_{\text{SS304}} = 405 \cdot (18.0 \times 10^{-6}) \cdot 480 = \mathbf{+3.499 \text{ mm}}$$
2. **Cordierite Hearth Stone ($L_0 = 400 \text{ mm}$)**:
   $$\Delta L_{\text{stone}} = 400 \cdot (2.8 \times 10^{-6}) \cdot 480 = \mathbf{+0.538 \text{ mm}}$$
3. **Outer Mild Steel Chassis ($L_0 = 420 \text{ mm}$, Operating at $60^\circ\text{C}$, $\Delta T = 40 \text{ K}$)**:
   $$\Delta L_{\text{outer}} = 420 \cdot (13.0 \times 10^{-6}) \cdot 40 = \mathbf{+0.218 \text{ mm}}$$

### 4.2 Joint Design Rules
* **Cordierite Stone Capture**:
  * Relative displacement between SS304 tray and Cordierite stone:
    $$\Delta_{\text{diff}} = 3.499 - 0.538 = 2.961 \text{ mm}$$
  * A perimeter clearance of **$\mathbf{4.0 \text{ mm}}$ on all four sides** is mandated.
  * The stone must rest freely without mechanical clamping. Corner retainers must have a $4.5 \text{ mm}$ slip slot.
* **Inner Dome to Outer Frame Tie Points**:
  * The hot inner dome must slide relative to the outer chassis.
  * All mounting holes on the outer frame are **slotted obrounds ($6.5 \times 12.0 \text{ mm}$)** oriented parallel to the expansion axis.
  * Fasteners must utilize **DIN 2093 Belleville Disc Springs** torqued to allow slip under thermal force while preventing loose vibrations.
  * Thread galling prevention: All stainless threads must be coated with high-purity nickel anti-seize paste rated to $1000^\circ\text{C}$.

---

## 5. Tolerances & Fits

* **General Sheet Metal Fabrications**: Compliant with **ISO 2768-mK**.
  * Linear features $120 \text{ mm} - 400 \text{ mm}$: $\pm 0.5 \text{ mm}$.
  * Angular features: $\pm 0^\circ 30'$.
* **Bolt Clearance Holes (ISO 273 Coarse Series)**:
  * M5 Fasteners: $\varnothing 5.8 \text{ mm}$ (providing $\pm 0.4 \text{ mm}$ initial float).
  * M6 Fasteners: $\varnothing 7.0 \text{ mm}$.
  * Thermal slip slots: $7.0 \times 12.0 \text{ mm}$ obround.

---

## 6. Food Contact Safety & Regulatory Compliance

* **FDA Compliance**: Complies with **FDA 21 CFR 175.300** and FDA CPG 7117.06/07 for ceramic food contact.
* **EU Compliance**: Complies with **EC Regulation No 1935/2004** and **2023/2006** (GMP).
* **Strict Material Prohibition**:
  * **Zero Galvanized / Zinc-Plated Materials**: Galvanized steel is strictly banned from the oven cooking chamber, burner tunnel, and exhaust stack. Zinc boils/fumes above $200^\circ\text{C}-419^\circ\text{C}$, releasing poisonous zinc oxide ($\text{ZnO}$) that causes metal fume fever.
  * **Zero Lead, Cadmium, or Toxic Glazes**: Hearth stone must be unglazed, certified pure cordierite refractory stone.
  * **Zero PTFE/PFA Non-Stick Coatings**: Cooking chamber surfaces must be bare passivated austenitic stainless steel.
