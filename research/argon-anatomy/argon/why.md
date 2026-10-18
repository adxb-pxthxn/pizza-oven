### Epistemological Convention

Every technical statement in this analysis is tagged according to its evidentiary basis:
*   **[Published]**: Directly stated in the 18 October 2026 source pack.
*   **[Inferred]**: Deduced directly from published dimensions, materials lists, or regulatory standards by geometric subtraction or standard engineering practice.
*   **[Modelled]**: Calculated from first-principles heat transfer, thermodynamics, or mechanics using the repository's physical constants and explicitly stated assumptions.

---

## 1. Architecture and Subsystem Breakdown

### 1.1 Gozney Arc Lite (`GOZ-3102`)
*   **Outer Shell**: **[Published]** Drawn/stamped sheet metal and die-cast aluminium finished in high-temperature paint and powder coat. **[Inferred]** The shell forms a structural monocoque clamping the internal insulation blanket against the inner core without an intermediate chassis frame.
*   **Inner Core**: **[Published]** Stainless steel (grade unspecified on the Arc Lite help centre page, **[Inferred]** 304 stainless steel by analogy with Tread and Dome XL). Encloses an internal volume of $325\text{ mm (W)} \times 355\text{ mm (D)} \times 150\text{ mm (H)}$.
*   **Insulation**: **[Published]** Single-layer ("1" on the comparison tool), water-soluble alkaline-earth silicate (AES) fibre blanket. **[Inferred]** Comparing the external width ($430\text{ mm}$) to the internal width ($325\text{ mm}$) leaves $(430 - 325) / 2 = 52.5\text{ mm}$ per side average budget for inner skin, insulation blanket, air gap, outer pressing, and lateral burner plumbing on the left side.
*   **Hearth Floor**: **[Published]** $12\text{ mm}$ removable cordierite stone.
*   **Burner & Gas Train**: **[Published]** $3.4\text{ kW}$ ($11,687\text{ BTU/h}$) lateral propane burner Located on the side of the hearth so yellow/orange diffusion-biased flames roll across the ceiling apex. Uses a $0.95\text{ mm}$ injector at $11\text{ in WC}$ ($2.74\text{ kPa}$) for US/CA (ANSI Z21.58 / CSA 1.6), or $0.85\text{ mm}$, $0.90\text{ mm}$, $0.95\text{ mm}$ across UK/EU categories $\text{I3P(30)}$, $\text{I3+(28-30/37)}$, $\text{I3P(37)}$, $\text{I3P(50)}$ at $252\text{ g/h}$.
*   **Air & Exhaust (Flue)**: **[Published]** No user flue; exhaust exits entirely through the $325\text{ mm} \times 85\text{ mm}$ front mouth arch. Primary and secondary combustion air enter through slots in the rear/side burner dock.
*   **Door**: **[Published]** None. Covering the mouth while lit is explicitly prohibited.
*   **Dock & Controls**: **[Published]** Rear/side dock houses the gas valve, piezo/electric igniter, and Flame Failure Device (FFD) thermocouple. Operated via a single push-turn dial held for up to $30\text{ s}$ on ignition. No built-in thermometer.

### 1.2 Gozney Tread (`GOZ-1893`)
*   **Outer Shell**: **[Published]** Multi-part enclosure comprising an SPCC (cold-rolled carbon steel, JIS G 3141) top pressing with ceramic paint, an SPCC lower pressing with high-temperature powder coat, a brushed 304 stainless steel mid-wrap, and powder-coated extruded aluminium trim, plus integrated GF20 PPS (20% glass-filled polyphenylene sulfide) carry/roof-rack handles.
*   **Inner Core & Landing**: **[Published]** 304 stainless steel inner dome ($310\text{ mm W} \times 380\text{ mm D} \times 150\text{ mm H}$) paired with a ceramic-painted 304 mouth arch and a high-pressure die-cast (HPDC) aluminium front landing capped with a 304 scratch guard.
*   **Insulation**: **[Published]** Single-layer ("1") non-carcinogenic, water-soluble calcium-magnesium silicate fibre (AES wool). **[Inferred]** Total width delta is $418 - 310 = 108\text{ mm}$ ($54\text{ mm}$ per side average); height delta is $320 - 150 = 170\text{ mm}$ (which includes top handle standoff height and base feet).
*   **Hearth Floor**: **[Published]** $12\text{ mm}$ removable cordierite stone.
*   **Burner & Gas Train**: **[Published]** $3.7\text{ kW}$ ($12,621\text{ BTU/h}$ on comparison tool; $12,500\text{ BTU/h}$ in US manual) lateral LPG burner. US spec uses a $0.98\text{ mm}$ injector at $11\text{ in WC}$. EU spec lists $273.8\text{ g/h}$ across $30/37/50\text{ mbar}$.
*   **Air, Exhaust & Door**: **[Published]** Flueless front-breathing design exhausting out the $310\text{ mm} \times 85\text{ mm}$ mouth. Requires $50\text{ mm}$ clear air around the SPCC dock for primary air intake. No door; LPG only; no wood or natural gas conversion.
*   **Dock & Controls**: **[Published]** Powder-coated SPCC dock with GF30 PA (30% glass-filled nylon) hose bracket, GF30 PP (polypropylene) control dial, electric ignition, and an analog thermometer measuring stone temperature.

### 1.3 Gozney Dome XL Gen 2 (`GOZ-2509`)
*   **Outer Shell**: **[Published]** Aluminised steel top pressing with ceramic paint, aluminised steel lower pressing with high-temperature powder coat, brushed 304 mid-wrap, and extruded aluminium trim. External envelope is $946\text{ mm (W)} \times 697\text{ mm (D)} \times 997\text{ mm (H, including removable flue)}$. **[Inferred]** Because the shipping carton is $613\text{ mm}$ high, the oven body excluding the removable flue assembly is $< 613\text{ mm}$ tall. Concerning the unassigned $219\text{ mm}$ and $543\text{ mm}$ callouts on the spec-sheet drawing: **[Inferred — Hypothesis]** $543\text{ mm}$ either repeats the internal depth ($543\text{ mm}$) or gives the main body height before the flue collar, while $219\text{ mm}$ represents either the lower plinth/dock height or the mouth-to-side-wall offset ($(946 - 470)/2 = 238\text{ mm}$ external, or $(724 - 470)/2 = 127\text{ mm}$ internal, making lower-plinth or flue-section height the more plausible assignment for $219\text{ mm}$).
*   **Inner Core & Landing**: **[Published]** 304 stainless steel inner core ($724\text{ mm W} \times 543\text{ mm D} \times 238\text{ mm H}$), ceramic-painted 304 mouth arch ($470\text{ mm W} \times 140\text{ mm H}$), and ceramic-painted HPDC aluminium landing with 304 scratch guard.
*   **Insulation**: **[Published]** 3-layer calcium-magnesium silicate fibre system. **[Inferred]** Width delta is $(946 - 724)/2 = 111\text{ mm}$ per side—more than double the wall thickness budget of the single-layer ovens ($52.5\text{–}54\text{ mm}$), accommodating multiple overlapping AES blankets above the crown and rigid insulation board under the hearth.
*   **Hearth Floor**: **[Published]** $30\text{ mm}$ removable cordierite stone (handled with a dedicated stone tool) plus a cast/fabricated duct grate on the right-hand side for solid-fuel under-fire air.
*   **Burner & Multi-Fuel System**: **[Published]** $10.6\text{ kW}$ lateral gas burner (US: $1.86\text{ mm}$ injector, $36,850\text{ BTU/h}$ at $11\text{ in WC}$; EU: $784\text{ g/h}$; comparison tool: $36,100\text{ BTU/h}$, $0.75\text{ kg/h}$). Includes a burner guard. Certified for propane, kiln-dried hardwood ($10\text{–}20\%$ moisture, $16\%$ optimum), and charcoal. An optional wood-fire control kit provides regulated under-bed airflow through the right-hand duct grate.
*   **Air, Flue & Door**: **[Published]** Top-mounted removable flue pipe, collar, flue top, and cap sitting above the chamber (inside the mouth-to-hearth exhaust zone), with a rain guard spaced $3\text{ mm}$ off the oven top. Ships with a door (permitted only when the gas burner is off and wood flames have died down to embers).
*   **Dock & Controls**: **[Published]** GF20 PP dock, anodised 6063 aluminium dial, USB-C rechargeable digital ambient thermometer with two meat probes.

