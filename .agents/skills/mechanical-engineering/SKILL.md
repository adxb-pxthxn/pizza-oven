---
name: mechanical-engineering
description: Mechanical engineering and sheet metal DFM specialist skill. Covers precision laser cutting, CNC press brake forming, bend deduction / K-factor calculations, high-temperature fastener engineering with differential thermal expansion joints (SS304, mild steel, cordierite stone at 500°C), ISO 2768-mK tolerances, ISO 273 clearance fits, and FDA/EU 1935/2004 food contact safety standards.
license: Apache-2.0
compatibility: Universal
metadata:
  discipline: Mechanical Engineering & DFM
  version: 1.0.0
---

# Mechanical Engineering & Sheet Metal DFM Skill

This skill provides comprehensive engineering principles, formulas, rules of thumb, and fabrication guidelines for designing high-temperature food equipment, specifically outdoor pizza ovens and thermal cooking appliances.

---

## 1. Sheet Metal Design for Manufacturing (DFM)

### 1.1 Laser Cutting Guidelines
Fiber laser cutting is the primary blanking process for stainless steel (SS304/SS316) and structural carbon steel panels.

* **Minimum Feature & Hole Diameter**:
  * For Austenitic Stainless Steel (SS304): $d_{\text{min}} \ge 1.0 \times T$ (thickness). Cutting holes smaller than sheet thickness causes excessive thermal dross and taper.
  * For Mild Steel: $d_{\text{min}} \ge 0.8 \times T$ with oxygen assist, $1.0 \times T$ with nitrogen assist.
* **Kerf Width & Lead-Ins**:
  * Typical kerf width: $0.15 \text{ mm}$ to $0.25 \text{ mm}$ depending on nozzle diameter and assist gas (high-pressure $N_2$ assist is mandatory for stainless steel to eliminate oxidation/slag on cut edges).
  * Lead-in placement: Always place pierce points on waste skeleton, never on finished part edges or inside bend radius zones.
* **Slot & Notch Proportions**:
  * Minimum slot width: $w_{\text{min}} \ge 1.0 \times T$.
  * Minimum distance between adjacent laser cuts / holes: $s \ge 2.0 \times T$.
* **Corner Reliefs & Tear Prevention**:
  * Any bend adjacent to a flat flange must have corner relief cuts to prevent material tearing at stress concentrations:
    * **Rectangular Relief**: Width $\ge T$, Depth $\ge R + T$.
    * **Tear / Laser Slit Relief**: Fine slit extending $\ge R + T$ past tangent line.
    * **Circular / Obround Relief**: Diameter $D \ge 2 \times T$, centered on the bend axis intersection.

---

### 1.2 CNC Press Brake Forming & Bending Mechanics

Air bending is the industry standard for forming oven bodies, internal flame baffles, and structural brackets.

#### 1.2.1 Core Bending Parameters
* **Sheet Thickness ($T$)**: Thickness of sheet stock in mm.
* **Inside Bend Radius ($R$)**: Inside radius formed by punch tip and die shoulder. For air bending SS304, recommended minimum inside bend radius is $R = 1.0 \times T$ to prevent outer grain cracking.
* **Bend Angle ($A$)**: Angle through which sheet is bent (e.g., $90^\circ$ for right angle).
* **Neutral Axis & K-Factor ($K$)**: Ratio of neutral axis distance $t$ to sheet thickness $T$:
  $$K = \frac{t}{T}$$
  * Typical air bending K-factors:
    * Stainless Steel 304 / 316: $K = 0.38$
    * Carbon Mild Steel (S235 / Q235): $K = 0.42$
    * Aluminum 5052-H32: $K = 0.40$
    * Copper / Brass: $K = 0.44$

#### 1.2.2 Mathematical Formulas for Flat Pattern Blank Layout
1. **Bend Allowance ($BA$)**: Arc length along the neutral axis during bend:
   $$BA = \frac{\pi}{180} \cdot A \cdot (R + K \cdot T)$$
