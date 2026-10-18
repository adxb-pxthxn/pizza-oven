---
name: oven-thermodynamics
description: Thermal physics and oven thermodynamics skill. Covers 60-90 second Neapolitan pizza thermodynamics (conduction, Stefan-Boltzmann radiation, convection, thermal effusivity), chamber geometry (classic 63% mouth-to-dome ratio, flame roll envelope, front throat flue dynamics), multi-layer insulation sizing (ceramic fiber, calcium silicate, microporous boards, ISO 13732-1 <60°C touch safety), and combustion fuel physics (LPG/propane, hardwood pellets, cordwood).
license: Apache-2.0
compatibility: Universal
metadata:
  discipline: Thermal Physics & Combustion Thermodynamics
  version: 1.0.0
---

# Oven Thermodynamics & Thermal Physics Skill

This skill provides thermal physics modeling, mathematical derivations, heat transfer equations, and combustion engineering guidelines for designing high-performance Neapolitan pizza ovens operating at $450^\circ\text{C}$ to $520^\circ\text{C}$ ($840^\circ\text{F} - 970^\circ\text{F}$).

---

## 1. Neapolitan Pizza Physics (The 60–90 Second Bake)

Baking true AVPN-compliant (*Associazione Verace Pizza Napoletana*) pizza requires simultaneously balancing three coupled modes of heat transfer so that dough gelatinization, crust blister charring (*leopard spotting*), cheese melting, and moisture flash-evaporation conclude within **60 to 90 seconds**.

```
             ================== DOME ROOF ==================
            /      Radiant Emission: q_rad = ε·σ·(T_dome⁴ - T_pizza⁴)      \
           /     Convective Flame Roll: q_conv = h_conv·(T_gas - T_pizza)   \
          /                                                           \
         |     ----------------- PIZZA -----------------               |
         |    [  Toppings / Cheese: Cooked by Radiation + Convection  ]  |
         |    [  Dough Base: Cooked by Direct Floor Conduction       ]  |
         |     -----------------------------------------               |
         |                                                             |
         \====== HEARTH FLOOR (Cordierite / Biscotto di Sorrento) =====/
               q_cond = (k_stone / t_stone) · (T_floor - T_dough)
```

### 1.1 Floor Conduction & Thermal Effusivity
Direct heat transfers from the refractory floor into the wet pizza dough ($70\%$ hydration, room temperature $20^\circ\text{C}$) via conduction.

#### The Contact Temperature Equation
When two semi-infinite solid bodies come into thermal contact, their interface temperature $T_{\text{interface}}$ is governed by their **thermal effusivity** $e$:
$$e = \sqrt{k \cdot \rho \cdot c_p} \quad \left[\frac{\text{J}}{\text{m}^2 \cdot \text{K} \cdot \text{s}^{1/2}}\right]$$
$$T_{\text{interface}} = \frac{e_{\text{stone}} T_{\text{stone}} + e_{\text{dough}} T_{\text{dough}}}{e_{\text{stone}} + e_{\text{dough}}}$$

* Where:
  * $k$: Thermal conductivity ($\text{W}/(\text{m}\cdot\text{K})$)
  * $\rho$: Density ($\text{kg}/\text{m}^3$)
  * $c_p$: Specific heat capacity ($\text{J}/(\text{kg}\cdot\text{K})$)

#### Material Effusivity Comparison at $480^\circ\text{C}$:
| Material | $k$ ($\text{W}/\text{m}\cdot\text{K}$) | $\rho$ ($\text{kg}/\text{m}^3$) | $c_p$ ($\text{J}/\text{kg}\cdot\text{K}$) | Effusivity $e$ ($\text{J}/\text{m}^2\text{K}\sqrt{\text{s}}$) | Bake Performance at $480^\circ\text{C}$ Floor |
|---|---|---|---|---|---|
| **Carbon Steel / Iron** | $45.0$ | $7850$ | $480$ | **$13,030$** | **Catastrophic burning**: Floor burns bottom black in $< 20\text{ s}$ before dough cooks. |
| **Cordierite Ceramic** | $2.2$ | $2100$ | $950$ | **$2,095$** | **Ideal portable balance**: Crisp undercarriage without scorching in 70–90 seconds. |
| **Biscotto di Sorrento** | $0.85$ | $1350$ | $880$ | **$1,005$** | **Classic Neapolitan clay**: Allows $500^\circ\text{C}+$ floor temperature with zero scorching. |
| **Pizza Dough (70% hyd.)**| $0.45$ | $1100$ | $3200$ | **$1,259$** | Heat sink absorbs floor thermal flux to flash vaporize internal water pockets. |