---

## 2. Mouth-to-Chamber Geometry and Solid-Fuel Physics

### 2.1 Dimensional Ratios
**[Modelled]** Computing the dimensionless opening ratios from the **[Published]** internal and mouth dimensions:

1.  **Horizontal Mouth-to-Chamber Width Ratio ($W_{\text{mouth}} / W_{\text{int}}$)**:
    *   **Arc Lite**: $\frac{325\text{ mm}}{325\text{ mm}} = 1.000$ ($100.0\%$)
    *   **Tread**: $\frac{310\text{ mm}}{310\text{ mm}} = 1.000$ ($100.0\%$)
    *   **Dome XL Gen 2**: $\frac{470\text{ mm}}{724\text{ mm}} = 0.649$ ($64.9\%$)

2.  **Vertical Mouth-to-Apex Height Ratio ($H_{\text{mouth}} / H_{\text{int}}$)**:
    *   **Arc Lite**: $\frac{85\text{ mm}}{150\text{ mm}} = 0.567$ ($56.7\%$)
    *   **Tread**: $\frac{85\text{ mm}}{150\text{ mm}} = 0.567$ ($56.7\%$)
    *   **Dome XL Gen 2**: $\frac{140\text{ mm}}{238\text{ mm}} = 0.588$ ($58.8\%$)

### 2.2 Why Full-Width Mouths Cannot Burn Wood Safely
**[Inferred]** The traditional Neapolitan brick oven heuristic sets $H_{\text{mouth}} / H_{\text{int}} \approx 0.63$ to balance buoyant hot-gas retention in the upper dome ("the thermal bell") against radiant view-factor losses and cold air entrainment across the hearth. All three Gozney ovens drop this vertical ratio slightly lower ($0.567\text{–}0.588$) to trap a deeper pocket of rolling gas above the mouth lip ($65\text{ mm}$ vertical trap on Arc Lite/Tread; $98\text{ mm}$ on Dome XL).

However, the horizontal ratio ($W_{\text{mouth}} / W_{\text{int}}$) dictates whether an oven can hold a wood fire next to a pizza:
*   **On Arc Lite ($325\text{ mm}$ wide) and Tread ($310\text{ mm}$ wide)**: **[Modelled]** A $12\text{ in}$ ($305\text{ mm}$) pizza leaves a total lateral clearance of $(325 - 305) = 20\text{ mm}$ in Arc Lite and $(310 - 305) = 5\text{ mm}$ in Tread. There is zero hearth width available for an ash bed or burning logs. Furthermore, because $W_{\text{mouth}} / W_{\text{int}} = 1.00$, the side walls run straight to the front opening without "cheeks" (front return baffles). If wood were placed inside, there is no dead-corner zone to shelter the ember bed from cross-drafts, nor a top chimney flue to create vertical stack draft ($\Delta P_{\text{stack}} = \rho_a g H_{\text{flue}} \left(1 - \frac{T_a}{T_{\text{gas}}}\right)$). Wood volatiles and smoke would spill directly out the full-width mouth, overheating the front fascia and starving the rear of oxygen.
*   **On Dome XL Gen 2 ($724\text{ mm}$ wide, $470\text{ mm}$ mouth)**: **[Modelled]** Subtracting the mouth width from the internal width leaves $724 - 470 = 254\text{ mm}$ of total front cheek structure ($\approx 127\text{ mm}$ per side if symmetric). An $18\text{ in}$ ($457\text{ mm}$) pizza requires $\sim 460\text{ mm}$ of central/left hearth, leaving $724 - 457 = 267\text{ mm}$ of lateral hearth width. **[Published]** The manual instructs the user to push the established wood fire to the right-hand side over the duct grate while the gas burner occupies the left-hand side. **[Inferred]** The right-hand front cheek shields the burning wood pile from direct wind blow-out and radiation loss out the mouth, while under-grate air feeds the ember bed and the top flue pulls the wood flame up across the $238\text{ mm}$ dome apex and back toward the front exhaust hood before exiting up the chimney.

---

## 3. Hearth Stone Mass, Stored Energy, and Heat-Up Capture Fraction

### 3.1 Calorific Value Mismatch in Published Gas Ratings
**[Modelled]** Before computing stone energy capture, the discrepancy between published kW ratings and mass flow rates must be resolved using propane's Lower Heating Value ($\text{LHV} = 46.4\text{ MJ/kg}$) vs Gross Calorific Value ($\text{HHV} \approx 50.35\text{ MJ/kg}$, or EN 437 reference conditions):
$$\dot{Q}_{\text{LHV}} = \dot{m} \times \frac{46.4\text{ MJ/kg}}{3.6\text{ MJ/kWh}}$$
*   **Arc Lite**: **[Published]** UK/EU plate states $3.4\text{ kW}$ and $252\text{ g/h}$; US comparison tool states $3.4\text{ kW}$ and $273.8\text{ g/h}$. **[Modelled]** At $\text{LHV} = 46.4\text{ MJ/kg}$, $0.252\text{ kg/h}$ yields $3.25\text{ kW}$ (and at $\text{HHV} = 48.6\text{ MJ/kg}$, it yields $3.40\text{ kW}$). Note that $\frac{3.4\text{ kW}}{3.7\text{ kW}} \times 273.8\text{ g/h} = 251.6\text{ g/h} \approx 252\text{ g/h}$. Therefore, $273.8\text{ g/h}$ on the US comparison tool for Arc Lite is a transcription error copied from the Tread column. Builders should use **$3.4\text{ kW}$** and **$252\text{ g/h}$**.
*   **Tread**: **[Published]** Spec sheet states $3.7\text{ kW}$ and $273.8\text{ g/h}$. **[Modelled]** At $\text{LHV} = 46.4\text{ MJ/kg}$, $0.2738\text{ kg/h}$ produces $3.53\text{ kW}$; producing $3.7\text{ kW}$ on an LHV basis requires $287\text{ g/h}$. At EN 437 gross reference enthalpy ($\approx 48.65\text{ MJ/kg}$), $273.8\text{ g/h}$ equals exactly $3.70\text{ kW}$. Builders should design to the **$3.7\text{ kW}$** nameplate.
*   **Dome XL Gen 2**: **[Published]** EU manual states $10.6\text{ kW}$ and $784\text{ g/h}$; spec sheet states "$10.6\text{ kWh}$ [sic] | $0.75\text{ kg/h}$". **[Modelled]** At $\text{LHV} = 46.4\text{ MJ/kg}$, $0.75\text{ kg/h}$ is $9.67\text{ kW}$ and $0.784\text{ kg/h}$ is $10.11\text{ kW}$. Using the same $48.65\text{ MJ/kg}$ gross conversion factor as Tread, $0.784\text{ kg/h}$ equals exactly $10.60\text{ kW}$. Builders should design to **$10.6\text{ kW}$** and **$784\text{ g/h}$**.

### 3.2 Stone Mass and Thermal Storage Arithmetic
**[Modelled]** Using cordierite properties $\rho = 2100\text{ kg/m}^3$, $c_p = 950\text{ J/(kg}\cdot\text{K)}$, and a bulk temperature rise $\Delta T = 480\text{ K}$ (from $20^\circ\text{C}$ ambient to $500^\circ\text{C}$ target), the volumetric heat capacity is:
$$\rho c_p = 2100 \times 950 = 1.995\text{ MJ/(m}^3\cdot\text{K)}$$
For $\Delta T = 480\text{ K}$, the stored thermal energy per cubic metre of fully soaked cordierite is:
$$e_{\text{vol}} = 1.995\text{ MJ/(m}^3\cdot\text{K)} \times 480\text{ K} = 957.6\text{ MJ/m}^3$$

