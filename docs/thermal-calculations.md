# Thermal Calculations & Heat Transfer Analysis: High-Temperature Pizza Oven

**Document Revision**: 1.0.0  
**Classification**: Thermal Physics, Combustion Thermodynamics & Numerical Analysis  
**Operating Parameters**: Steady-State Chamber: $500^\circ\text{C}$ ($773.15 \text{ K}$), Ambient: $20^\circ\text{C}$ ($293.15 \text{ K}$)  

---

## 1. Neapolitan Pizza Physics (60–90 Second Heat Balance)

True Neapolitan pizza requires cooking a thin ($2 - 3\text{ mm}$) dough disc with a puffed, airy rim (*cornicione*) in **60 to 90 seconds**. The thermal energy delivered to the pizza is partitioned across three simultaneous heat transfer mechanisms:

$$\dot{Q}_{\text{total}} = \dot{Q}_{\text{conduction (floor)}} + \dot{Q}_{\text{radiation (dome)}} + \dot{Q}_{\text{convection (flame roll)}}$$

```
                +---------------------------------------+
                |    Radiant Dome Emission (~65-70%)    |
                |    q_rad = ε·σ·F·(T_dome⁴ - T_top⁴)   |
                +---------------------------------------+
                                   |
                                   v
             +---------------------------------------------+
             |         Pizza Cornicione & Toppings         |
             +---------------------------------------------+
             |           Pizza Wet Dough Matrix            |
             +---------------------------------------------+
                                   ^
                                   |
                +---------------------------------------+
                |     Floor Conduction (~20-25%)        |
                |       q_cond = e_ratio · ΔT           |
                +---------------------------------------+
                                   |
                +---------------------------------------+
                |    Convective Flame Sweep (~10-15%)   |
                |      q_conv = h_conv · (T_gas - T)    |
                +---------------------------------------+
```

---

## 2. Floor Conduction & Thermal Effusivity Derivation

When raw pizza dough ($T_{\text{dough}} \approx 20^\circ\text{C}$, $70\%$ water hydration) is placed onto the baking floor ($T_{\text{floor}} \approx 480^\circ\text{C}$), transient 1D heat conduction occurs across their interface.

### 2.1 The Interface Contact Temperature Equation
Treating the hearth and dough as semi-infinite media during the first 10 seconds of contact, the instantaneous interface contact temperature $T_i$ is governed by their respective **thermal effusivities** ($e$):

$$e = \sqrt{k \cdot \rho \cdot c_p} \quad \left[\frac{\text{J}}{\text{m}^2 \cdot \text{K} \cdot \text{s}^{1/2}}\right]$$

$$T_i = \frac{e_{\text{floor}} T_{\text{floor}} + e_{\text{dough}} T_{\text{dough}}}{e_{\text{floor}} + e_{\text{dough}}}$$

### 2.2 Numerical Comparison of Floor Materials at $480^\circ\text{C}$

#### 1. Wet Dough Properties:
* Conductivity $k_{\text{dough}} = 0.45 \text{ W}/(\text{m}\cdot\text{K})$
* Density $\rho_{\text{dough}} = 1100 \text{ kg}/\text{m}^3$
* Heat capacity $c_{p,\text{dough}} = 3200 \text{ J}/(\text{kg}\cdot\text{K})$
* $$e_{\text{dough}} = \sqrt{0.45 \cdot 1100 \cdot 3200} = \mathbf{1,258.6 \text{ J}/(\text{m}^2\cdot\text{K}\cdot\text{s}^{1/2})}$$

#### 2. Mild Carbon Steel Plate:
* $k = 45.0 \text{ W}/(\text{m}\cdot\text{K})$, $\rho = 7850 \text{ kg}/\text{m}^3$, $c_p = 480 \text{ J}/(\text{kg}\cdot\text{K})$
* $$e_{\text{steel}} = \sqrt{45.0 \cdot 7850 \cdot 480} = \mathbf{13,030.0 \text{ J}/(\text{m}^2\cdot\text{K}\cdot\text{s}^{1/2})}$$
* $$T_i = \frac{13030(480) + 1259(20)}{13030 + 1259} = \mathbf{439.5^\circ\text{C}}$$
* *Outcome*: **Catastrophic Failure**. The dough interface instantly hits $\sim 440^\circ\text{C}$. Flour burns to acrid carbon soot within 15–20 seconds, before heat can conduct through the dough interior.