* **Engineering Rule**: High-temperature ovens ($>450^\circ\text{C}$) MUST use moderate-to-low effusivity hearth materials ($e \le 2200$) like cordierite or porous volcanic refractory clay. Steel or cast iron plates are restricted to low-temperature home baking ($<280^\circ\text{C}$).

---

### 1.2 Radiant Dome Emission (Stefan-Boltzmann Law)
The oven dome acts as a thermal radiator that cooks the top crust (*cornicione*), browns mozzarella, and bubbles the sauce.

$$q_{\text{rad}} = \varepsilon_{\text{dome}} \cdot \sigma \cdot F_{\text{dome}\to\text{pizza}} \cdot \left( T_{\text{dome}}^4 - T_{\text{pizza}}^4 \right)$$

* Where:
  * $\sigma = 5.67037 \times 10^{-8} \text{ W}/(\text{m}^2\cdot\text{K}^4)$ (Stefan-Boltzmann constant)
  * $\varepsilon_{\text{dome}} \approx 0.85$ to $0.90$ (Stainless steel with high-temperature carbon soot coating)
  * $F_{\text{dome}\to\text{pizza}}$: Geometric view factor ($\approx 0.75 - 0.85$ in compact parabolic/catenary domes)
  * $T_{\text{dome}} \approx 773.15 \text{ K}$ ($500^\circ\text{C}$); $T_{\text{pizza}} \approx 373.15 \text{ K}$ ($100^\circ\text{C}$)

* **Fourth-Power Radiation Dominance**:
  At $500^\circ\text{C}$, radiant heat flux reaches $\sim 15,000 \text{ W}/\text{m}^2$, accounting for over **$70\%$** of the top cooking energy. If the dome drops to $350^\circ\text{C}$, radiant power collapses by over **$55\%$**, doubling bake times and drying out the delicate dough crumb.

---

### 1.3 Convective Airflow & Boundary Layer Stripping
As hot combustion gases roll along the ceiling, forced/natural convection sweeps away the evaporative boundary layer of steam rising from the pizza crust:
$$q_{\text{conv}} = h_{\text{conv}} \cdot (T_{\text{gas}} - T_{\text{surface}})$$
* Turbulent flame sweep maintains $h_{\text{conv}} \approx 25 - 45 \text{ W}/(\text{m}^2\cdot\text{K})$.
* This high heat transfer coefficient induces the Maillard reaction and caramelization in the blisters of the crust within seconds.

---

## 2. Chamber Geometry & Aerodynamics

### 2.1 The Classic 63% Mouth-to-Dome Ratio
For optimal natural draft and thermal trapping, the chamber mouth height ($h_{\text{mouth}}$) must adhere to the traditional Neapolitan ratio:
$$\frac{h_{\text{mouth}}}{H_{\text{dome}}} \approx 0.63 \quad (60\% - 65\%)$$

```
        |<------------------- L_chamber ------------------->|
        +---------------------------------------------------+
       /                     DOME ROOF                       \  ^
      /  <-<-<- Flame Roll Ceiling Vortex <-<-<-              \ | H_dome
     /                                                         \| (e.g. 250mm)
    | [Burner / Fire]                                    FLUE   | v
    |                                                 /======/  |
    |                                                /  EXHAUST |
    |                                          =====+           |
    |                                         |     |           | ^
    |                                   INLET |     | MOUTH     | | h_mouth = 0.63 * H_dome
    |                                   AIR   |     | OPENING   | | (e.g. 158mm)
    +-----------------------------------------+-----+-----------+ v
    |================== CORDIERITE HEARTH ======================|
```