2. **Outside Setback ($OSSB$)**: Distance from outside apex corner to tangent point of bend:
   $$OSSB = \tan\left(\frac{A}{2}\right) \cdot (R + T)$$
3. **Bend Deduction ($BD$)**: Amount subtracted from outside flange dimensions to obtain flat blank length:
   $$BD = 2 \cdot OSSB - BA = 2 \cdot \tan\left(\frac{A}{2}\right) \cdot (R + T) - \frac{\pi}{180} \cdot A \cdot (R + K \cdot T)$$
4. **Flat Blank Sizing**: For an $N$-flange profile with outside dimensions $L_1, L_2, \dots, L_N$:
   $$L_{\text{flat}} = \sum_{i=1}^N L_i - \sum_{j=1}^{N-1} BD_j$$

#### 1.2.3 V-Die Sizing & Flange Limits
* **V-Die Width ($V$)**: Standard tooling rule for air bending:
  $$V = 8 \times T \quad (\text{for } T \le 3\text{ mm SS304})$$
* **Minimum Flange Length ($b_{\text{min}}$)**: Flange must span die opening shoulders without falling into the V-groove:
  $$b_{\text{min}} \approx \frac{V}{2} + \text{safety margin} \approx 4.0 \times T + R$$
* **Hole-to-Bend Distance ($d_{\text{min}}$)**: Holes placed too close to a bend will distort into an egg shape:
  $$d_{\text{min}} \ge 2.5 \times T + R$$
* **Hole-to-Edge Distance ($e_{\text{min}}$)**:
  $$e_{\text{min}} \ge 2.0 \times T$$

---

## 2. Fastener Engineering & Differential Thermal Expansion Joints

### 2.1 The Physics of Differential Thermal Expansion
In a $500^\circ\text{C}$ pizza oven, materials with dramatically differing Coefficients of Thermal Expansion (CTE, $\alpha$) operate in close mechanical proximity.

$$\Delta L = L_0 \cdot \alpha \cdot \Delta T$$

| Material | Application in Oven | CTE $\alpha$ ($10^{-6}/\text{K}$) | Modulus $E$ (GPa) | Exp. at $\Delta T=480\text{ K}$ ($L=400\text{ mm}$) |
|---|---|---|---|---|
| **AISI 304 Stainless** | Inner dome liner, flame ceiling, stone tray | $18.0 \times 10^{-6}$ | $193$ | **$+3.46 \text{ mm}$** |
| **Mild Carbon Steel** | Outer chassis skin, legs, exterior brackets | $13.0 \times 10^{-6}$ | $210$ | **$+2.50 \text{ mm}$** |
| **Cordierite Stone** | Floor baking hearth | **$2.8 \times 10^{-6}$** | $125$ | **$+0.54 \text{ mm}$** |
| **Refractory Firebrick**| High-mass hearth / rear backstop | $5.5 \times 10^{-6}$ | $80$ | **$+1.06 \text{ mm}$** |

### 2.2 Differential Expansion Hazards & Solutions

#### Hazard 1: Cordierite Hearth Stone Shattering
* **Issue**: A $400 \times 400 \text{ mm}$ cordierite ceramic baking stone expands by only $0.54\text{ mm}$, whereas the enclosing SS304 sheet metal tray expands by $3.46\text{ mm}$ (a differential shift of $\Delta_{\text{diff}} \approx 2.92\text{ mm}$).
* **Rule**: **NEVER mechanically bolt, clamp, or rigidly pinch cordierite ceramic hearth stones.**
* **Mitigation**:
  * Mount the stone on a floating perimeter shelf.
  * Provide minimum $4.0\text{ mm}$ clearance gap around all stone edges.
  * Rest the stone on high-density ceramic fiber paper ($2\text{ mm}$) or calcium silicate sub-floor to decouple thermal strain and prevent point-load stress concentrations.