#### 3. Cordierite Ceramic Hearth ($15\text{ mm}$):
* $k = 2.2 \text{ W}/(\text{m}\cdot\text{K})$, $\rho = 2100 \text{ kg}/\text{m}^3$, $c_p = 950 \text{ J}/(\text{kg}\cdot\text{K})$
* $$e_{\text{cordierite}} = \sqrt{2.2 \cdot 2100 \cdot 950} = \mathbf{2,095.0 \text{ J}/(\text{m}^2\cdot\text{K}\cdot\text{s}^{1/2})}$$
* $$T_i = \frac{2095(480) + 1259(20)}{2095 + 1259} = \mathbf{307.3^\circ\text{C}}$$
* *Outcome*: **Optimal Balance**. The contact temperature settles at $\sim 307^\circ\text{C}$, providing rapid crust spring and blister development while evaporating moisture without blackening the base over a 75-second bake.

#### 4. Biscotto di Sorrento (Traditional Volcanic Clay):
* $k = 0.85 \text{ W}/(\text{m}\cdot\text{K})$, $\rho = 1350 \text{ kg}/\text{m}^3$, $c_p = 880 \text{ J}/(\text{kg}\cdot\text{K})$
* $$e_{\text{biscotto}} = \sqrt{0.85 \cdot 1350 \cdot 880} = \mathbf{1,004.9 \text{ J}/(\text{m}^2\cdot\text{K}\cdot\text{s}^{1/2})}$$
* $$T_i = \frac{1005(480) + 1259(20)}{1005 + 1259} = \mathbf{224.2^\circ\text{C}}$$
* *Outcome*: Excellent for extreme heat ($>520^\circ\text{C}$); allows extended bakes without undercarriage scorching.

---

## 3. Radiant Dome Emission & View Factor Analysis

Top-down radiation is the dominant heat source responsible for cheese caramelization, Maillard browning, and blistering (*leopard spots*) on the *cornicione*.

### 3.1 Stefan-Boltzmann Formulation
The net radiative heat flux transferred from the dome to the pizza top surface is:

$$\dot{q}_{\text{rad}} = \varepsilon_{\text{effective}} \cdot \sigma \cdot F_{\text{dome}\to\text{pizza}} \cdot \left( T_{\text{dome}}^4 - T_{\text{pizza}}^4 \right)$$

* Stefan-Boltzmann constant: $\sigma = 5.67037 \times 10^{-8} \text{ W}/(\text{m}^2\cdot\text{K}^4)$
* Inner dome emissivity (carbon-seasoned 304 SS): $\varepsilon_{\text{dome}} \approx 0.85$
* Pizza surface emissivity (water/dough/oil mix): $\varepsilon_{\text{pizza}} \approx 0.92$
* Two-surface enclosed exchange factor:
  $$\varepsilon_{\text{effective}} = \frac{1}{\frac{1}{\varepsilon_{\text{dome}}} + \frac{A_{\text{pizza}}}{A_{\text{dome}}}\left(\frac{1}{\varepsilon_{\text{pizza}}} - 1\right)} \approx 0.82$$
* View factor for a low catenary parabolic dome ($H = 250\text{ mm}$, $W = 405\text{ mm}$):
  $$F_{\text{dome}\to\text{pizza}} \approx 0.80$$

### 3.2 Numerical Radiation Flux Calculation
At steady-state Neapolitan temperature:
* $T_{\text{dome}} = 500^\circ\text{C} = 773.15 \text{ K}$
* $T_{\text{pizza}} = 100^\circ\text{C} = 373.15 \text{ K}$ (boiling moisture cap)