* **If $\frac{h_{\text{mouth}}}{H_{\text{dome}}} > 0.70$ (Mouth too tall)**:
  * Hot gas escapes directly out the upper mouth without circulating over the hearth.
  * Thermal efficiency plummets, flame rolls out the front opening into the operator's face, and chamber temperature drops.
* **If $\frac{h_{\text{mouth}}}{H_{\text{dome}}} < 0.55$ (Mouth too short)**:
  * Combustion air intake is choked; burner produces soot, carbon monoxide, and unstable flame lifting.
  * Accessing and turning the pizza with a peel becomes mechanically impossible.

### 2.2 Flue & Chimney Aerodynamics: The Front Throat Trap
In a properly tuned pizza oven:
1. Fresh oxygen-rich intake air enters through the **lower third** of the mouth opening.
2. The burner (rear or side) ignites this air, driving expanding hot gases along the curved ceiling.
3. The curved ceiling forces a **flame roll envelope** down toward the hearth floor.
4. The exhaust flue is positioned in a **front throat hood** above the mouth, capturing combustion products only *after* they have given up their radiant and convective heat to the cooking zone.

---

## 3. Multi-Layer Insulation & Touch Safety Calculations

### 3.1 Touch Temperature Limit (ISO 13732-1)
Under international standard **ISO 13732-1** (*Ergonomics of the thermal environment - Methods for the assessment of human responses to contact with surfaces*):
* For bare, un-coated metals: Contact threshold for burn injury ($t_{\text{contact}} = 1\text{ s}$) is **$60^\circ\text{C}$ to $65^\circ\text{C}$**.
* For powder-coated / painted metals: Contact threshold is **$70^\circ\text{C}$**.
* **Safety Mandate**: Outdoor consumer appliances must maintain exterior chassis skin temperature **$\le 60^\circ\text{C}$** when internal chamber reaches steady-state **$500^\circ\text{C}$**.

### 3.2 Steady-State Multi-Layer Heat Transfer Network
Heat transfer through the dome wall is governed by:
$$q = \frac{T_{\text{in}} - T_{\text{amb}}}{R_{\text{total}}}$$
$$R_{\text{total}} = \frac{1}{h_{\text{in}}} + \sum_{i=1}^N \frac{t_i}{k_i} + \frac{1}{h_{\text{ext}}}$$

```
T_in (500°C) ---> [1/h_in] ---> T_w1
                           ---> [t_ss / k_ss]       (Inner SS304 liner)
                           ---> [t_ins1 / k_ins1]   (Primary High-Temp Board)
                           ---> [t_ins2 / k_ins2]   (Secondary Blanket)
                           ---> [t_air / k_air]     (Stagnant Air Break)
                           ---> [t_ext / k_ext]     (Outer Powder-Coated Skin)
                           ---> [1/h_ext]      ---> T_amb (20°C)
```

### 3.3 Insulation Materials Comparison
| Insulation Material | Density ($\text{kg}/\text{m}^3$) | $k$ at $200^\circ\text{C}$ ($\text{W}/\text{m}\cdot\text{K}$) | $k$ at $500^\circ\text{C}$ ($\text{W}/\text{m}\cdot\text{K}$) | Max Temp Rating | Mechanical Form |
|---|---|---|---|---|---|
| **Ceramic Fiber Blanket** (Kaowool / Fiberfrax) | $128$ | $0.065$ | $0.110$ | $1260^\circ\text{C}$ | Flexible needle-punched mat |
| **Calcium Silicate Board** (Skamol / Promat) | $245$ | $0.055$ | $0.078$ | $1000^\circ\text{C}$ | Rigid self-supporting board |
| **Microporous Silica Panel** (Microtherm) | $320$ | **$0.022$** | **$0.034$** | $1000^\circ\text{C}$ | Ultra-thin rigid / semi-rigid |
| **Stagnant Air Standoff Gap** | $1.2$ | $0.032$ | $0.055$ | N/A | Sheet metal double-wall standoff |