#### Hazard 2: Bi-Metallic Warping & Oil-Canning
* **Issue**: Rigidly fastening a hot inner SS304 dome ($T=500^\circ\text{C}$) to a cooler outer chassis ($T=60^\circ\text{C}$) results in constrained thermal strain:
  $$\sigma_{\text{thermal}} = E \cdot \alpha \cdot \Delta T \approx 193 \times 10^3 \cdot 18.0 \times 10^{-6} \cdot 480 \approx 1,668 \text{ MPa}$$
  This far exceeds the hot yield strength of SS304 ($R_{p0.2} \approx 130\text{ MPa}$ at $500^\circ\text{C}$), causing immediate buckling, permanent distortion, and sheared rivet/bolt heads.
* **Mitigation**:
  * **Slotted Expansion Holes**: Slot length = Bolt nominal diameter + $\Delta L_{\text{expansion}} \times 1.5$.
  * **Belleville Disc Springs (DIN 2093 / DIN 6796)**: Maintain constant clamping preload through thermal expansion/contraction cycles without rattling or rigid lockup.
  * **Step Bushings / Shoulder Bolts**: Allow sheet metal plates to slide freely across each other while retaining out-of-plane alignment.

#### Hazard 3: Thread Galling & Seizing at $500^\circ\text{C}$
* **Issue**: Stainless steel bolts (A2-70 / A4-80) gall and cold-weld into stainless tapped holes or nuts, especially under thermal cycling.
* **Mitigation**:
  * Always apply high-temperature nickel-based or ceramic anti-seize paste rated to $1000^\circ\text{C}$ (e.g., Loctite 771).
  * Use prevailing-torque all-metal locknuts (DIN 980V) rather than nylon-insert nuts (nylon melts at $220^\circ\text{C}$).

---

## 3. Tolerances, Fits & Fastener Standards

### 3.1 General Tolerances: ISO 2768-mK
All un-dimensioned sheet metal features must comply with **ISO 2768-m** (medium linear/angular tolerances) and **ISO 2768-K** (geometrical tolerances).

#### Linear Dimension Tolerances (ISO 2768-m)
| Nominal Range (mm) | Tolerance ($\pm$ mm) |
|---|---|
| $0.5$ to $3$ | $\pm 0.1$ |
| Over $3$ to $6$ | $\pm 0.1$ |
| Over $6$ to $30$ | $\pm 0.2$ |
| Over $30$ to $120$ | $\pm 0.3$ |
| Over $120$ to $400$ | $\pm 0.5$ |
| Over $400$ to $1000$ | $\pm 0.8$ |
| Over $1000$ to $2000$ | $\pm 1.2$ |

#### Angular Tolerances (ISO 2768-m)
* Short leg length $< 10\text{ mm}$: $\pm 1^\circ$
* Leg length $10$ to $50\text{ mm}$: $\pm 0^\circ 30'$
* Leg length $50$ to $120\text{ mm}$: $\pm 0^\circ 20'$

### 3.2 Clearance Holes for Fasteners: ISO 273
For bolts passing through sheet metal brackets and chassis members:

| Fastener Thread | Fine Series (mm) | Medium Series (Standard) (mm) | Coarse Series (Thermal Expansion) (mm) |
|---|---|---|---|
| **M4** | $\varnothing 4.3$ | $\varnothing 4.5$ | $\varnothing 4.8$ |
| **M5** | $\varnothing 5.3$ | $\varnothing 5.5$ | $\varnothing 5.8$ |
| **M6** | $\varnothing 6.4$ | $\varnothing 6.6$ | $\varnothing 7.0$ |
| **M8** | $\varnothing 8.4$ | $\varnothing 9.0$ | $\varnothing 10.0$ |

* *Rule*: Use **Coarse Series** or **Slotted Holes** for all fasteners operating within the thermal gradient zone ($>150^\circ\text{C}$).

---

## 4. Food Contact Safety & Materials Compliance