Because Gozney publishes internal chamber width and depth ($W_{\text{int}} \times D_{\text{int}}$) rather than the exact D-shaped stone profile after corner radii and burner cutouts, we calculate two explicit bounds:
1.  **Bounding Rectangle ($f_{\text{shape}} = 1.00$)**: $A_{\text{rect}} = W_{\text{int}} \times D_{\text{int}}$.
2.  **Shaped Cordierite Hearth ($f_{\text{shape}} = 0.85$ for Arc Lite/Tread; $f_{\text{shape}} = 0.80$ for Dome XL to account for the wider arch taper, burner slot, and ash grate)**: $A_{\text{shaped}} = f_{\text{shape}} \times W_{\text{int}} \times D_{\text{int}}$.

| Metric (Modelled from Published Envelopes) | Arc Lite ($t = 12\text{ mm}$) | Tread ($t = 12\text{ mm}$) | Dome XL Gen 2 ($t = 30\text{ mm}$) |
| :--- | :--- | :--- | :--- |
| **Internal $W_{\text{int}} \times D_{\text{int}}$ [Published]** | $0.325 \times 0.355\text{ m}$ | $0.310 \times 0.380\text{ m}$ | $0.724 \times 0.543\text{ m}$ |
| **Bounding Area $A_{\text{rect}}$ ($f=1.00$)** | $0.1154\text{ m}^2$ | $0.1178\text{ m}^2$ | $0.3931\text{ m}^2$ |
| **Stone Volume $V_{\text{rect}}$ ($f=1.00$)** | $0.001385\text{ m}^3$ ($1.38\text{ L}$) | $0.001414\text{ m}^3$ ($1.41\text{ L}$) | $0.01179\text{ m}^3$ ($11.79\text{ L}$) |
| **Stone Mass $m_{\text{rect}}$ ($f=1.00$)** | $2.91\text{ kg}$ | $2.97\text{ kg}$ | $24.77\text{ kg}$ |
| **Shaped Stone Mass $m_{\text{shaped}}$ ($f=0.85 / 0.80$)** | $2.47\text{ kg}$ | $2.52\text{ kg}$ | $19.81\text{ kg}$ |
| **Stored Energy $Q_{\text{stone, rect}}$ ($\Delta T = 480\text{ K}$)** | $1.33\text{ MJ}$ | $1.35\text{ MJ}$ | $11.29\text{ MJ}$ |
| **Stored Energy $Q_{\text{stone, shaped}}$ ($\Delta T = 480\text{ K}$)** | $1.13\text{ MJ}$ | $1.15\text{ MJ}$ | $9.04\text{ MJ}$ |
| **Nameplate Burner Power $\dot{Q}_{\text{in}}$ [Published]** | $3.4\text{ kW}$ | $3.7\text{ kW}$ | $10.6\text{ kW}$ |
| **Heat-Up Time $t_{\text{heat}}$ [Published]** | $20\text{–}30\text{ min}$ | $15\text{–}20\text{ min}$ | $40\text{–}45\text{ min}$ (US) / $60\text{ min}$ (EU) |
| **Total Gas Energy Fired $Q_{\text{in}} = \dot{Q}_{\text{in}} \cdot t_{\text{heat}}$** | $4.08\text{–}6.12\text{ MJ}$ | $3.33\text{–}4.44\text{ MJ}$ | $25.44\text{–}28.62\text{ MJ}$ ($40\text{–}45\text{ m}$) / $38.16\text{ MJ}$ ($60\text{ m}$) |
| **Capture Fraction $\eta_{\text{rect}} = Q_{\text{stone, rect}} / Q_{\text{in}}$** | $32.5\%$ ($20\text{ m}$) – $21.7\%$ ($30\text{ m}$) | $40.7\%$ ($15\text{ m}$) – $30.5\%$ ($20\text{ m}$) | $44.4\%$ ($40\text{ m}$) – $29.6\%$ ($60\text{ m}$) |
| **Capture Fraction $\eta_{\text{shaped}} = Q_{\text{stone, shaped}} / Q_{\text{in}}$** | $27.6\%$ ($20\text{ m}$) – $18.4\%$ ($30\text{ m}$) | $34.6\%$ ($15\text{ m}$) – $25.9\%$ ($20\text{ m}$) | $35.5\%$ ($40\text{ m}$) – $23.7\%$ ($60\text{ m}$) |

### 3.3 Why $12\text{ mm}$ vs $30\text{ mm}$: Conduction Time Scales and Capture Fraction
**[Modelled]** In a top-heated gas oven where exhaust leaves through an open front mouth, $70\text{–}80\%$ of the burner enthalpy exits with the flue gas and wall losses; a realistic net stone capture fraction $\eta_{\text{stone}}$ over a full soak is $20\text{–}30\%$.

1.  **Why Dome XL conflicts on heat-up time ($40\text{–}45\text{ min}$ vs $60\text{ min}$)**:
    The thermal diffusivity of cordierite is:
    $$\alpha = \frac{k}{\rho c_p} = \frac{2.2\text{ W/(m}\cdot\text{K)}}{2100\text{ kg/m}^3 \times 950\text{ J/(kg}\cdot\text{K)}} = 1.103 \times 10^{-6}\text{ m}^2/\text{s}$$
    The characteristic conduction diffusion time across slab thickness $L$ ($\text{Fo} = \frac{\alpha \tau}{L^2} = 1$) scales with $L^2$:
    *   **For $L = 12\text{ mm}$ (Arc Lite / Tread)**: $\tau_{12} = \frac{(0.012\text{ m})^2}{1.103 \times 10^{-6}\text{ m}^2/\text{s}} = 130.6\text{ s}$ ($\approx 2.2\text{ min}$).
    *   **For $L = 30\text{ mm}$ (Dome XL)**: $\tau_{30} = \frac{(0.030\text{ m})^2}{1.103 \times 10^{-6}\text{ m}^2/\text{s}} = 816.0\text{ s}$ ($\approx 13.6\text{ min}$).
    Because $30\text{ mm}$ is $2.5\times$ thicker, its conduction lag is $2.5^2 = 6.25\times$ longer. **[Inferred]** Note that Dome XL's published thermometer is **digital, ambient** (measuring dome air/crown temperature), whereas Tread's is **analog, stone**. At $40\text{–}45\text{ min}$, Dome XL's ambient air and top $10\text{ mm}$ of stone reach $500^\circ\text{C}$, but achieving a uniform $\Delta T = 480\text{ K}$ soak through all $19.8\text{–}24.8\text{ kg}$ of cordierite at $40\text{ min}$ would require a $35.5\text{–}44.4\%$ capture fraction. The EU spec sheet figure of **$60\text{ min}$ to $500^\circ\text{C}$** ($\eta_{\text{shaped}} = 23.7\%$, $\eta_{\text{rect}} = 29.6\%$) aligns with the $20\text{–}30\%$ physical capture band and $3\tau_{30} \approx 41\text{ min}$ internal equilibration time. **A builder must use $60\text{ min}$ as the true thermal soak time for a $30\text{ mm}$ hearth.**