* **Optimal Composite Architecture for Compact Portable Ovens**:
  1. **Inner Shell**: $1.5\text{ mm}$ SS304.
  2. **Primary Insulation**: $25\text{ mm}$ Calcium Silicate board (structural bottom) or $30\text{ mm}$ Ceramic Fiber blanket (dome).
  3. **Convection Standoff Gap**: $8 - 12\text{ mm}$ vented/stagnant air shield.
  4. **Outer Shell**: $1.2\text{ mm}$ powder-coated mild steel or brushed 304 stainless steel.
  * *Result*: Exterior touch temperature remains below **$57^\circ\text{C}$** at full $500^\circ\text{C}$ soak.

---

## 4. Fuel & Combustion Physics

### 4.1 Fuel Comparison Table
| Fuel Type | Lower Heating Value (LHV) | Delivery Format | Combustion Air Requirement | Typical Burner Sizing |
|---|---|---|---|---|
| **LPG / Propane** ($C_3H_8$) | **$46.4 \text{ MJ/kg}$** ($93 \text{ MJ/m}^3$) | Pressurized tank (28–37 mbar regulator) | $23.8 \text{ m}^3 \text{ air} / \text{m}^3 \text{ fuel}$ | $8.0 - 12.0 \text{ kW}$ ($27 - 41 \text{ kBTU/hr}$) |
| **Natural Gas** ($CH_4$) | $35.8 \text{ MJ/m}^3$ | Low-pressure line (20 mbar) | $9.5 \text{ m}^3 \text{ air} / \text{m}^3 \text{ fuel}$ | $9.0 - 13.0 \text{ kW}$ ($31 - 44 \text{ kBTU/hr}$) |
| **Hardwood Pellets** | $18.0 \text{ MJ/kg}$ | Gravity hopper / auger feed | $\sim 5.0 \text{ m}^3 \text{ air} / \text{kg}$ | $0.8 - 1.5 \text{ kg/hr}$ burn rate |
| **Hardwood Cordwood** (Oak, Beech, Ash) | $16.0 \text{ MJ/kg}$ (at $15\%$ moisture) | Split kindling ($20 - 30\text{ cm}$) | Natural chimney draft | $1.5 - 2.5 \text{ kg/hr}$ burn rate |

### 4.2 Burner Sizing Derivation
To heat a portable $400 \times 400 \text{ mm}$ chamber from $20^\circ\text{C}$ to $500^\circ\text{C}$ in $< 25 \text{ minutes}$:
* Total thermal storage capacity (stone + liner + participating insulation):
  $$Q_{\text{storage}} \approx 4.5 \text{ MJ}$$
* Open-mouth draft efficiency: $\eta_{\text{draft}} \approx 40\%$ (exhaust gas exits at $450^\circ\text{C}$).
* Required energy input:
  $$E_{\text{fuel}} = \frac{Q_{\text{storage}}}{\eta_{\text{draft}}} \approx \frac{4.5}{0.40} = 11.25 \text{ MJ}$$
* Power required for $25\text{ min}$ ($1500\text{ s}$) preheat:
  $$P_{\text{burner}} = \frac{11.25 \times 10^6 \text{ J}}{1500 \text{ s}} = 7,500 \text{ W} = \mathbf{7.5 \text{ kW}} \quad (\sim 25,600 \text{ BTU/hr})$$
* **Standard Burner Specification**: Size gas burner for **$8.0 \text{ kW}$ to $9.5 \text{ kW}$** to guarantee fast recovery between consecutive pizzas in high-wind conditions.

---

## 5. Python Helper Script Reference

The skill includes verified CLI automation tools located in `scripts/`:

### 5.1 Thermal Wall & Preheat Dynamics Simulator
`scripts/thermal_model.py`:
```bash
# Analyze 3-layer wall with 35mm ceramic fiber insulation:
python3 scripts/thermal_model.py -t 500 --insulation ceramic_fiber --ins-thick 35 --preheat

# Multi-layer custom stack with air break for touch-safety verification:
python3 scripts/thermal_model.py -t 500 --layers "ss304:1.5,calcium_silicate:30,ceramic_fiber:25,air_gap:10,mild_steel_painted:1.2" --preheat
```