$$T_{\text{dome}}^4 = (773.15)^4 = 3.5734 \times 10^{11} \text{ K}^4$$
$$T_{\text{pizza}}^4 = (373.15)^4 = 1.9388 \times 10^{10} \text{ K}^4$$
$$\Delta(T^4) = 3.3795 \times 10^{11} \text{ K}^4$$

$$\dot{q}_{\text{rad}} = 0.82 \cdot (5.67037 \times 10^{-8}) \cdot 0.80 \cdot (3.3795 \times 10^{11}) = \mathbf{12,568.6 \text{ W/m}^2} \quad (\sim 12.6 \text{ kW/m}^2)$$

For a $320 \text{ mm}$ (12.6") pizza ($A = \pi \cdot 0.16^2 = 0.0804 \text{ m}^2$):
$$\dot{Q}_{\text{rad, pizza}} = 12568.6 \cdot 0.0804 = \mathbf{1,010.5 \text{ W}} \quad (1.01 \text{ kW})$$
Over a $70 \text{ second}$ bake, total radiant energy absorbed by the pizza:
$$E_{\text{rad}} = 1010.5 \times 70 = \mathbf{70.7 \text{ kJ}}$$

---

## 4. Chamber Aerodynamics & The 63% Mouth-to-Dome Ratio

### 4.1 Fluid Mechanics of the Combustion Vortex
In a front-flue pizza oven, combustion air moves under a natural buoyancy-driven draft governed by the stack effect (Bernoulli / hydrostatic pressure differential):

$$\Delta P_{\text{draft}} = \rho_{\text{ambient}} \cdot g \cdot H_{\text{eff}} \left( 1 - \frac{T_{\text{amb}}}{T_{\text{gas}}} \right)$$

```
                                  [ EXHAUST CHIMNEY ]
                                          ^
                                          |
                         +----------------+---------+
                         |      FRONT FLUE HOOD     |
                         |   (Combustion Product)   |
  =======================+                          |
 /  Hot Laminar Flame Roll   -> -> -> ->            |
|                                        \          |
|  [Rear Burner]                          v         |  Chamber Mouth
|   Gas Jet Flame                          \        |  h_mouth = 158mm
|                                           v       |
|                                            \      |
|    ==== CORDIERITE BAKING HEARTH ====       v     |
|                                        <-- <-- <--|  Fresh O2 Ingress
+---------------------------------------------------+  (Lower 1/3 of mouth)
```

### 4.2 The Neapolitan 63% Golden Ratio Derivation
* **Dome Ceiling Height**: $H_{\text{dome}} = 250.0 \text{ mm}$
* **Optimum Mouth Opening Height**:
  $$h_{\text{mouth}} = 0.632 \times H_{\text{dome}} = 0.632 \times 250 = \mathbf{158.0 \text{ mm}}$$

* **Aerodynamic Balance**:
  * **Ingress Boundary (Lower $0 - 55 \text{ mm}$)**: Cold ambient air ($20^\circ\text{C}$, $\rho = 1.20 \text{ kg/m}^3$) rushes in along the bottom hearth plane at $v \approx 0.8 - 1.2 \text{ m/s}$, feeding the rear burner with fresh oxygen.
  * **Egress Boundary (Upper $55 - 158 \text{ mm}$)**: Expanding hot combustion products ($>550^\circ\text{C}$, $\rho \approx 0.42 \text{ kg/m}^3$) sweep along the ceiling, vortex into the front hood, and vent upward through the $\varnothing 101.6 \text{ mm}$ chimney.
  * *Failure Mode at $>70\%$ Ratio*: The hot ceiling layer collapses out the front mouth opening, scorching the operator and dropping oven temperature.
  * *Failure Mode at $<55\%$ Ratio*: The flame chokes, generating excessive soot and yellow tipping due to air starvation.

---

## 5. Multi-Layer Insulation Model & Touch Temperature Verification

Under **ISO 13732-1**, the maximum touch temperature on an accessible exterior powder-coated surface must not exceed **$60.0^\circ\text{C}$** when the interior chamber operates continuously at **$500.0^\circ\text{C}$**.

### 5.1 Thermal Resistance Model
$$R_{\text{total}} = \frac{1}{h_{\text{in}}} + \sum_{i=1}^N \frac{t_i}{k_i} + \frac{1}{h_{\text{ext}}}$$
$$\dot{q}_{\text{loss}} = \frac{T_{\text{in}} - T_{\text{amb}}}{R_{\text{total}}}$$

#### Composite Wall Architecture:
1. **Layer 1: Inner Shell**: $1.5 \text{ mm}$ AISI 304 ($k = 18.0 \text{ W/m}\cdot\text{K}$)
   $$R_1 = \frac{0.0015}{18.0} = 0.000083 \text{ m}^2\cdot\text{K/W}$$
2. **Layer 2: Structural Sub-Layer**: $30.0 \text{ mm}$ Calcium Silicate Board ($k = 0.065 \text{ W/m}\cdot\text{K}$)
   $$R_2 = \frac{0.0300}{0.065} = 0.4615 \text{ m}^2\cdot\text{K/W}$$
3. **Layer 3: Thermal Blanket**: $25.0 \text{ mm}$ Ceramic Fiber Blanket ($k = 0.080 \text{ W/m}\cdot\text{K}$)
   $$R_3 = \frac{0.0250}{0.080} = 0.3125 \text{ m}^2\cdot\text{K/W}$$
4. **Layer 4: Standoff Air Break**: $10.0 \text{ mm}$ Stagnant Gap ($k = 0.035 \text{ W/m}\cdot\text{K}$)
   $$R_4 = \frac{0.0100}{0.035} = 0.2857 \text{ m}^2\cdot\text{K/W}$$
5. **Layer 5: Outer Chassis Shell**: $1.2 \text{ mm}$ Powder-Coated Mild Steel ($k = 45.0 \text{ W/m}\cdot\text{K}$)
   $$R_5 = \frac{0.0012}{45.0} = 0.000027 \text{ m}^2\cdot\text{K/W}$$

* Sum of conductive resistances: $R_{\text{cond, total}} = 1.0598 \text{ m}^2\cdot\text{K/W}$.
* Convective/Radiative resistances:
  * Internal: $h_{\text{in}} = 30.0 \text{ W/m}^2\text{K} \implies R_{\text{in}} = 0.0333 \text{ m}^2\cdot\text{K/W}$.
  * External: $h_{\text{ext}} \approx 10.9 \text{ W/m}^2\text{K} \implies R_{\text{ext}} = 0.0917 \text{ m}^2\cdot\text{K/W}$.
* Total thermal resistance:
  $$R_{\text{total}} = 0.0333 + 1.0598 + 0.0917 = \mathbf{1.1848 \text{ m}^2\cdot\text{K/W}}$$

### 5.2 Heat Flux & Temperature Gradient Results
$$\dot{q} = \frac{500.0 - 20.0}{1.1848} = \mathbf{405.1 \text{ W/m}^2}$$

Interface temperature drops:
* **Chamber Internal Gas**: $500.0^\circ\text{C}$
* **Inner SS304 Surface**: $500 - 405.1(0.0333) = \mathbf{486.5^\circ\text{C}}$
* **After Calcium Silicate Board**: $486.5 - 405.1(0.4615) = \mathbf{299.5^\circ\text{C}}$
* **After Ceramic Fiber Blanket**: $299.5 - 405.1(0.3125) = \mathbf{172.9^\circ\text{C}}$
* **After Standoff Air Break**: $172.9 - 405.1(0.2857) = \mathbf{57.2^\circ\text{C}}$
* **Outer Powder-Coated Skin Touch Temp**: $\mathbf{56.9^\circ\text{C}}$

* **Touch Safety Conclusion**:
  $$T_{\text{exterior}} = 56.9^\circ\text{C} < 60.0^\circ\text{C} \quad \mathbf{[PASS] \text{ Compliant with ISO 13732-1}}$$

Total steady-state heat loss through entire oven surface ($A_{\text{total}} = 0.64 \text{ m}^2$):
$$\dot{Q}_{\text{loss}} = 405.1 \text{ W/m}^2 \times 0.64 \text{ m}^2 = \mathbf{259.3 \text{ W}} \quad (0.26 \text{ kW})$$

---

## 6. Burner Sizing & Preheat Dynamics

### 6.1 Total Thermal Mass Breakdown
To bring the oven from $20^\circ\text{C}$ to $500^\circ\text{C}$ ($\Delta T = 480 \text{ K}$):

| Component | Mass ($m$) | Specific Heat ($c_p$) | Heat Capacity ($C_{\text{th}} = m \cdot c_p$) | Stored Energy at $500^\circ\text{C}$ |
|---|---|---|---|---|
| **Cordierite Stone ($15\text{ mm}$)** | $5.04 \text{ kg}$ | $950 \text{ J/kg}\cdot\text{K}$ | $4,788 \text{ J/K}$ | $2.30 \text{ MJ}$ |
| **Inner SS304 Dome ($1.5\text{ mm}$)** | $7.58 \text{ kg}$ | $500 \text{ J/kg}\cdot\text{K}$ | $3,790 \text{ J/K}$ | $1.82 \text{ MJ}$ |
| **Participating Insulation ($\sim 35\%$)** | $1.02 \text{ kg}$ | $1050 \text{ J/kg}\cdot\text{K}$ | $1,071 \text{ J/K}$ | $0.51 \text{ MJ}$ |
| **TOTALS** | **$13.64 \text{ kg}$** | — | **$9,649 \text{ J/K}$** | **$4.63 \text{ MJ}$** |

### 6.2 Burner Sizing & Energy Requirement
* Open-mouth draft thermal capture efficiency: $\eta_{\text{capture}} \approx 40\%$ (exhaust gas exits at $\sim 450^\circ\text{C}$).
* Total fuel chemical energy required:
  $$E_{\text{fuel}} = \frac{4.63 \times 10^6 \text{ J}}{0.40} = 11.58 \text{ MJ}$$
* Sizing for an **8.0 kW burner** ($27,300 \text{ BTU/hr}$):
  * Useful heat ingress rate: $\dot{Q}_{\text{net}} = 8.0 \times 0.40 = 3.20 \text{ kW} = 3,200 \text{ W}$.
  * Average steady-state loss during preheat: $\dot{Q}_{\text{loss, avg}} \approx 200 \text{ W}$.
  * Effective heating rate: $\dot{Q}_{\text{eff}} = 3,000 \text{ W}$.
  * Time to reach $500^\circ\text{C}$:
    $$t_{\text{preheat}} = \frac{4.63 \times 10^6 \text{ J}}{3000 \text{ W}} = 1,543 \text{ s} \approx \mathbf{25.7 \text{ minutes}}$$

---

## 7. Fuel Consumption & Energy Density Summary

| Fuel Type | LHV Density | Firing Rate for $8.0\text{ kW}$ | Cost / Bake Hour (Nominal) | Emissions & Ash |
|---|---|---|---|---|
| **LPG Propane** | $46.4 \text{ MJ/kg}$ | $0.62 \text{ kg/hr}$ ($1.2 \text{ L/hr}$) | $\sim \$1.50 - \$2.00$ | Clean blue flame, zero ash, precise needle-valve control. |
| **Hardwood Pellets** | $18.0 \text{ MJ/kg}$ | $1.60 \text{ kg/hr}$ | $\sim \$1.00 - \$1.50$ | Fast ignite, gravity feed, minimal ash ($<0.7\%$). |
| **Dry Hardwood Kindling** | $16.0 \text{ MJ/kg}$ (at $15\%$ moisture) | $1.80 \text{ kg/hr}$ | $\sim \$0.80 - \$1.20$ | Traditional wood aroma, live rolling ember bed, requires ash cleaning. |