2.  **Why Arc Lite and Tread use $12\text{ mm}$**:
    *   **Mass ceiling**: A $30\text{ mm}$ stone in the Tread footprint would weigh $2.5 \times 2.52\text{ kg} = 6.30\text{ kg}$ (shaped) to $7.42\text{ kg}$ (rectangular), adding $\sim 3.8\text{–}4.5\text{ kg}$ and pushing a $13.5\text{ kg}$ portable oven toward $18\text{ kg}$.
    *   **Fast-bake requirement**: With only $1.13\text{–}1.35\text{ MJ}$ needed to soak the $12\text{ mm}$ slab and $\tau_{12} = 2.2\text{ min}$, a $3.4\text{–}3.7\text{ kW}$ burner brings the stone to $500^\circ\text{C}$ in $15\text{–}25\text{ min}$.
    *   **The trade-off (Recovery)**: **[Modelled]** Contact between $500^\circ\text{C}$ cordierite ($e_s = \sqrt{k \rho c_p} \approx 2095\text{ J/(m}^2\cdot\text{K}\cdot\text{s}^{1/2}\text{)}$) and $20^\circ\text{C}$ dough ($e_d \approx 1259\text{ J/(m}^2\cdot\text{K}\cdot\text{s}^{1/2}\text{)}$) produces an initial interfacial temperature:
        $$T_i = \frac{e_s T_s + e_d T_d}{e_s + e_d} = \frac{2095(500) + 1259(20)}{2095 + 1259} = 319.8^\circ\text{C}$$
        During a $90\text{ s}$ Neapolitan bake, the thermal penetration depth into the stone is $\delta \approx 2\sqrt{\alpha t} = 2\sqrt{1.103 \times 10^{-6} \times 90} = 19.9\text{ mm}$. Because $19.9\text{ mm} > 12\text{ mm}$, the cooling wave from a single pizza reaches the bottom of a $12\text{ mm}$ stone before the bake finishes. In a $30\text{ mm}$ stone ($30\text{ mm} > 19.9\text{ mm}$), the lower $10\text{ mm}$ acts as an undisturbed thermal reservoir that recharges the top surface by upward conduction while the next pizza is being stretched. Also, a $12\text{ mm}$ stone lacks the bending section modulus ($Z \propto t^2$, so $30\text{ mm}$ is $6.25\times$ stronger in bending) to survive thermal shock from a localized $700^\circ\text{C}$ hardwood ember bed or accidental log impact.

---

## 4. Insulation Architecture: 1 Layer vs 3 Layers

**[Published]** Gozney specifies "1" insulation layer for Arc Lite and Tread, and "3" layers for Dome XL Gen 2, using non-carcinogenic, water-soluble calcium-magnesium silicate (AES) fibre throughout. Layer thicknesses and skin temperatures are not published.

**[Inferred]** From the published external-to-internal envelope deltas:
*   **Arc Lite / Tread (1-Layer)**: Total side wall budget is $52.5\text{–}54.0\text{ mm}$ average; total vertical budget (roof + floor + $12\text{ mm}$ stone + feet/handles) is $147\text{ mm}$ (Arc Lite) to $170\text{ mm}$ (Tread). Once sheet thicknesses, burner plenum clearance, and base air gap are subtracted, a "1-layer" build accommodates a single $25\text{ mm}$ ($1\text{ in}$) wrap of AES blanket over the dome and a thinner $10\text{–}15\text{ mm}$ insulating mat or air gap beneath the stone.
*   **Dome XL (3-Layer)**: Side wall budget is $111.0\text{ mm}$ per side; vertical budget (body $< 613\text{ mm}$ minus $238\text{ mm}$ internal height) is $\sim 300\text{–}350\text{ mm}$. This accommodates a 3-layer stack—typically two overlapping $25\text{ mm}$ AES fibre blankets ($50\text{ mm}$ total) plus a third layer (either an additional blanket wrap or a rigid structural calcium silicate board / reflective air-gap shield) over the crown, and $50\text{–}75\text{ mm}$ of high-density calcium silicate board under the $30\text{ mm}$ stone.

**[Modelled]** Steady-state 1D conduction through a flat composite wall of AES blanket ($k \approx 0.08\text{ W/(m}\cdot\text{K)}$ mean at $260^\circ\text{C}$, $\rho = 128\text{ kg/m}^3$) with inner core temperature $T_{\text{core}} = 500^\circ\text{C}$, ambient $T_\infty = 25^\circ\text{C}$, and combined natural convection + radiation external heat transfer coefficient $h_{\text{ext}} \approx 12\text{ W/(m}^2\cdot\text{K)}$:
$$q'' = \frac{T_{\text{core}} - T_\infty}{\frac{L_{\text{ins}}}{k} + \frac{1}{h_{\text{ext}}}}, \quad T_{\text{skin}} = T_\infty + \frac{q''}{h_{\text{ext}}}$$

*   **Case A — 1 Layer ($L_{\text{ins}} = 25\text{ mm}$)**:
    *   $R_{\text{ins}} = \frac{0.025}{0.08} = 0.3125\text{ m}^2\cdot\text{K/W}$; $R_{\text{ext}} = \frac{1}{12} = 0.0833\text{ m}^2\cdot\text{K/W}$.
    *   $q'' = \frac{500 - 25}{0.3958} = 1200\text{ W/m}^2$.
    *   $T_{\text{skin}} = 25 + \frac{1200}{12} = 125^\circ\text{C}$.
    *   **Touch Risk**: Exceeds the ISO 13732-1 bare-metal $1\text{ s}$ burn threshold ($\approx 60^\circ\text{C}$) by $65\text{ K}$. **[Published]** This explains why Arc Lite requires a $30\text{ min}$ cooldown before moving, and why Tread uses high-temperature GF20 PPS polymer standoffs/handles on the roof so a user never grabs the painted steel shell directly.
*   **Case B — 3 Layers ($L_{\text{ins}} = 75\text{ mm}$ total equivalent)**:
    *   $R_{\text{ins}} = \frac{0.075}{0.08} = 0.9375\text{ m}^2\cdot\text{K/W}$.
    *   $q'' = \frac{500 - 25}{1.0208} = 465\text{ W/m}^2$ ($61\%$ reduction in conductive heat flux per unit area).
    *   $T_{\text{skin}} = 25 + \frac{465}{12} = 63.8^\circ\text{C}$ (hovering right at the $\approx 60^\circ\text{C}$ short-contact threshold).
*   **Mass & Recovery Impact**:
    *   **Mass**: Covering Arc Lite's $\sim 0.35\text{ m}^2$ dome surface with one $25\text{ mm}$ layer of $128\text{ kg/m}^3$ AES wool adds only $0.35 \times 0.025 \times 128 = 1.12\text{ kg}$. Covering Dome XL's $\sim 1.1\text{ m}^2$ envelope with $75\text{ mm}$ of AES wool and $240\text{ kg/m}^3$ calcium silicate board adds $\sim 12\text{–}15\text{ kg}$ of insulation alone.
    *   **Recovery**: In Arc Lite/Tread, conductive shell losses over $\sim 0.45\text{ m}^2$ at $1200\text{ W/m}^2$ bleed $\sim 540\text{ W}$ ($15\text{–}16\%$ of burner output), and under-stone losses cool the bottom of the $12\text{ mm}$ stone between pizzas. In Dome XL, thick under-hearth board forces nearly all stored heat in the $30\text{ mm}$ stone to conduct upward into the dough rather than downward into the stand.

---

## 5. Mass Delta Analysis: Why Tread ($13.5\text{ kg}$) Outweighs Arc Lite ($12.0\text{ kg}$)

**[Published]** Both ovens take a $12\text{ in}$ pizza, share a $150\text{ mm}$ internal height, use a $12\text{ mm}$ cordierite stone, and have 1 insulation layer, yet Tread weighs $13.5\text{ kg}$ ($14\text{ kg}$ support requirement in US manual) vs Arc Lite's $12.0\text{ kg}$—a $+\mathbf{1.5\text{ kg}}$ ($+12.5\%$) penalty on the portable unit.

**[Inferred & Modelled]** Walking the published geometry and Bill of Materials (BOM) explains where the $1.5\text{ kg}$ goes:

1.  **Taller External Shell & Deeper Internal Floor ($+0.35\text{ to }0.50\text{ kg}$)**:
    *   **[Published]** Tread is $12\text{ mm}$ narrower ($418\text{ mm}$ vs $430\text{ mm}$) but $3\text{ mm}$ deeper externally ($484\text{ mm}$ vs $481\text{ mm}$), $25\text{ mm}$ deeper internally ($380\text{ mm}$ vs $355\text{ mm}$), and $23\text{ mm}$ taller ($320\text{ mm}$ vs $297\text{ mm}$).
    *   **[Modelled]** As calculated in Section 3.2, Tread's $310 \times 380\text{ mm}$ internal floor area ($0.1178\text{ m}^2$) is $2.1\%$ larger than Arc Lite's $325 \times 355\text{ mm}$ floor ($0.1154\text{ m}^2$), adding $\sim 0.05\text{–}0.06\text{ kg}$ to the cordierite stone and inner 304 pan. The deeper 304 inner core and multi-piece outer wrap (SPCC top + SPCC bottom + 304 mid-wrap + extruded aluminium trim) add overlapping flange joints that a simple two-piece shell lacks ($\sim 0.3\text{–}0.4\text{ kg}$).
2.  **Roof-Rack & Carry Handles + Structural Mounts ($+0.50\text{ to }0.70\text{ kg}$)**:
    *   **[Published]** Arc Lite is flagged `Portable: No` (tabletop only) and lacks top handles. Tread is flagged `Portable: Yes` with integrated roof-rack/carry handles and clips moulded in GF20 PPS.
    *   **[Inferred]** For roof-rack tie-down survival under dynamic vehicle braking/cornering loads, the GF20 PPS handles cannot merely screw into thin outer sheet metal; they require internal load-spreading brackets tied to the lower chassis pressing.
3.  **HPDC Aluminium Front Landing with 304 Scratch Guard ($+0.30\text{ to }0.45\text{ kg}$)**:
    *   **[Published]** Tread has a protruding high-pressure die-cast aluminium front landing ledge topped with a 304 stainless steel scratch guard, plus a ceramic-painted 304 mouth arch. Arc Lite has a flush front mouth without an extended armored landing ledge.
4.  **SPCC Dock, Hose Bracket, and Analog Stone Thermometer ($+0.20\text{ to }0.30\text{ kg}$)**:
    *   **[Published]** Tread adds a built-in bimetallic/capillary analog stone thermometer + probe, a GF30 PA hose-management bracket, and an SPCC dock pressing built to survive field transport, whereas Arc Lite omits the thermometer entirely (`Thermometer: none`).

---

## 6. Manufacturing Engineering: Why Stamped Shells + 304 Core + HPDC Landing

### 6.1 Factory Economics (High-Volume Tooling vs Unit Cost)
**[Inferred]** Gozney builds these ovens from four distinct material/process classes rather than a one-piece cast iron/aluminium shell or an all-welded sheet-metal body:

1.  **Outer Shell — Deep-Drawn SPCC (Tread) or Aluminised Steel (Dome XL)**:
    *   *Why not one-piece casting?* Sand or die-casting a dome covering $0.3\text{–}1.1\text{ m}^2$ requires a minimum wall thickness of $3.5\text{–}6.0\text{ mm}$ for molten metal fluidity. At $\rho_{\text{Al}} = 2700\text{ kg/m}^3$, a $4.5\text{ mm}$ cast aluminium shell for Dome XL would weigh $\sim 14\text{ kg}$ by itself (or $\sim 38\text{ kg}$ in cast iron), cost $4\times$ more per cycle, and suffer high porosity/scrap rates prior to ceramic enamelling. Deep-drawing $0.8\text{–}1.2\text{ mm}$ SPCC or aluminised steel in a progressive stamping die takes seconds and keeps shell mass under $35\%$ of a casting.
    *   *Why aluminised steel on Dome XL vs SPCC on Tread?* Dome XL runs up to $60\text{ min}$ preheats and multi-hour wood fires (taking $3\text{ hours}$ to cool). Should condensation or rain enter via the flue gap, Type 1 aluminised steel (hot-dip Al-Si alloy coating) resists both high-temperature oxidation up to $\sim 650^\circ\text{C}$ and wet atmospheric corrosion far better than plain cold-rolled carbon steel (SPCC). *(Note for builders: Aluminised steel is safe because aluminium melts at $660^\circ\text{C}$ without toxic vapor pressure; **galvanised/zinc-coated steel is strictly banned** because zinc boils at $907^\circ\text{C}$ and oxidises/sublimes above $400^\circ\text{C}$, causing metal fume fever.)*
2.  **Inner Core — 304 Stainless Steel**:
    *   **[Modelled]** Inside the combustion chamber, flame impingement reaches $800\text{–}950^\circ\text{C}$. Plain SPCC scales rapidly above $500^\circ\text{C}$, and aluminium melts at $660^\circ\text{C}$. Grade 304 austenitic stainless steel resists intermittent oxidation to $870^\circ\text{C}$ ($925^\circ\text{C}$ continuous).
    *   *Thermal expansion decoupling*: With $\alpha_{304} = 18 \times 10^{-6}\text{ K}^{-1}$ and $\Delta T = 500\text{ K}$, Dome XL's $724\text{ mm}$ wide inner core expands by:
        $$\Delta L = 724\text{ mm} \times 18 \times 10^{-6}\text{ K}^{-1} \times 500\text{ K} = 6.52\text{ mm}$$
        Meanwhile, the $30\text{ mm}$ cordierite stone ($\alpha_{\text{cord}} = 2.8 \times 10^{-6}\text{ K}^{-1}$) expands by only $724 \times 2.8 \times 10^{-6} \times 480 = 0.97\text{ mm}$, and the cool outer shell ($\Delta T \approx 40\text{ K}$) expands by $\sim 0.35\text{ mm}$. A thin stamped 304 inner liner floating inside compliant AES fibre blanket absorbs $6.5\text{ mm}$ of thermal growth via elastic flexing at the mouth slip-joint without cracking welds.
3.  **Front Landing — HPDC Aluminium + 304 Scratch Guard**:
    *   The front mouth transition demands complex 3D compound curvature, rigid boss mounts, and thick heat-sinking ribs where hot flue gas rolls out the arch—features impossible to form in a single sheet stamping without tearing. High-pressure die-cast aluminium provides net-shape 3D stiffness, while a thin stamped 304 plate clipped on top prevents aluminium galling and abrasion from steel pizza peels.

### 6.2 Translation to an Adelaide Workshop (1-Off Build Strategy)
**[Inferred]** You cannot amortise $\$150,000+$ of deep-draw stamping and HPDC dies over a single oven. Instead, use your Fusion 360 / FreeCAD sheet-metal workspace, makerspace/uni press brake, TIG welder, and Gumtree/Marketplace sourcing to invert the factory process:
*   **Inner Core & Outer Shell**: Do not deep-draw a compound sphere. Model a faceted polygonal vault (e.g., 5-bend press-brake octagonal barrel vault with a flat or 3-piece tapered rear cone) in 304 stainless steel ($1.2\text{–}1.5\text{ mm}$ inner core; $0.9\text{–}1.2\text{ mm}$ 304 or mild steel painted outer skin), OR repurpose a decommissioned $50\text{ L}$ 304 stainless beer keg ($363\text{–}395\text{ mm}$ diameter) split longitudinally for a Tread-class chamber. Allow $3\text{–}5\text{ mm}$ slotted slip joints at the front mouth flange so the 304 inner core can grow $\Delta L \approx 3\text{–}7\text{ mm}$ relative to the outer skin without buckling.
*   **Front Landing**: Replace the HPDC aluminium casting with a laser-cut and folded $2.0\text{–}3.0\text{ mm}$ 304 stainless steel apron bolted over a thermal-break gasket of $3\text{ mm}$ AES millboard, with a turned hardwood (spotted gum or jarrah) front handle or peel-rest rail isolated from the hot gas path.

#### Estimated Adelaide Material Costs (2026 AUD — Explicitly Labeled as Estimates)
*   **304 Stainless Sheet ($1.2\text{ mm}$ or $1.5\text{ mm}$)**:
    *   *Retail (e.g., Midway Metals / Edcon Steel, Wingfield/Cavan)*: $\sim\text{AUD }180\text{–}260$ per $1200 \times 2400\text{ mm}$ sheet (laser cutting adds $\sim\text{AUD }80\text{–}150$).
    *   *Second-hand / Offcuts (Gumtree / Facebook Marketplace / local scrap yards)*: $\sim\text{AUD }40\text{–}90$ for catering bench tops, sink cut-outs, or $50\text{ L}$ damaged kegs ($\text{AUD }50\text{–}80$).