### 4.1 Regulatory Standards
* **United States**: FDA 21 CFR 175.300 (Resinous and polymeric coatings) & Compliance Policy Guide Sec. 545.400 (Pottery/Ceramics - Lead/Cadmium leaching).
* **European Union**: Regulation (EC) No 1935/2004 (Materials and articles intended to come into contact with food) and Regulation (EC) No 2023/2006 (Good Manufacturing Practice).
* **NSF / ANSI Standard 51**: Food Equipment Materials.

### 4.2 Approved Materials for High-Temperature Food Zones ($>400^\circ\text{C}$)
1. **Austenitic Stainless Steel 304 (EN 1.4301 / X5CrNi18-10)**:
   * Standard for interior cooking liners, flame rolling domes, and stone hearth surrounds.
   * Excellent high-temperature oxidation resistance up to $870^\circ\text{C}$.
   * Safe, chemically inert, non-toxic, easily cleaned.
2. **Austenitic Stainless Steel 316 (EN 1.4401 / X5CrNiMo17-12-2)**:
   * Recommended for outdoor coastal environments or burner jet mixing nozzles where chlorides and acids may be present.
3. **Cordierite Ceramic ($2\text{MgO}\cdot 2\text{Al}_2\text{O}_3\cdot 5\text{SiO}_2$)**:
   * Highly resistant to thermal shock ($\Delta T > 600^\circ\text{C}$ quench resistance).
   * Open porous micro-structure absorbs dough steam for a crisp Neapolitan crust.
   * Must be certified lead-free, cadmium-free, and silica-dust stabilized.
4. **Vitrified Refractory Firebrick (Alumina-Silica)**:
   * Suitable for hearths and flame backstops; must meet heavy metal leaching limits.

### 4.3 Prohibited Materials in High-Temperature Cooking Chambers
* **GALVANIZED STEEL (CRITICAL HAZARD)**:
  * Zinc melts at $419.5^\circ\text{C}$ and begins vaporizing/oxidizing into toxic zinc oxide fumes ($\text{ZnO}$) above $200^\circ\text{C}$.
  * Ingesting or inhaling zinc fumes causes **Metal Fume Fever** and acute food contamination.
  * **ZERO galvanized sheet metal, zinc-plated fasteners, or zinc brackets are permitted in the hot gas path or cooking chamber.**
* **CADMIUM & LEAD**:
  * Cadmium-plated hardware and lead-bearing solders/brass fittings are strictly prohibited anywhere near the food cavity or burner gas train.
* **PTFE / FLUOROPOLYMERS (TEFLON)**:
  * Decomposes above $260^\circ\text{C}$, releasing highly toxic polymer fumes (fluorine gas compounds). Prohibited in oven interior.
* **ALUMINUM IN HOT CHAMBERS**:
  * Aluminum alloys (e.g. 5052, 6061) lose structural integrity above $200^\circ\text{C}$ and melt at $\sim 640^\circ\text{C}$. Prohibited in the inner chamber or flame path.

---

## 5. Python Helper Scripts Reference

The skill includes verified CLI automation tools located in `scripts/`:

### 5.1 Sheet Metal Bend Allowance & Flat Blank Calculator
`scripts/bend_allowance.py`:
```bash
# Calculate 90° bend in 2.0mm SS304:
python3 scripts/bend_allowance.py -t 2.0 -r 2.0 -a 90 --material ss304

# Compute flat blank for U-channel with flange verification:
python3 scripts/bend_allowance.py -t 1.5 -r 1.5 -f 30 120 30 --material ss304
```

### 5.2 Thermal Expansion & Joint Clearance Calculator
`scripts/thermal_expansion.py`:
```bash
# Compute expansion of 400mm SS304 tray heated to 500°C:
python3 scripts/thermal_expansion.py -l 400 -m ss304 -t1 20 -t2 500

# Calculate clearance gap and slot travel between SS304 tray and Cordierite stone:
python3 scripts/thermal_expansion.py -l 350 -m ss304 --mat2 cordierite -t1 20 -t2 500
```