*   **Cordierite Hearth Stone**:
    *   *Retail (Pottery supplies / refractory stockists in Adelaide)*: $\sim\text{AUD }50\text{–}85$ for a $12\text{–}15\text{ mm}$ shelf; $\sim\text{AUD }140\text{–}240$ for $25\text{–}30\text{ mm}$ heavy kiln shelves.
    *   *Second-hand (Gumtree / studio kiln cleanouts)*: $\sim\text{AUD }20\text{–}60$ for used $15\text{–}30\text{ mm}$ cordierite kiln shelves (ensure they have never been used for lead-glaze firing!).
*   **Insulation (AES / Superwool Blanket & Calcium Silicate Board)**:
    *   *Retail (Refractory suppliers / industrial insulation, Regency Park/Wingfield)*: $\sim\text{AUD }110\text{–}170$ per full carton of $25\text{ mm}$ AES blanket ($7.3\text{ m}$ roll); $\sim\text{AUD }65\text{–}110$ for a $1000 \times 600 \times 50\text{ mm}$ calcium silicate board.
    *   *Second-hand / Split-roll*: $\sim\text{AUD }25\text{–}50$ per linear metre on Marketplace from other pizza-oven builders selling leftover roll offcuts.
*   **Certified Gas Burner / Valve / Regulator Assembly (AGA / SANZ certified)**:
    *   *Retail*: $\sim\text{AUD }140\text{–}320$ for an AGA-approved complete retro-fit lateral/banjo/ring burner module with integrated FFD valve, piezo igniter, LCC27 hose, and $2.75\text{ kPa}$ regulator.
    *   *Second-hand*: $\sim\text{AUD }50\text{–}120$ for a complete donor AGA-certified portable gas pizza oven or commercial catering salamander burner assembly on Gumtree (pressure-test with soapy water and replace the hose/regulator assembly if aged $>5\text{ years}$).

---

## 7. Safety Architecture, Clearances, Door Rules, and Wind Physics

1.  **Flame Failure Device (FFD) & $30\text{ s}$ Hold Rule**:
    *   **[Published]** Lighting requires pushing and turning the dial and holding for up to $30\text{ s}$ to disengage the FFD.
    *   **[Inferred]** Propane ($C_3H_8$) has a molecular weight of $44.1\text{ g/mol}$ vs dry air at $28.97\text{ g/mol}$ (specific gravity $\approx 1.52$). Unlike natural gas (methane, specific gravity $\approx 0.55$), unburned propane pools inside the oven floor and spills down over the benchtop toward ignition sources. The FFD uses a bimetallic/thermocouple junction placed in the pilot/burner root flame; until heated to $\sim 400\text{–}600^\circ\text{C}$ (generating $\sim 15\text{–}30\text{ mV}$ under load), the spring-loaded电磁 (electromagnetic) safety magnet inside the gas valve drops out and snaps the gas supply shut. Under AS/NZS 5601 / AGA certification, an FFD is mandatory for enclosed/semi-enclosed outdoor gas cooking appliances of this class.
2.  **Prohibition on Covering the Mouth While Lit / Using a Door on Gas**:
    *   **[Published]** Arc Lite and Tread forbid covering the mouth while a flame is lit; Dome XL forbids installing the door while the gas burner is on (door is allowed only on wood embers after naked flames subside).
    *   **[Modelled]** Complete stoichiometric combustion of propane ($C_3H_8 + 5O_2 + 18.8N_2 \rightarrow 3CO_2 + 4H_2O + 18.8N_2$) requires $15.6\text{ kg}$ of air per $1\text{ kg}$ of propane ($\approx 13.0\text{ m}^3$ of air at $20^\circ\text{C}$ per kg of LPG).
        *   At $273.8\text{ g/h}$ (Tread), the burner consumes $0.2738 \times 13.0 = 3.56\text{ m}^3/\text{h}$ ($\approx 1.0\text{ L/s}$) of stoichiometric air; with $50\%$ excess air to prevent soot/CO, it requires $\sim 1.5\text{ L/s}$ of fresh air and discharges $\sim 4.5\text{ L/s}$ of hot expanded exhaust at $600^\circ\text{C}$.
        *   At $784\text{ g/h}$ (Dome XL), hot exhaust flow exceeds $\sim 13\text{ L/s}$.
        *   On flueless ovens (Arc Lite/Tread), the mouth is the *only* exhaust port and secondary-air intake. Blocking it chokes $O_2$, causing immediate rich-burn quenching, massive carbon monoxide ($\text{CO}$) generation, and accumulation of unburned propane/CO mixtures that can deflagrate ("flash-back") when the cover is removed or force flame backward out the dock intake slots. Even on Dome XL (which has a flue), closing the front door with a $10.6\text{ kW}$ gas burner running starves secondary over-hearth air and risks flame-out followed by raw gas pooling if the thermocouple takes $15\text{–}45\text{ s}$ to cool and trip.
3.  **Dock Air Slots ($50\text{ mm}$ Clearance), Wind Orientation, and Dock Fire**:
    *   **[Published]** Do not cover dock slots (CO hazard); maintain $50\text{ mm}$ clear air around the dock; orient the mouth downwind; shut down immediately if fire appears out of the dock.
    *   **[Inferred]** The lateral burner relies on a Venturi mixer fed by the gas injector jet ($0.85\text{–}1.86\text{ mm}$). Primary air is entrained through the dock slots by jet momentum. Blocking the dock slots cuts primary aeration, shifting the flame from a controlled yellow/orange rolling diffusion/partially-premixed sheet into a heavy sooting, high-CO regime. Conversely, if strong wind blows *into* the front mouth ($P_{\text{stag}} = \frac{1}{2}\rho v^2$), chamber static pressure rises above the stagnation pressure of the low-pressure LPG Venturi tube, reversing flow and driving live flame backward through the mixer tube and out the dock slots—melting the GF20 PP / GF30 PA polymer dock components and heating the flexible LPG hose toward burst failure.
4.  **Combustible Clearances ($0.3\text{ m}$ Sides/Rear, $1.0\text{ m}$ Front) & Cooling Intervals ($30\text{ min}$ vs $3\text{ h}$)**:
    *   **[Published]** All three ovens mandate $0.3\text{ m}$ ($300\text{ mm}$) back/side clearance and $1.0\text{ m}$ ($1000\text{ mm}$) front clearance from combustible construction, and forbid operation on or under combustible structures. Cooling time before moving is $30\text{ min}$ (Arc Lite) vs $3\text{ hours}$ (Dome XL).
    *   **[Modelled]** At $T_{\text{core}} = 500^\circ\text{C}$ ($773\text{ K}$), blackbody emissive power at the mouth plane is $E_b = \sigma T^4 = 5.670 \times 10^{-8} \times (773)^4 = 20.25\text{ kW/m}^2$. For Dome XL's mouth ($0.470 \times 0.140\text{ m} = 0.0658\text{ m}^2$), radiant power streaming straight forward is $\sim 1.33\text{ kW}$ on top of the convective buoyant plume spilling up from the arch. Thus front clearance must be $3.3\times$ larger than side clearance ($1.0\text{ m}$ vs $0.3\text{ m}$). Regarding cooldown: Dome XL stores $9.0\text{–}11.3\text{ MJ}$ in its $30\text{ mm}$ stone wrapped inside a 3-layer ($R \approx 0.94\text{ m}^2\cdot\text{K/W}$) enclosure, giving a thermal RC time constant roughly $6\times$ longer than Arc Lite's $1.1\text{–}1.3\text{ MJ}$ stone in a 1-layer shell ($180\text{ min}$ vs $30\text{ min}$).

---

## 8. Comparative Engineering Tables

### Table 1: Master Published Specifications (18 October 2026 Source Pack)

| Parameter | Gozney Arc Lite (`GOZ-3102`) | Gozney Tread (`GOZ-1893`) | Gozney Dome XL Gen 2 (`GOZ-2509`) | Conflict Resolution / Builder Guidance |
| :--- | :--- | :--- | :--- | :--- |
| **AU Retail Price** | AUD 649 | AUD 899 | AUD 3,999 | Context: Arc AUD 1,199; Arc XL AUD 1,499; Dome Gen 2 AUD 2,999. |
| **US Retail Price** | USD 399.99 | USD 499.99 | USD 2,799.99 | — |
| **Supported Fuel** | Propane (LPG) only | Propane (LPG) only | Propane + Wood + Charcoal | Hardwood: kiln-dried, $10\text{–}20\%$ moisture ($16\%$ opt). |
| **Oven Mass (Unpacked)** | $12.0\text{ kg}$ ($26.4\text{ lb}$) | $13.5\text{ kg}$ ($29.7\text{ lb}$) / $14\text{ kg}$ (US manual) | $73.0\text{ kg}$ ($160.9\text{ lb}$) | Use $14.0\text{ kg}$ for Tread stand design. |
| **Packed Mass** | $14.8\text{ kg}$ | $16.0\text{ kg}$ | $80.8\text{ kg}$ | — |
| **External $W \times D \times H$** | $430 \times 481 \times 297\text{ mm}$ | $418 \times 484 \times 320\text{ mm}$ ($125\text{ mm}$ callout) | $946 \times 697 \times 997\text{ mm}$ (incl. flue) | Dome XL carton H is $613\text{ mm}$ (flue ships detached). |
| **Internal $W \times D \times H$** | $325 \times 355 \times 150\text{ mm}$ | $310 \times 380 \times 150\text{ mm}$ | $724 \times 543 \times 238\text{ mm}$ | — |
| **Mouth $W \times H$** | $325 \times 85\text{ mm}$ | $310 \times 85\text{ mm}$ (spec) / $315\text{ mm}$ ($12.4\text{ in}$ tool) | $470 \times 140\text{ mm}$ | Use $310\text{ mm}$ as the Tread spec-sheet mouth width. |
| **Pizza Capacity** | $12\text{ in}$ ($305\text{ mm}$) | $12\text{ in}$ ($305\text{ mm}$) | $18\text{ in}$ ($457\text{ mm}$) | — |
| **Max Temp** | $950+^\circ\text{F}$ ($500^\circ\text{C}$) | $500^\circ\text{C}$ ($950+^\circ\text{F}$) | $950+^\circ\text{F}$ ($500^\circ\text{C}$) | — |
| **Heat-Up Time** | $20\text{–}30\text{ min}$ | $15\text{–}20\text{ min}$ | $40\text{–}45\text{ min}$ (US tool) / $60\text{ min}$ to $500^\circ\text{C}$ (EU spec) | Use $60\text{ min}$ for Dome XL full $30\text{ mm}$ stone soak ($15\text{ m}\to 300^\circ\text{C}$, $30\text{ m}\to 400^\circ\text{C}$). |
| **Cordierite Stone** | $12\text{ mm}$, removable | $12\text{ mm}$, removable | $30\text{ mm}$, removable | — |
| **Insulation Layers & Type** | 1 layer, water-soluble AES fibre | 1 layer, Ca-Mg silicate fibre | 3 layers, Ca-Mg silicate fibre | — |
| **Burner Power** | $3.4\text{ kW}$ ($11,687\text{ BTU/h}$) | $3.7\text{ kW}$ ($12,621\text{ BTU/h}$ tool; $12,500\text{ BTU/h}$ US) | $10.6\text{ kW}$ ($36,100\text{ BTU/h}$ tool; $36,850\text{ BTU/h}$ US) | Design to kW nameplates: $3.4\text{ kW}$, $3.7\text{ kW}$, $10.6\text{ kW}$. |
| **Published Gas Flow** | $252\text{ g/h}$ (UK/EU plate) / $273.8\text{ g/h}$ (US tool) | $273.8\text{ g/h}$ (spec) / $273\text{ g/h}$ (tool) | $784\text{ g/h}$ (EU manual) / $0.75\text{ kg/h}$ (tool & spec) | Use $252\text{ g/h}$ (Arc Lite), $273.8\text{ g/h}$ (Tread), $784\text{ g/h}$ (Dome XL). |
| **Gas Injector Orifice** | $0.95\text{ mm}$ (US $11\text{ in WC}$); $0.85/0.90/0.95\text{ mm}$ (EU) | $0.98\text{ mm}$ (US $11\text{ in WC}$) | $1.86\text{ mm}$ (US $11\text{ in WC}$) | Buy factory-matched certified burner + jet assembly. |
| **Thermometer** | None | Analog (stone probe) | Digital (ambient + 2 meat probes, USB-C) | — |
| **Flue & Door** | No flue, no door | No flue, no door | Removable flue ($3\text{ mm}$ rain-guard gap) + ember door | Never use a door while any gas burner is lit. |
| **Approvals Listed** | ANSI Z21.58 / CSA 1.6; UK/EU I3P/I3+ | CE / UKCA / UKNI / ETL / CSA / GM | CE / ETL / AGA / SANZ | AGA & SANZ are the AU/NZ gas marks on Dome XL. |
| **Clearances & Cool Time** | $0.3\text{ m}$ sides/back, $1.0\text{ m}$ front; $30\text{ min}$ cool | $0.3\text{ m}$ sides/back, $1.0\text{ m}$ front, $50\text{ mm}$ dock | $0.3\text{ m}$ sides/back, $1.0\text{ m}$ front; $3\text{ h}$ cool | Outdoor only; never under/on combustible structures. |

---

### Table 2: Inferred and Modelled Engineering Ratios

| Derived Engineering Metric [Inferred / Modelled] | Gozney Arc Lite | Gozney Tread | Gozney Dome XL Gen 2 | Engineering Significance |
| :--- | :--- | :--- | :--- | :--- |
| **Mouth-to-Internal Width Ratio ($W_{\text{mouth}} / W_{\text{int}}$)** | $1.000$ ($100.0\%$) | $1.000$ ($100.0\%$) | $0.649$ ($64.9\%$) | $<0.70$ creates front cheeks needed to shelter a wood fire. |
| **Mouth-to-Apex Height Ratio ($H_{\text{mouth}} / H_{\text{int}}$)** | $0.567$ ($56.7\%$) | $0.567$ ($56.7\%$) | $0.588$ ($58.8\%$) | Slightly tighter than the $0.63$ Neapolitan rule to trap dome gas. |
| **Average Side-Wall Envelope Budget $(W_{\text{ext}} - W_{\text{int}})/2$** | $52.5\text{ mm}$ | $54.0\text{ mm}$ | $111.0\text{ mm}$ | Dome XL provides $>2\times$ wall thickness for 3-layer insulation. |
| **Depth Envelope Budget ($D_{\text{ext}} - D_{\text{int}}$)** | $126.0\text{ mm}$ | $104.0\text{ mm}$ | $154.0\text{ mm}$ | Shared across rear insulation, burner dock, and front landing. |
| **Bounding Hearth Area ($W_{\text{int}} \times D_{\text{int}}$)** | $0.1154\text{ m}^2$ | $0.1178\text{ m}^2$ | $0.3931\text{ m}^2$ | Dome XL has $3.34\times$ to $3.41\times$ the hearth area of the $12\text{ in}$ ovens. |
| **Power Density on Hearth ($\dot{Q}_{\text{in}} / A_{\text{rect}}$)** | $29.46\text{ kW/m}^2$ | $31.41\text{ kW/m}^2$ | $26.97\text{ kW/m}^2$ | All three sit tightly inside the $27\text{–}31.5\text{ kW/m}^2$ hearth loading band! |
| **Power Density on Chamber Box Vol ($\dot{Q}_{\text{in}} / V_{\text{int, box}}$)** | $196.4\text{ kW/m}^3$ | $209.4\text{ kW/m}^3$ | $113.3\text{ kW/m}^3$ | Tread has the highest volumetric firing intensity ($15\text{–}20\text{ min}$ sprint). |
| **Firing Intensity per Mouth Area ($\dot{Q}_{\text{in}} / A_{\text{mouth, rect}}$)** | $123.1\text{ kW/m}^2$ | $140.4\text{ kW/m}^2$ | $161.1\text{ kW/m}^2$ | Dome XL supplements its narrower mouth with a top flue. |
| **Stone Mass ($f=1.00$ rect / $f=0.85$ or $0.80$ shaped)** | $2.91\text{ kg}$ / $2.47\text{ kg}$ | $2.97\text{ kg}$ / $2.52\text{ kg}$ | $24.77\text{ kg}$ / $19.81\text{ kg}$ | Stone is $\sim 20\text{–}24\%$ of total oven mass on Arc Lite/Tread; $\sim 27\text{–}34\%$ on Dome XL. |
| **Stone Thermal Mass Share ($m_{\text{stone, shaped}} / m_{\text{oven}}$)** | $20.6\%$ | $18.7\%$ | $27.1\%$ | Dome XL dedicates the highest fraction of total mass to hearth thermal ballast. |
| **Stone Conduction Time Constant ($\tau = L^2/\alpha$)** | $130.6\text{ s}$ ($2.2\text{ min}$) | $130.6\text{ s}$ ($2.2\text{ min}$) | $816.0\text{ s}$ ($13.6\text{ min}$) | Explains why $30\text{ mm}$ stone requires $60\text{ min}$ to soak fully. |
| **Stone Stored Energy ($\Delta T = 480\text{ K}$, shaped / rect)** | $1.13\text{ MJ}$ / $1.33\text{ MJ}$ | $1.15\text{ MJ}$ / $1.35\text{ MJ}$ | $9.04\text{ MJ}$ / $11.29\text{ MJ}$ | Dome XL stores $8.0\times$ more hearth thermal energy than Arc Lite/Tread. |
| **Heat-Up Capture Fraction ($\eta_{\text{shaped}}$ at max published $t_{\text{heat}}$)** | $18.4\%$ (at $30\text{ min}$) | $25.9\%$ (at $20\text{ min}$) | $23.7\%$ (at $60\text{ min}$) | Confirms $20\text{–}26\%$ net stone energy capture at full thermal soak. |

---

## 9. Adelaide Builder's Synthesis: Five Decisions to Copy, Five to Reject

### Five Engineering Decisions to Copy
1.  **Target the $27\text{–}31\text{ kW/m}^2$ Hearth Power Density Band**: **[Modelled]** Across all three ovens, burner nameplate power divided by internal floor area stays remarkably constant ($27.0\text{ to }31.4\text{ kW/m}^2$). When selecting a certified off-the-shelf LPG burner assembly, size your hearth floor area $A_{\text{floor}}$ directly to the burner's kW rating ($\dot{Q} \approx 29\text{ kW/m}^2 \times A_{\text{floor}}$).
2.  **Keep Vertical Mouth-to-Apex Ratio Near $0.57\text{–}0.59$**: **[Modelled]** Dropping the mouth arch height to $57\text{–}59\%$ of the inner dome height (slightly tighter than the $63\%$ brick-oven rule of thumb) creates a deep upper convective ceiling pocket ($65\text{–}98\text{ mm}$ deep) that forces the lateral gas flame to roll across the dome before spilling out the mouth.
3.  **Match Mouth Width Ratio to Fuel Choice ($1.00$ for Compact Gas-Only, $\le 0.65$ + Top Flue for Wood)**: **[Inferred]** If building a compact $12\text{ in}$ gas-only oven, a full-width mouth ($W_{\text{mouth}}/W_{\text{int}} = 1.0$) maximizes peel manoeuvrability and eliminates the need for a chimney flue. If you want to burn hardwood, you must widen the chamber by at least $220\text{–}260\text{ mm}$ beyond the pizza diameter, restrict the mouth width to $\le 65\%$ so the front cheeks shelter the ember bed, add an under-bed air grate, and install a top flue outside the door plane.
4.  **Use a $25\text{–}30\text{ mm}$ Cordierite Hearth Backed by Rigid Calcium Silicate Board (Unless Building an Ultra-Light Portable)**: **[Modelled]** Because the $90\text{ s}$ thermal penetration depth in cordierite is $\approx 20\text{ mm}$, a $25\text{–}30\text{ mm}$ kiln shelf sitting on $50\text{ mm}$ of calcium silicate board ($k \approx 0.065\text{ W/(m}\cdot\text{K)}$) eliminates recovery lag between back-to-back pizzas and resists wood-fire thermal shock.
5.  **Float the 304 Inner Core Inside AES Blanket with Slip-Jointed Mouth Flanges**: **[Modelled]** A 304 stainless inner liner grows $\sim 9\text{ mm}$ per metre of width at $500^\circ\text{C}$. Wrapping it in non-carcinogenic water-soluble AES blanket (Superwool class) and connecting it to the outer skin via slotted/sliding mechanical tabs at the front mouth prevents thermal-fatigue weld cracking.

### Five Commercial Decisions NOT to Copy
1.  **Do Not Use a $12\text{ mm}$ Stone on a Stationary Backyard Oven**: **[Inferred]** Gozney uses $12\text{ mm}$ stones on Arc Lite and Tread strictly to keep total oven weight at $12.0\text{–}13.5\text{ kg}$ for parcel shipping and roof-rack portability, and to advertise a $15\text{–}20\text{ min}$ heat-up time. On a home patio cart where an extra $4\text{ kg}$ does not matter, a $12\text{ mm}$ stone saturates its cooling wave in a single $90\text{ s}$ bake ($\delta \approx 20\text{ mm} > 12\text{ mm}$) and requires re-soaking between pizzas.
2.  **Do Not Limit Yourself to a Single $25\text{ mm}$ Insulation Layer**: **[Modelled]** A single layer is used on Arc Lite and Tread to hit the AUD $649\text{–}899$ price point and a $\sim 420\text{ mm}$ external width envelope. Adding a second $25\text{ mm}$ wrap of AES blanket costs less than AUD $40$ and $1.2\text{ kg}$ in a home build while cutting shell heat loss in half and dropping outer skin temperatures toward the $60^\circ\text{C}$ touch threshold.
3.  **Do Not Attempt Compound-Curved Sheet Metal Stampings or Die-Cast Aluminium Landings**: **[Inferred]** Stamped SPCC/aluminised domes and HPDC aluminium landings exist only because high-volume press and die-casting tooling pays for itself over tens of thousands of units. In an Adelaide makerspace, a press-brake-folded faceted 304 stainless dome with a folded $2\text{–}3\text{ mm}$ 304 sheet landing performs identically at zero tooling cost.
4.  **Do Not Rely Solely on an Ambient Air Thermometer (or Omit the Thermometer Entirely)**: **[Inferred]** Arc Lite omits a thermometer to hit a lower price tier (protecting the AUD $1,199$ Arc margin), and Dome XL's digital ambient gauge reads $500^\circ\text{C}$ air temperature $15\text{–}20\text{ min}$ before its $30\text{ mm}$ stone is actually soaked through ($40\text{–}45\text{ min}$ air vs $60\text{ min}$ stone). Drill a blind horizontal hole or slot into the mid-plane of your cordierite stone for a K-type thermocouple, paired with a handheld infrared pyrometer aimed at the stone centre.
5.  **Do Not Mould Custom Glass-Filled Polymer Docks (GF20 PP / GF30 PA) Close to the Intake Path**: **[Inferred]** Commercial units use injection-moulded glass-filled nylon/polypropylene docks for rapid assembly line snap-fitting and thermal isolation of the control knob. If wind blows into the mouth and causes a dock flashback, polymer docks melt. Fabricate your burner housing and air-intake shroud out of folded stainless or mild steel sheet with generous $50\text{ mm}+$ louvered wind baffles, and isolate the bought-in certified gas valve shaft with a simple sheet-metal heat shield and a turned hardwood or anodised aluminium knob.
