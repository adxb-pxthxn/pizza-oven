### Epistemic Key

Every technical claim, dimension, and calculation in this study is labelled by source class:
*   **[Published]**: Appears directly in the 18 October 2026 Gozney source pack.
*   **[Inferred]**: Deduced from published geometry, material designations, shipping cartons, or standard manufacturing practice. The underlying assumption is named.
*   **[Modelled]**: Calculated from first-principles heat transfer, thermodynamics, or mechanics of materials using the repository constants or stated textbook properties.
*   **ESTIMATE**: All Adelaide material prices are 2026 AUD market estimates for retail and second-hand sourcing (Gumtree / Facebook Marketplace SA).

---

## 1. Reference Baselines and Source Reconciliations

Before selecting substitute materials for an Adelaide shop build, the published benchmarks and data conflicts across the three reference ovens must be resolved into single design values.

| Parameter | Arc Lite (GOZ-3102) | Tread (GOZ-1893) | Dome XL Gen 2 (GOZ-2509) |
| :--- | :--- | :--- | :--- |
| **AU / US Retail Price [Published]** | AUD 649 / USD 399.99 | AUD 899 / USD 499.99 | AUD 3,999 / USD 2,799.99 |
| **External W × D × H [Published]** | $430 \times 481 \times 297\text{ mm}$ | $418 \times 484 \times 320\text{ mm}$ | $946 \times 697 \times 997\text{ mm}$ (inc. flue) |
| **Internal W × D × H [Published]** | $325 \times 355 \times 150\text{ mm}$ | $310 \times 380 \times 150\text{ mm}$ | $724 \times 543 \times 238\text{ mm}$ |
| **Mouth W × H [Published]** | $325 \times 85\text{ mm}$ | $310 \times 85\text{ mm}$ (spec) / $315\text{ mm}$ (tool) | $470 \times 140\text{ mm}$ |
| **Mouth-to-Apex Ratio [Modelled]** | $85 / 150 = 0.567$ | $85 / 150 = 0.567$ | $140 / 238 = 0.588$ |
| **Oven Mass [Published]** | $12.0\text{ kg}$ ($26.4\text{ lb}$); $14.8\text{ kg}$ packed | $13.5\text{ kg}$ ($29.7\text{ lb}$); $14\text{ kg}$ manual; $16\text{ kg}$ packed | $73.0\text{ kg}$ ($160.9\text{ lb}$); $80.8\text{ kg}$ packed |
| **Hearth Stone [Published]** | $12\text{ mm}$ cordierite, removable | $12\text{ mm}$ cordierite, removable | $30\text{ mm}$ cordierite, removable |
| **Insulation [Published]** | 1 layer, water-soluble fibre | 1 layer, Ca-Mg silicate fibre (AES) | 3 layers, Ca-Mg silicate fibre (AES) |
| **Nameplate Power [Published]** | $3.4\text{ kW}$ ($11,687\text{ BTU/h}$) | $3.7\text{ kW}$ ($12,621\text{ BTU/h}$ tool / $12,500$ manual) | $10.6\text{ kW}$ ($36,100\text{ BTU/h}$ tool / $36,850$ manual) |
| **Injector Jet (US 11" WC) [Published]**| $0.95\text{ mm}$ (EU: $0.85/0.90/0.95\text{ mm}$) | $0.98\text{ mm}$ | $1.86\text{ mm}$ |

### Resolution of Published Data Conflicts

1.  **Gas Power vs. Mass Flow Rate**:
    *   *Arc Lite*: **[Published]** The UK/EU data plate states $3.4\text{ kW}$ ($252\text{ g/h}$), whereas the US comparison tool states $3.4\text{ kW}$ and $273.8\text{ g/h}$. **[Modelled]** Using propane $\text{LHV} = 46.4\text{ MJ/kg}$ ($46.4\text{ kJ/g}$):
        $$\dot{Q}_{252} = \frac{252\text{ g/h}}{3600\text{ s/h}} \times 46.4\text{ kJ/g} = 3.25\text{ kW}\text{ (LHV)}$$
        At Gross Calorific Value ($\text{HHV} \approx 50.0\text{ MJ/kg}$, standard EN 437 appliance test basis), $252\text{ g/h}$ equals $\frac{252}{3600} \times 50.0 = 3.50\text{ kW}$. **[Inferred]** The $273.8\text{ g/h}$ figure on the US comparison tool is a copy-paste error from the Tread column. **Builder Rule**: Use $3.4\text{ kW}$ ($252\text{ g/h}$) for the Arc Lite class.
    *   *Tread*: **[Published]** The spec sheet states $3.7\text{ kW}$ and $273.8\text{ g/h}$. The US comparison tool lists $273\text{ g/h}$ and $12,621\text{ BTU/h}$ ($3.70\text{ kW}$), while the US manual lists $12,500\text{ BTU/h}$ ($3.66\text{ kW}$). **[Modelled]** At $\text{LHV} = 46.4\text{ MJ/kg}$, $273.8\text{ g/h}$ yields:
        $$\dot{Q}_{273.8,\text{LHV}} = \frac{273.8}{3600} \times 46.4 = 3.53\text{ kW}$$
        Conversely, producing $3.7\text{ kW}$ on an LHV basis requires $\frac{3.7}{46.4} \times 3600 = 287.1\text{ g/h}$. On a Gross CV basis ($50.0\text{ MJ/kg}$), $273.8\text{ g/h}$ equals $3.80\text{ kW}$. **Builder Rule**: Treat $3.7\text{ kW}$ as the nameplate heat input and $273.8\text{ g/h}$ as the nominal mass flow.
    *   *Dome XL Gen 2*: **[Published]** The EU manual states $10.6\text{ kW}$ ($784\text{ g/h}$). The comparison tool states $0.75\text{ kg/h}$ and $36,100\text{ BTU/h}$ ($10.58\text{ kW}$). The spec sheet prints "$10.6\text{ kWh} \mid 0.75\text{ kg/h}$" (where $\text{kWh}$ is a dimensional typo for $\text{kW}$). The US manual states $36,850\text{ BTU/h}$ ($10.80\text{ kW}$). **[Modelled]** At $\text{LHV} = 46.4\text{ MJ/kg}$:
        $$\dot{Q}_{750} = \frac{750\text{ g/h}}{3600\text{ s/h}} \times 46.4\text{ kJ/g} = 9.67\text{ kW}$$
        $$\dot{Q}_{784} = \frac{784\text{ g/h}}{3600\text{ s/h}} \times 46.4\text{ kJ/g} = 10.11\text{ kW}$$
        At Gross CV ($50.0\text{ MJ/kg}$), $784\text{ g/h}$ is $10.89\text{ kW}$ and $750\text{ g/h}$ is $10.42\text{ kW}$. **Builder Rule**: Design burner heat release and ventilation around $10.6\text{ kW}$ and size LPG bottle vaporisation for $784\text{ g/h}$ (a single $9\text{ kg}$ bottle in cold Adelaide winter weather will ice up at $784\text{ g/h}$ after long runs; manifold two $9\text{ kg}$ bottles or use a $15\text{–}45\text{ kg}$ cylinder).
2.  **Tread Mouth Width and Drawing Callout**:
    *   **[Published]** The spec sheet gives a $310 \times 85\text{ mm}$ mouth ($12.2\text{ in}$) and $310\text{ mm}$ internal width. The comparison tool writes $12.4\text{ in}$ ($315\text{ mm}$). **Builder Rule**: Use $310\text{ mm}$; the mouth cannot be wider than the $310\text{ mm}$ internal firebox without a flared arch casting.
    *   **[Published]** A Tread drawing callout shows $125\text{ mm}$ without a label. **[Inferred]** Assuming standard orthographic callouts, $125\text{ mm}$ represents either the side burner dock projection or the lower cradle/leg height. Do not use $125\text{ mm}$ to constrain the main firebox envelope.
3.  **Dome XL Gen 2 Carton Height, $219\text{ mm}$ Callout, and Heat-up Time**:
    *   **[Published]** Overall height is $997\text{ mm}$ including the flue, but the shipping carton is $1077 \times 815 \times 613\text{ mm}$ and the flue components are packed loose in the box. **[Inferred]** The main oven body height without the flue is at most $613\text{ mm}$ (likely $550\text{–}580\text{ mm}$ allowing for packaging foam).
    *   **[Published]** The spec sheet drawing includes an unlabelled $219\text{ mm}$ callout alongside $543\text{ mm}$ (internal depth), $997\text{ mm}$, $697\text{ mm}$, and $946\text{ mm}$. **[Inferred]** Hypothesis: $219\text{ mm}$ is either the height of the lower dock/pedestal base up to the hearth plane, or the length of the removable cylindrical flue pipe section above the collar.
    *   **[Published]** The EU spec sheet states 60 min to $500\text{ }^\circ\text{C}$ (15 min to $300\text{ }^\circ\text{C}$, 30 min to $400\text{ }^\circ\text{C}$), while the US comparison tool states 40–45 min. **Builder Rule**: Use 60 minutes. Thermally soaking a $30\text{ mm}$ thick cordierite slab through its full depth requires the longer window.
4.  **Mouth-to-Apex Ratio**:
    *   **[Modelled]** Traditional brick Neapolitan ovens use a mouth-to-vault-apex ratio of $0.63$. The published Gozney geometries yield $85 / 150 = 0.567$ (Arc Lite and Tread) and $140 / 238 = 0.588$ (Dome XL Gen 2). **[Inferred]** Lowering the ratio from $0.63$ to $0.57\text{–}0.59$ increases the depth of the hot buoyancy pocket trapped under the ceiling, compensating for the lack of heavy refractory thermal mass in sheet-metal ovens.

---

## 2. Alternative Materials Evaluation for an Adelaide Home Builder

**[Published]** Gozney constructs its commercial ovens from deep-drawn SPCC or aluminised steel outer pressings, 304 stainless steel inner cores and mid-wraps, high-pressure die-cast (HPDC) aluminium landings and trims, alkaline-earth silicate (AES) fibre blankets, cordierite stones, and glass-filled polymers (GF20 PPS, GF30 PA, GF30 PP, GF20 PP) for handles and docks.

Because an individual builder in Adelaide will not pay for deep-drawing stamping dies or HPDC moulds, the table and detailed engineering profiles below evaluate nine shop-buildable alternatives across all four functional zones.

### Summary Matrix of Alternative Materials

| Material | Oven Zone | Max Cont. Temp [Inferred] | Food Contact Verdict | Adelaide Retail Band (ESTIMATE) | Adelaide 2nd-Hand Band (ESTIMATE) | Shop Difficulty | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense High-Alumina Castable** | Inner vault | $1300\text{–}1600\text{ }^\circ\text{C}$ | Safe once cured (no floor abrasion; use cordierite floor) | AUD $65–$110 per $25\text{ kg}$ bag | AUD $20–$40 per bag (surplus) | Medium (formwork & vibration) | Steam spalling / explosive cracking on rapid first firing |
| **Perlite or Vermiculite Concrete** | Insulation layer | $900\text{–}1100\text{ }^\circ\text{C}$ | **No** (friable, dusty, high porosity) | AUD $45–$75 per $100\text{ L}$ bag + AUD $60–$85 CA cement | AUD $15–$30 (leftover bags) | Easy (hand-packed over form) | Structural crushing; moisture retention causing steam spalling |
| **RCF vs. AES Fibre Blanket** | Insulation layer | $1260\text{ }^\circ\text{C}$ (RCF) / $1200\text{ }^\circ\text{C}$ (AES) | **No** (must be sealed out of gas/food path) | AUD $110–$180 per carton ($7.3\text{ m} \times 610\text{ mm} \times 25\text{ mm}$) | AUD $15–$35 per offcut metre | Easy (utility knife & foil tape) | Friable fibre shedding; mechanical compression under load |
| **Calcium Silicate Board** | Rigid under-hearth / structural insulation | $1000\text{ }^\circ\text{C}$ | **No** (chalky dust; non-structural for abrasion) | AUD $120–$210 per sheet ($1200 \times 600 \times 25\text{–}50\text{ mm}$) | AUD $30–$70 per offcut panel | Easy (woodworking saws + P2/P3 mask) | Moisture absorption (hygroscopic); brittle fracture under point loads |
| **Cordierite Shelf vs. Dense Firebrick** | Hearth floor | $1250\text{ }^\circ\text{C}$ (Cord.) / $1300\text{ }^\circ\text{C}$ (Brick) | **Yes** (purpose-made hearth surface) | Cordierite: AUD $70–$160. Firebrick: AUD $5.50–$9.00 each | Kiln shelves: AUD $25–$60. Bricks: AUD $1–$3 each | Easy (wet diamond blade) | Thermal shock fracture (if wet) or mechanical drop |
| **Mild Steel / Cast Iron Plate** | Hearth floor (450–500 °C) | $550\text{ }^\circ\text{C}$ (scaling limit) | **Fail at 450–500 °C** (burns dough instantly) | AUD $60–$140 ($6\text{–}10\text{ mm}$ laser-cut plate) | AUD $15–$40 (scrap yard offcut) | Easy | Instant pyrolytic charring of dough base due to excessive effusivity |
| **Recycled LPG Bottle / Beer Keg** | Inner vault | $450\text{ }^\circ\text{C}$ (LPG mild steel) / $800\text{ }^\circ\text{C}$ (304 SS keg) | Safe if 304 SS (Keg) or stripped/descaled mild steel | New 50 L keg: AUD $220–$300 | Decommissioned keg: AUD $40–$80. Expired 9/45 kg bottle: AUD $0–$25 | Medium (strict purging, cold cutting, TIG) | Residual gas explosion during cutting; thermal buckling & differential expansion |
| **Spun or Beaten Aluminium** | **Outer cold shell ONLY** | $150\text{ }^\circ\text{C}$ structural limit ($660\text{ }^\circ\text{C}$ melt) | **No** (outer skin only) | AUD $90–$180 ($1.6\text{–}3.0\text{ mm}$ 5005/5052 sheet) | AUD $25–$60 (scrap sheet / road sign blanks) | High (annealing, wheeling, hammerforming) | Loss of temper/yield strength $>150\text{ }^\circ\text{C}$; local melting near mouth |
| **Composites (GRP / Cement Sheet)** | Outer cold shell | $80\text{ }^\circ\text{C}$ (GRP) / $150\text{ }^\circ\text{C}$ (Cement sheet) | **No** (toxic styrene/smoke or steam spalling) | AUD $40–$90 per panel/kit | AUD $10–$25 (building leftovers) | Easy–Medium | GRP: resin pyrolysis & toxic fire. Cement sheet: explosive steam delamination |
| **Microporous Silica Board** | Ultra-thin insulation layer | $1000\text{ }^\circ\text{C}$ | **No** (encapsulated in foil/glass cloth) | AUD $220–$420 per panel ($1000 \times 600 \times 10\text{–}25\text{ mm}$) | Rare second-hand (AUD $80–$150 if found) | Easy (cut and seal edges with high-temp tape) | Crushing under clamping loads; irreversible sintering above $1000\text{ }^\circ\text{C}$ |

---

### Detailed Material Profiles and Engineering Proofs

#### 2.1 Cast Refractory (High-Alumina Castable) Inner Dome
*   **Where it sits**: Inner vault (replacing the 304 stainless steel sheet inner core).
*   **Continuous Temperature**: **[Inferred]** $1300\text{ }^\circ\text{C}$ to $1600\text{ }^\circ\text{C}$ depending on alumina content ($40\text{–}60\%\text{ Al}_2\text{O}_3$, calcium aluminate hydraulic binder).
*   **Food-Contact Verdict**: Safe for radiant and convective exposure above food. Do not bake directly on a raw castable floor because aggregate pull-out leaves grit in the dough; pair a castable dome with a smooth cordierite or pressed firebrick floor.
*   **Adelaide Sourcing**: Industrial refractory suppliers in Wingfield, Regency Park, or Gepps Cross (e.g., TechRentals/refractory stockists, local foundry suppliers, or pottery kiln suppliers in Edwardstown).
    *   *Retail*: **ESTIMATE** AUD $65–$110 per $25\text{ kg}$ bag (a Tread/Arc-sized dome takes $18\text{–}25\text{ kg}$ at $20\text{–}25\text{ mm}$ wall thickness; a Dome XL class takes $75\text{–}100\text{ kg}$).
    *   *Second-hand*: **ESTIMATE** AUD $20–$40 per unopened surplus bag on Gumtree/Marketplace (check manufacture date; hydraulic shelf life is 6–12 months in dry storage).
*   **Difficulty**: Medium. Requires building an inner male mould (styrofoam carved on a CNC router, or an inflatable exercise ball/plywood ribs) and an outer female mould, plus mechanical vibration during pouring because low-water castables are thixotropic. Adding $1.5\text{–}2.0\text{ wt}\%$ of $25\text{ mm}$ 304/310 stainless steel needles increases flexural toughness and prevents crack propagation.
*   **Failure Mode**: Explosive steam spalling during the first firing. Hydraulic calcium aluminate binders lock free and chemically bound water inside fine pores. If heated above $100\text{ }^\circ\text{C}$ before free water escapes, internal steam pressure exceeds the tensile strength of the green ceramic ($\sim 2\text{–}4\text{ MPa}$), blowing chunks off the ceiling. Cure covered at ambient for 48 hours, air-dry for 5–7 days, then step-cure at $80\text{ }^\circ\text{C}$, $150\text{ }^\circ\text{C}$, and $300\text{ }^\circ\text{C}$ for 2 hours each before full firing.

#### 2.2 Perlite or Vermiculite Concrete
*   **Where it sits**: Bulk thermal insulation over a structural inner dome or under a structural hearth sub-plate. Never use as an inner dome face or cooking floor.
*   **Continuous Temperature**: **[Inferred]** $900\text{–}1100\text{ }^\circ\text{C}$ when bound with calcium aluminate (Fondu/CA) cement; $400\text{–}500\text{ }^\circ\text{C}$ if bound with ordinary Portland cement (which dehydrates and loses strength above $450\text{ }^\circ\text{C}$).
*   **Food-Contact Verdict**: **No**. It is soft, porous, and sheds silicate dust.
*   **Adelaide Sourcing**: Hydroponic/garden wholesalers in Virginia or Wingfield for $100\text{ L}$ bags of coarse exfoliated perlite or vermiculite; landscape/builders' yards for calcium aluminate cement.
    *   *Retail*: **ESTIMATE** AUD $45–$75 per $100\text{ L}$ bag of perlite/vermiculite + AUD $60–$85 per $20\text{ kg}$ bag of CA cement.
    *   *Second-hand*: **ESTIMATE** AUD $15–$30 for partial bags on Marketplace.
*   **Difficulty**: Easy. Mixed at a 5:1 to 6:1 volume ratio (aggregate to cement) with just enough water to form a damp snowball that holds shape without dripping.
*   **Failure Mode**: High thermal conductivity compared to ceramic fibre (**[Inferred]** $k \approx 0.12\text{–}0.18\text{ W/mK}$ vs. $0.08\text{ W/mK}$ for fibre blanket), meaning you need roughly twice the wall thickness ($100\text{–}120\text{ mm}$ vs. $50\text{ mm}$) for the same heat retention. Also absorbs water like a sponge if exposed to rain, destroying its insulating value until boiled dry.

#### 2.3 Ceramic Fibre Blanket (RCF) vs. AES (Calcium-Magnesium Silicate) Blanket
*   **Where it sits**: Primary insulation wrap around the inner vault.
*   **Continuous Temperature**: **[Published]** Repository constant for ceramic fibre blanket is $1260\text{ }^\circ\text{C}$ ($k \approx 0.08\text{ W/mK}$, $\rho = 128\text{ kg/m}^3$, $c_p = 1050\text{ J/kgK}$). **[Published]** Gozney uses water-soluble calcium-magnesium silicate fibre (Alkaline-Earth Silicate, AES—the Morgan Superwool / Unifrax Insulfrax class), rated continuously around $1100\text{–}1200\text{ }^\circ\text{C}$ with $k$ in the same $0.07\text{–}0.08\text{ W/mK}$ band.
*   **Food-Contact Verdict**: **No**. The insulation space must be completely isolated from the oven chamber and burner air intake so convective drafts cannot entrain fibres onto food.
*   **Dust and Binder Rules**:
    1.  *Biopersistence*: Standard alumino-silicate Refractory Ceramic Fibre (RCF / Kaowool) is classified in Australia as a Category 1B carcinogen (respirable biopersistent fibres). AES wool (calcium-magnesium silicate) is low-biopersistence (biosoluble in lung fluid) and exempt from carcinogen classification, which is why Gozney explicitly states **"non-carcinogenic and water soluble, manufactured from calcium and magnesium silicate fibres"** **[Published]**. Specify **AES / Superwool Plus ($128\text{ kg/m}^3$)**, and still wear a P2/P3 respirator, disposable coveralls, and gloves when cutting.
    2.  *Binder Rules*: Buy **needled blanket without organic binders**. Never use residential glasswool or rockwool building batts (which use phenol-formaldehyde/acrylic binders that pyrolise at $200\text{–}250\text{ }^\circ\text{C}$ into acrid, toxic smoke and slump into powder above $650\text{ }^\circ\text{C}$).
*   **Adelaide Sourcing**: Kiln and foundry suppliers (Edwardstown, Wingfield).
    *   *Retail*: **ESTIMATE** AUD $110–$180 per full carton ($7320 \times 610 \times 25\text{ mm}$, $128\text{ kg/m}^3$ AES blanket), or AUD $25–$40 per linear metre cut from a roll.
    *   *Second-hand*: **ESTIMATE** AUD $15–$35 per linear metre from leftover pizza oven or forge builds on Gumtree.
*   **Difficulty**: Easy. Cut with a sharp Stanley knife against a straightedge.
*   **Failure Mode**:Zero compressive strength. If used under the hearth stone, the weight of the stone and peel crushes the blanket, causing the floor tiles to rock and crack. Use blanket over the dome only, and rigid Calcium Silicate board under the floor.

#### 2.4 Calcium Silicate Board
*   **Where it sits**: Rigid structural insulation directly underneath the cordierite hearth floor, and as a rigid thermal break at mounting bosses, feet, and flue collars.
*   **Continuous Temperature**: **[Inferred]** $1000\text{ }^\circ\text{C}$ (**[Published]** repo constants: $k \approx 0.065\text{ W/mK}$, $\rho = 240\text{ kg/m}^3$).
*   **Food-Contact Verdict**: **No**. It is soft and chalky; it sits beneath the cordierite cooking stone.
*   **Adelaide Sourcing**: Industrial insulation and refractory merchants in Wingfield / Regency Park (e.g., Promat Promasil / Skamol SkamoEnclosure / Calsil stockists).
    *   *Retail*: **ESTIMATE** AUD $120–$210 per sheet ($1200 \times 600 \times 25\text{ mm}$ or $50\text{ mm}$).
    *   *Second-hand*: **ESTIMATE** AUD $30–$70 for half-sheet offcuts on Marketplace.
*   **Difficulty**: Easy. Cuts cleanly on a bandsaw, table saw, or hand saw (wear a P2/P3 mask and connect workshop dust extraction).
*   **Failure Mode**: Strongly hygroscopic. If water enters the oven shell (or wet castable is poured directly onto bare Cal-Sil without a plastic slip-sheet or waterproofing sealer), it sucks moisture out of the mix, causing the castable to chalk and the Cal-Sil to soften and crack when heated.

#### 2.5 Cordierite and Firebrick Floors vs. Steel or Cast Iron (Effusivity Proof)
*   **Where it sits**: Hearth cooking floor. **[Published]** Arc Lite and Tread use $12\text{ mm}$ removable cordierite; Dome XL Gen 2 uses $30\text{ mm}$ removable cordierite.
*   **Continuous Temperature**: **[Inferred]** $1250\text{ }^\circ\text{C}$ (cordierite) / $1300\text{ }^\circ\text{C}$ (low-duty/medium-duty dense aluminosilicate firebrick).
*   **Food-Contact Verdict**: **Yes**. Both are non-toxic, inert ceramic cooking surfaces. Never substitute granite, marble, or slate (granite contains quartz that undergoes a violent $0.8\%$ volumetric $\alpha\text{-to-}\beta$ phase inversion at $573\text{ }^\circ\text{C}$ alongside trapped fluid inclusions, shattering explosively; marble calcines; slate delaminates explosively).
*   **Why Steel or Cast Iron Fails at $450\text{–}500\text{ }^\circ\text{C}$ [Modelled]**:
    When $20\text{ }^\circ\text{C}$ pizza dough ($T_{\text{dough}} = 20\text{ }^\circ\text{C}$) lands on a hot floor ($T_{\text{floor}}$), the instantaneous interfacial contact temperature $T_{\text{int}}$ is governed by the thermal effusivity $e = \sqrt{k \rho c_p}$ ($\text{J}\cdot\text{m}^{-2}\cdot\text{K}^{-1}\cdot\text{s}^{-1/2}$) of the two bodies:
    $$T_{\text{int}} = \frac{e_{\text{floor}} T_{\text{floor}} + e_{\text{dough}} T_{\text{dough}}}{e_{\text{floor}} + e_{\text{dough}}}$$
    Using **[Published]** repository constants for cordierite and dough, plus **[Inferred]** standard handbook values for dense firebrick and mild steel/cast iron:
    *   **Dough [Published]**: $e_{\text{dough}} = 1259\text{ J/m}^2\text{K s}^{1/2}$, $T_{\text{dough}} = 20\text{ }^\circ\text{C}$.
    *   **Cordierite [Published / Modelled]**: $k = 2.2\text{ W/mK}$, $\rho = 2100\text{ kg/m}^3$, $c_p = 950\text{ J/kgK}$:
        $$e_{\text{cord}} = \sqrt{2.2 \times 2100 \times 950} = \sqrt{4,389,000} = 2095\text{ J/m}^2\text{K s}^{1/2}$$
    *   **Dense Firebrick [Inferred / Modelled]**: $k = 1.4\text{ W/mK}$, $\rho = 2200\text{ kg/m}^3$, $c_p = 900\text{ J/kgK}$:
        $$e_{\text{brick}} = \sqrt{1.4 \times 2200 \times 900} = \sqrt{2,772,000} = 1665\text{ J/m}^2\text{K s}^{1/2}$$
    *   **Mild Steel / Cast Iron [Inferred / Modelled]**: $k = 45\text{ W/mK}$, $\rho = 7850\text{ kg/m}^3$, $c_p = 500\text{ J/kgK}$:
        $$e_{\text{steel}} = \sqrt{45 \times 7850 \times 500} = \sqrt{176,625,000} = 13,290\text{ J/m}^2\text{K s}^{1/2}$$

    Evaluating $T_{\text{int}}$ across the $450\text{–}500\text{ }^\circ\text{C}$ operating window:
    *   **On Cordierite at $450\text{ }^\circ\text{C}$ and $500\text{ }^\circ\text{C}$**:
        $$T_{\text{int, cord (450)}} = \frac{(2095 \times 450) + (1259 \times 20)}{2095 + 1259} = \frac{967,930}{3354} = 288.6\text{ }^\circ\text{C}$$
        $$T_{\text{int, cord (500)}} = \frac{(2095 \times 500) + (1259 \times 20)}{2095 + 1259} = \frac{1,072,680}{3354} = 319.8\text{ }^\circ\text{C}$$
    *   **On Dense Firebrick at $450\text{ }^\circ\text{C}$ and $500\text{ }^\circ\text{C}$**:
        $$T_{\text{int, brick (450)}} = \frac{(1665 \times 450) + (1259 \times 20)}{1665 + 1259} = \frac{774,430}{2924} = 264.9\text{ }^\circ\text{C}$$
        $$T_{\text{int, brick (500)}} = \frac{(1665 \times 500) + (1259 \times 20)}{1665 + 1259} = \frac{857,680}{2924} = 293.3\text{ }^\circ\text{C}$$
    *   **On Mild Steel / Cast Iron at $450\text{ }^\circ\text{C}$ and $500\text{ }^\circ\text{C}$**:
        $$T_{\text{int, steel (450)}} = \frac{(13,290 \times 450) + (1259 \times 20)}{13,290 + 1259} = \frac{6,005,680}{14,549} = 412.8\text{ }^\circ\text{C}$$
        $$T_{\text{int, steel (500)}} = \frac{(13,290 \times 500) + (1259 \times 20)}{13,290 + 1259} = \frac{6,670,180}{14,549} = 458.5\text{ }^\circ\text{C}$$

    *Physical Interpretation*: Maillard browning peaks between $160\text{ }^\circ\text{C}$ and $260\text{ }^\circ\text{C}$, while rapid pyrolysis (black carbonisation of starch) sets in above $330\text{–}350\text{ }^\circ\text{C}$. At $450\text{–}500\text{ }^\circ\text{C}$, cordierite ($289\text{–}320\text{ }^\circ\text{C}$) and firebrick ($265\text{–}293\text{ }^\circ\text{C}$) hold the contact interface right at the crisp/leopard-spotting boundary for a 60–90 second bake. Steel ($413\text{–}459\text{ }^\circ\text{C}$) has $6.3\times$ the effusivity of cordierite; it dumps heat into the wet dough so fast that the base turns to bitter carbon in under 8 seconds while the interior crumb remains raw dough. (Baking steels only work in $250\text{ }^\circ\text{C}$ domestic electric ovens, where $T_{\text{int, steel (250)}} = 230.1\text{ }^\circ\text{C}$).
*   **Adelaide Sourcing**:
    *   *Cordierite*: Ceramic/pottery supply houses in Adelaide (e.g., Bennett's Magill Pottery / Clayworks stockists or kiln suppliers) sell $12\text{–}25\text{ mm}$ kiln shelves up to $600 \times 600\text{ mm}$. **ESTIMATE** Retail: AUD $70–$160. **ESTIMATE** Second-hand (retired pottery kiln shelves on Gumtree): AUD $25–$60 (verify no lead glaze drips are fused to the shelf).
    *   *Firebricks*: Littlehampton Clay Bricks (Adelaide Hills) or local refractory brickyards ($230 \times 115 \times 38\text{ mm}$ or $76\text{ mm}$ dense firebricks). **ESTIMATE** Retail: AUD $5.50–$9.00 per brick. **ESTIMATE** Second-hand: AUD $1.00–$3.00 per brick (do not use green/chromate-containing industrial furnace bricks or old storage-heater bricks that may contain asbestos gaskets).

#### 2.6 Recycled Gas Bottles and Beer Kegs as an Inner Vault
*   **Where it sits**: Structural inner firebox vault. A $50\text{ L}$ DIN/US beer keg ($\varnothing 363\text{–}395\text{ mm} \times 532\text{–}600\text{ mm}$) is drawn from $1.5\text{–}2.0\text{ mm}$ 304 stainless steel—matching the **[Published]** 304 inner core material of all three Gozney ovens and approximating the internal volume of the Arc Lite ($325 \times 355\text{ mm}$) or Tread ($310 \times 380\text{ mm}$). Expired $9\text{ kg}$ ($\varnothing 310\text{ mm}$) or $45\text{ kg}$ ($\varnothing 375\text{ mm}$) LPG cylinders are $2.3\text{–}3.0\text{ mm}$ mild steel.
*   **Continuous Temperature**: **[Inferred]** $800\text{ }^\circ\text{C}$ for 304 stainless kegs; $450\text{–}500\text{ }^\circ\text{C}$ for mild steel LPG cylinders (mild steel oxidises and sheds mill/oxide scale rapidly above $500\text{ }^\circ\text{C}$).
*   **Mandatory De-commissioning and Cold-Cutting Protocol**:
    1.  **Never cut a closed or unpurged vessel.**
    2.  *Beer Kegs*: Depressurise the spear valve completely before unscrewing or releasing the retaining circlip (a pressurised spear becomes a lethal projectile). Remove the spear valve entirely. Flush with water.
    3.  *LPG Cylinders*: Only use out-of-date cylinders that have been fully vented outdoors away from ignition sources. Unscrew and completely remove the brass cylinder valve using a long bar and strap wrench. Fill the cylinder to overflowing with water and detergent to displace all residual heavier-than-air propane/butane vapour and flush out mercaptan sludge.
    4.  **Cold-Cut Initial Relief**: Make the initial relief opening while filled with water or using a cold mechanical method (sabre saw / nibbler / drill with cutting fluid) before touching the vessel with an angle grinder or TIG torch.
    5.  **Permanent De-commissioning**: Destroy the valve boss threads or cut the boss completely out of the shell so the vessel can **never be re-valved or used as a pressure vessel again**. Strip all external zinc/galvanising or paint off an LPG cylinder by abrasive blasting before putting it in the hot path.
*   **Differential Thermal Expansion Rule [Modelled]**:
    **[Published]** Repo constants: $\alpha_{\text{304}} = 18 \times 10^{-6}\text{ K}^{-1}$ and $\alpha_{\text{cordierite}} = 2.8 \times 10^{-6}\text{ K}^{-1}$.
    Across a $\Delta T = 480\text{ K}$ ($20\text{ }^\circ\text{C}$ to $500\text{ }^\circ\text{C}$) across a $350\text{ mm}$ wide hearth:
    $$\Delta L_{\text{304}} = 350\text{ mm} \times (18 \times 10^{-6}\text{ K}^{-1}) \times 480\text{ K} = 3.02\text{ mm}$$
    $$\Delta L_{\text{cordierite}} = 350\text{ mm} \times (2.8 \times 10^{-6}\text{ K}^{-1}) \times 480\text{ K} = 0.47\text{ mm}$$
    The stainless vault expands $2.55\text{ mm}$ more than the stone on heat-up, and shrinks $2.55\text{ mm}$ back onto the stone on cool-down. If a cordierite floor is fitted tightly inside a steel keg cradle while hot, or constrained by rigid welds without at least a $4\text{–}5\text{ mm}$ peripheral expansion gap, the shrinking steel shell will crush and split the stone during cool-down.
*   **Adelaide Sourcing**:
    *   *Retail*: **ESTIMATE** AUD $220–$300 (new unbranded $50\text{ L}$ 304 keg shell from brewing suppliers).
    *   *Second-hand*: **ESTIMATE** AUD $40–$80 for legally decommissioned scrap kegs on Gumtree/scrap metal yards in Wingfield; AUD $0–$25 for out-of-test $9\text{ kg}$ or $45\text{ kg}$ LPG bottles.

#### 2.7 Spun or Beaten Aluminium (Outer Cold Shell Only)
*   **Where it sits**: **Outer cold shell ONLY** (plus cold external trims or cast landings isolated by a thermal break). Never place aluminium in the inner vault, flue pipe, or burner dock wall.
*   **Temperature Where It Stops Being Structure [Inferred]**:
    *   **Structural Yield / Creep Limit: $150\text{ }^\circ\text{C}$ to $200\text{ }^\circ\text{C}$.** Work-hardened wrought sheet alloys (5005, 5052-H32) and precipitation-hardened alloys (6061-T6, 6063-T5) begin losing their temper and yield strength above $150\text{ }^\circ\text{C}$. At $200\text{–}250\text{ }^\circ\text{C}$, yield strength drops by $50\text{–}70\%$ and thermal creep causes thin shells to sag under their own weight.
    *   **Solidus / Melting Point: $580\text{–}660\text{ }^\circ\text{C}$.** A $500\text{ }^\circ\text{C}$ chamber has local gas/flame temperatures of $750\text{–}900\text{ }^\circ\text{C}$, which will melt an aluminium inner liner into a puddle.
*   **Food-Contact Verdict**: **No** (external casing only).
*   **Adelaide Sourcing**: Sheet metal suppliers in Wingfield/Regency Park ($1.6\text{–}2.5\text{ mm}$ 5005 or 5052 sheet; 5005 spins and hammerforms easily when annealed with soot from a rich oxy-acetylene flame and wiped off at $\sim 350\text{ }^\circ\text{C}$).
    *   *Retail*: **ESTIMATE** AUD $90–$180 per half sheet ($1200 \times 1200 \times 2.0\text{ mm}$).
    *   *Second-hand*: **ESTIMATE** AUD $25–$60 (offcuts at scrap metal yards or Marketplace).
*   **Difficulty**: High for compound curves (requires English wheel, shrinkage stump/sandbag, or lathe spinning over a turned hardwood chuck).
*   **Failure Mode**: Localized softening, blistering paint, or melting right above the oven mouth arch if rolling flames lick the outer shell lip. The mouth arch must be shielded with a 304 stainless baffle.

#### 2.8 Composite Shells (GRP / Fibreglass and Cement Board)
*   **Where it sits**: Candidate outer shell materials—**rejected for adjacent-to-flame zones**.
*   **Why They Fail Next to a Flame [Inferred]**:
    1.  *GRP (Glass-Reinforced Polyester / Vinylester / Epoxy)*: Standard polyester and epoxy laminating resins have a glass transition temperature ($T_g$) of only $60\text{–}110\text{ }^\circ\text{C}$ and undergo thermal decomposition above $180\text{–}220\text{ }^\circ\text{C}$. If mouth radiation or a brief flame rollout hits a GRP lip, the resin ignites, releasing dense black styrene smoke. GRP can only be used as a decorative cold cover over a fully self-contained, thick-walled brick/castable igloo whose external masonry surface never exceeds $50\text{ }^\circ\text{C}$, stopped at least $200\text{ mm}$ back from the mouth and flue.
    2.  *Cement Sheet (Fibro / Villaboard / HardieFlex)*: Modern Australian cellulose-reinforced autoclaved cement sheet uses wood-pulp cellulose fibres (roughly $7\text{–}10\text{ wt}\%$) rather than asbestos. Above $150\text{–}200\text{ }^\circ\text{C}$, the cellulose fibres char and pyrolise, destroying tensile strength. Furthermore, cement sheet holds $8\text{–}12\%$ equilibrium moisture; rapid heating next to a flame turns trapped pore water into high-pressure steam, causing explosive delamination and gunshot-like spalling.
*   **Adelaide Sourcing**: Hardware stores (**ESTIMATE** Retail AUD $40–$90; Second-hand AUD $10–$25), but **do not use in the hot envelope**.

#### 2.9 Microporous Insulation Board (Bought Slab Only)
*   **Where it sits**: Ultra-thin outer or under-hearth backup insulation layer where envelope space is tight (e.g., matching the thin floor stack of the Arc Lite or Tread).
*   **Continuous Temperature**: **[Inferred]** $1000\text{ }^\circ\text{C}$ (fumed silica + silicon carbide/titania IR opacifier + E-glass reinforcing filaments, encapsulated in glass cloth or foil). Thermal conductivity is $k \approx 0.021\text{–}0.026\text{ W/mK}$ at $200\text{–}400\text{ }^\circ\text{C}$—lower than still air because the pore size ($<50\text{ nm}$) is smaller than the mean free path of air molecules ($68\text{ nm}$), suppressing Knudsen gas conduction.
*   **Why It Is a Bought Slab, Not a DIY Mix**: You cannot reproduce nanoporous Knudsen-regime pressing at home; mixing fumed silica with water collapses the nanopore structure via capillary tension, turning it into ordinary dense silica with $5\times$ higher conductivity.
*   **Food-Contact Verdict**: **No**. Keep encapsulated inside the outer shell cavity.
*   **Adelaide Sourcing**: Specialist industrial refractory suppliers (Promat Promalight / Microtherm or Morgan WDS Ultra stockists).
    *   *Retail*: **ESTIMATE** AUD $220–$420 per panel ($1000 \times 600 \times 10\text{ mm}$ to $25\text{ mm}$).
    *   *Second-hand*: **ESTIMATE** AUD $80–$150 (rare; occasional industrial furnace surplus).
*   **Failure Mode**: If exposed directly to the hot face above $1000\text{ }^\circ\text{C}$, the amorphous nanopores sinter and shrink irreversibly. Place it on the **cold side** of an AES fibre blanket or Cal-Sil board so the microporous slab stays below $400\text{–}600\text{ }^\circ\text{C}$, where its $k$ value is lowest.

---

## 3. Engineering Analysis: Turned or Coopered Hardwood Outer Body

Adib has a wood lathe, coopering capability, and CAD/CAM access, and wants to build a turned or coopered hardwood barrel/stave outer body to contain the castable core and insulation—eliminating sheet-metal pressings for the outer shell.

### 3.1 Steady-State 1D Thermal Resistance Network [Modelled]

**Target and Boundary Conditions [Published / Prompt Specified]**:
*   Internal gas temperature: $T_{\text{gas}} = 500\text{ }^\circ\text{C}$
*   Ambient air temperature: $T_{\text{amb}} = 20\text{ }^\circ\text{C}$ ($\Delta T_{\text{total}} = 500 - 20 = 480\text{ K}$)
*   Internal convective/effective heat transfer coefficient: $h_{\text{in}} = 25\text{ W/m}^2\text{K}$
*   External convective/effective heat transfer coefficient (still outdoor air): $h_{\text{ext}} = 10\text{ W/m}^2\text{K}$
*   Maximum allowable hardwood inner-face temperature in steady state: $T_{\text{w,in}} \le 80\text{ }^\circ\text{C}$
*   Hardwood wall thickness: $L_{\text{wood}} = 20\text{ mm} = 0.020\text{ m}$ (within the $18\text{–}25\text{ mm}$ stave specification).

#### The "Thermal Dam" Trap of a Wood Outer Shell
Before choosing the insulation thickness, note a critical physical difference between a sheet-metal outer shell and a $20\text{ mm}$ hardwood outer shell.
*   A $1.2\text{ mm}$ steel shell has negligible thermal resistance ($R_{\text{steel}} \approx 0.00003\text{ m}^2\text{K/W}$); heat reaching the outer skin dissipates directly into the air via $R_{\text{ext}} = \frac{1}{h_{\text{ext}}} = 0.100\text{ m}^2\text{K/W}$.
*   Dry South Australian hardwood (e.g., Red Gum, Sugar Gum, or Jarrah across the grain) has a thermal conductivity of **[Inferred]** $k_{\text{wood}} = 0.16\text{ W/mK}$. A $20\text{ mm}$ wood stave therefore has a thermal resistance of:
    $$R_{\text{wood}} = \frac{L_{\text{wood}}}{k_{\text{wood}}} = \frac{0.020\text{ m}}{0.16\text{ W/mK}} = 0.125\text{ m}^2\text{K/W}$$
    Because the wood sits in series with the external air boundary layer ($R_{\text{ext}} = 0.100\text{ m}^2\text{K/W}$), the combined resistance from the wood inner face to ambient air is:
    $$R_{\text{wood+ext}} = R_{\text{wood}} + R_{\text{ext}} = 0.125 + 0.100 = 0.225\text{ m}^2\text{K/W}$$
    The wood acts as an external thermal dam, trapping heat at the insulation-to-wood interface. For $T_{\text{w,in}}$ not to exceed $80\text{ }^\circ\text{C}$ ($T_{\text{w,in}} - T_{\text{amb}} \le 60\text{ K}$) in a closed, unventilated 1D stack, the maximum allowable steady-state heat flux $q''$ through the wall is:
    $$q''_{\text{max}} = \frac{T_{\text{w,in,max}} - T_{\text{amb}}}{R_{\text{wood}} + R_{\text{ext}}} = \frac{80 - 20}{0.225\text{ m}^2\text{K/W}} = 266.67\text{ W/m}^2$$
    This requires a minimum total 1D thermal resistance across the wall of:
    $$R_{\text{total,min}} = \frac{T_{\text{gas}} - T_{\text{amb}}}{q''_{\text{max}}} = \frac{480\text{ K}}{266.67\text{ W/m}^2} = 1.800\text{ m}^2\text{K/W}$$

#### Proposed Layer Stack (Closed 1D Conductive Stack)
To satisfy $R_{\text{total}} \ge 1.800\text{ m}^2\text{K/W}$ while keeping the wood off the hot ceramic fibre face, we specify the following 4-layer solid wall stack:
1.  **Inner Refractory Vault**: $25\text{ mm}$ ($L_1 = 0.025\text{ m}$) dense high-alumina castable refractory (**[Inferred]** $k_1 = 1.50\text{ W/mK}$).
2.  **Primary Insulation**: $100\text{ mm}$ ($L_2 = 0.100\text{ m}$, four $25\text{ mm}$ wraps) AES calcium-magnesium silicate fibre blanket (**[Published]** $k_2 = 0.080\text{ W/mK}$).
3.  **Rigid Thermal Break / Backing Liner**: $25\text{ mm}$ ($L_3 = 0.025\text{ m}$) Calcium Silicate board or stave segments (**[Published]** $k_3 = 0.065\text{ W/mK}$).
4.  **Outer Cold Shell**: $20\text{ mm}$ ($L_4 = 0.020\text{ m}$) coopered or turned hardwood (**[Inferred]** $k_4 = 0.160\text{ W/mK}$).

#### Step-by-Step 1D Resistance and Temperature Calculation [Modelled]

1.  **Individual Unit Thermal Resistances ($R_i$ in $\text{m}^2\text{K/W}$)**:
    *   Internal convection:
        $$R_{\text{in}} = \frac{1}{h_{\text{in}}} = \frac{1}{25} = 0.0400\text{ m}^2\text{K/W}$$
    *   Layer 1 ($25\text{ mm}$ Castable):
        $$R_1 = \frac{L_1}{k_1} = \frac{0.025}{1.50} = 0.0167\text{ m}^2\text{K/W}$$
    *   Layer 2 ($100\text{ mm}$ AES Blanket):
        $$R_2 = \frac{L_2}{k_2} = \frac{0.100}{0.080} = 1.2500\text{ m}^2\text{K/W}$$
    *   Layer 3 ($25\text{ mm}$ Calcium Silicate):
        $$R_3 = \frac{L_3}{k_3} = \frac{0.025}{0.065} = 0.3846\text{ m}^2\text{K/W}$$
    *   Layer 4 ($20\text{ mm}$ Hardwood):
        $$R_4 = \frac{L_4}{k_4} = \frac{0.020}{0.160} = 0.1250\text{ m}^2\text{K/W}$$
    *   External convection:
        $$R_{\text{ext}} = \frac{1}{h_{\text{ext}}} = \frac{1}{10} = 0.1000\text{ m}^2\text{K/W}$$

2.  **Total Resistance and Steady-State Heat Flux ($q''$)**:
    $$R_{\text{total}} = 0.0400 + 0.0167 + 1.2500 + 0.3846 + 0.1250 + 0.1000 = 1.9163\text{ m}^2\text{K/W}$$
    $$q'' = \frac{T_{\text{gas}} - T_{\text{amb}}}{R_{\text{total}}} = \frac{500 - 20}{1.9163\text{ m}^2\text{K/W}} = \frac{480\text{ K}}{1.9163\text{ m}^2\text{K/W}} = 250.48\text{ W/m}^2$$

3.  **Interface Temperatures Through the Stack**:
    *   **Hot gas**: $T_{\text{gas}} = 500.0\text{ }^\circ\text{C}$
    *   **Castable inner hot face ($T_{\text{s,in}}$)**:
        $$T_{\text{s,in}} = 500.0 - (250.48 \times 0.0400) = 500.0 - 10.02 = 489.98\text{ }^\circ\text{C}$$
    *   **Castable / AES blanket interface ($T_{1\text{–}2}$)**:
        $$T_{1\text{–}2} = 489.98 - (250.48 \times 0.0167) = 489.98 - 4.18 = 485.80\text{ }^\circ\text{C}$$
    *   **AES blanket / Calcium Silicate interface ($T_{2\text{–}3}$)**:
        $$T_{2\text{–}3} = 485.80 - (250.48 \times 1.2500) = 485.80 - 313.10 = 172.70\text{ }^\circ\text{C}$$
    *   **Calcium Silicate / Hardwood Inner Face ($T_{\text{w,in}}$)**:
        $$T_{\text{w,in}} = 172.70 - (250.48 \times 0.3846) = 172.70 - 96.33 = \mathbf{76.37\text{ }^\circ\text{C}} \quad (\le 80\text{ }^\circ\text{C}\text{ target achieved})$$
    *   **Hardwood Outer Face ($T_{\text{w,out}}$)**:
        $$T_{\text{w,out}} = 76.37 - (250.48 \times 0.1250) = 76.37 - 31.31 = \mathbf{45.06\text{ }^\circ\text{C}}$$
    *   *Verification against ambient*: $T_{\text{amb}} = 45.06 - (250.48 \times 0.1000) = 45.06 - 25.05 = 20.01\text{ }^\circ\text{C}$.

#### Comparison Against Inadequate Stacks [Modelled]
To show why thin insulation or perlite concrete alone fails inside a wood barrel:
*   **Failure Case 1 ($25\text{ mm}$ Castable + $50\text{ mm}$ AES Blanket + $20\text{ mm}$ Wood, no Cal-Sil)**:
    $R_{\text{total}} = 0.0400 + 0.0167 + 0.6250 + 0.1250 + 0.1000 = 0.9067\text{ m}^2\text{K/W}$.
    $q'' = 480 / 0.9067 = 529.39\text{ W/m}^2$.
    **Wood inner face**: $T_{\text{w,in}} = 20 + 529.39 \times (0.1250 + 0.1000) = \mathbf{139.1\text{ }^\circ\text{C}}$ (**FAILS**: causes severe wood desiccation, resin exudation, splitting, and long-term low-temperature pyrolysis).
*   **Failure Case 2 ($25\text{ mm}$ Castable + $100\text{ mm}$ Perlite Concrete at $k = 0.12\text{ W/mK}$ + $20\text{ mm}$ Wood)**:
    $R_{\text{perlite}} = 0.100 / 0.12 = 0.8333\text{ m}^2\text{K/W} \implies R_{\text{total}} = 1.1150\text{ m}^2\text{K/W}$.
    $q'' = 480 / 1.1150 = 430.49\text{ W/m}^2$.
    **Wood inner face**: $T_{\text{w,in}} = 20 + 430.49 \times 0.2250 = \mathbf{116.9\text{ }^\circ\text{C}}$ (**FAILS**: perlite concrete would have to be $200\text{ mm}$ thick to keep $T_{\text{w,in}} \le 80\text{ }^\circ\text{C}$).

---

### 3.2 What Breaks the 1D Model in a Real Oven

A 1D radial conduction model only applies to the mid-belly of the barrel away from openings. Five boundary conditions break the 1D model and will ignite a naive wooden shell:

1.  **Flame Roll and Buoyant Plume Out the Mouth**:
    In a flue-less oven (like the Arc Lite or Tread) or when firing on high, $450\text{–}650\text{ }^\circ\text{C}$ exhaust gases spill out the top edge of the mouth arch and rise straight up the front bulkhead. Convective heat transfer at the mouth brow jumps from $10\text{ W/m}^2\text{K}$ to $40\text{–}60\text{ W/m}^2\text{K}$ with a gas temperature above the auto-ignition temperature of hardwood ($\sim 250\text{–}300\text{ }^\circ\text{C}$).
2.  **Direct View-Factor Radiation at a Wood Arch**:
    Any material framing the $310 \times 85\text{ mm}$ or $470 \times 140\text{ mm}$ opening has a direct optical view factor to the $500\text{ }^\circ\text{C}$ stone and $850\text{ }^\circ\text{C}$ flame. **[Modelled]** Using $\sigma = 5.670 \times 10^{-8}\text{ W/m}^2\text{K}^4$, blackbody emissive power at $500\text{ }^\circ\text{C}$ ($773\text{ K}$) is:
    $$E_b = 5.670 \times 10^{-8} \times (773.15)^4 = 20,247\text{ W/m}^2$$
    Even a small view factor ($F = 0.15$) delivers $>3,000\text{ W/m}^2$ to the mouth surround—$12\times$ the allowable conductive flux. A wooden mouth arch will burst into flame within minutes.
3.  **The Flue Penetration**:
    If the oven uses a top flue (like the Dome XL Gen 2), the stainless steel flue pipe runs at $350\text{–}500\text{ }^\circ\text{C}$. Passing that pipe through or near wooden staves creates a high-flux thermal bridge that will char and ignite the surrounding timber.
4.  **The Hot Landing and Burner Dock**:
    Spilled burning cheese/flour on the front landing, radiant heat downwards onto the hearth lip, and hot secondary air intake / burner blowback at the lateral burner dock (**[Published]** Tread manual: *"Fire out of the dock means shut down"*) can expose the bottom edge of a wooden shell to direct flame.
5.  **Rain and Outdoor Weathering**:
    If rain enters the joints between coopered staves and wets the Calcium Silicate or AES blanket, the insulation conductivity spikes by $5\text{–}10\times$, boiling water into steam against the inner face of the wood and warping the barrel apart.

---

### 3.3 Engineering Mitigations to Make the Hardwood Barrel Work

To turn Adib's coopered/turned barrel into a safe, durable build, apply six mandatory design rules:

1.  **Non-Combustible 304 Stainless Mouth Surround and Brow Deflector**:
    Do not bring wood anywhere near the oven mouth. Fabricate the entire front faceplate and mouth tunnel out of $1.5\text{–}2.0\text{ mm}$ 304 stainless steel (or cast refractory), recessed or projecting so that the wooden barrel staves terminate at least **$150\text{ mm}$ radially outward and behind** the mouth opening, separated by Calcium Silicate board and a proud stainless heat-deflector lip above the brow.
2.  **304 Twin-Wall Flue Collar with Calcium Silicate Sleeve (or Flue-less Front Exhaust)**:
    If fitting a flue, pass it through a $250\text{ mm}$ diameter 304 stainless deck plate, insulated from the wood stave ring by a minimum $75\text{ mm}$ annular sleeve of Calcium Silicate board and a ventilated air collar.
3.  **Add a $15\text{–}20\text{ mm}$ Bottom-to-Top Ventilated Air Cavity + Aluminium Foil Shield**:
    Instead of pressing the wood staves tight against the Calcium Silicate board, wrap the outside of the $75\text{–}100\text{ mm}$ AES/Cal-Sil insulation core in $0.5\text{ mm}$ sheet metal or heavy aluminium foil (low emissivity $\varepsilon \approx 0.05$), and stand the wooden barrel staves off on $15\text{–}20\text{ mm}$ spacers with open air intake slots at the base and exhaust vents at the top crown. Natural chimney convection through this $15\text{ mm}$ air gap carries away the $250\text{ W/m}^2$ conductive heat leak before it ever touches the wood, dropping $T_{\text{w,in}}$ from $76\text{ }^\circ\text{C}$ down to **$30\text{–}35\text{ }^\circ\text{C}$** and cutting the required AES blanket thickness from $100\text{ mm}$ to $75\text{ mm}$.
4.  **South Australian Timber Species Selection**:
    Avoid resinous softwoods (Radiata Pine exudes flammable turpentine/pitch above $65\text{ }^\circ\text{C}$ and warps badly). Select dense, kiln-dried hardwoods readily sourced in Adelaide:
    *   **Tasmanian Blackwood (*Acacia melanoxylon*)**: Best stability and lowest movement in service; easy to cooper and turn; widely available from Adelaide timber merchants (e.g., Otto Timber / specialty salvage yards).
    *   **Jarrah (*Eucalyptus marginata*, brought in from WA / salvaged in SA)**: High density ($\sim 820\text{ kg/m}^3$), naturally durable, low volatile extractives.
    *   **Sugar Gum (*Eucalyptus cladocalyx*) or River Red Gum (*Eucalyptus camaldulensis*)**: Abundant across SA (Adelaide Hills, Mid North, Fleurieu), very hard and dense ($900\text{–}1100\text{ kg/m}^3$), though interlocking grain requires sharp tooling and slow drying to avoid surface checking.
    *   *Pricing*: **ESTIMATE** Retail kiln-dried dressed boards: AUD $140–$260 for enough board-feet to cooper a Tread/Arc-sized shell. **ESTIMATE** Second-hand (salvaged Jarrah floorboards or Red Gum slabs on Gumtree SA): AUD $40–$90.
5.  **Moisture Movement vs. Thermal Movement**:
    Wood is hygroscopic: when heated from $20\text{ }^\circ\text{C}$ (at $12\%$ equilibrium moisture content in Adelaide winter) to $60\text{–}75\text{ }^\circ\text{C}$ on its inner face, it loses moisture and **shrinks** tangentially by $2\text{–}4\%$, whereas its positive thermal expansion is tiny ($\alpha \approx 3\text{–}5 \times 10^{-6}\text{ K}^{-1}$ parallel to grain, $30\text{–}50 \times 10^{-6}\text{ K}^{-1}$ across grain). Net effect: **a heated wood barrel shrinks, loosening its hoops.**
    *   *Solution*: Use Quarter-Sawn staves (radial shrinkage is half of tangential shrinkage), machine a floating spline or tongue-and-groove joint between staves without rigid glue locking the entire circumference, and tension the external 304 stainless coopering hoops with **Belleville disc-spring washers** on the draw-bolts so the hoops automatically take up slack as the timber dries and swells across Adelaide seasons.
6.  **Zero-Char Design Rule**:
    **A char layer is NOT an acceptable design state.** In structural fire engineering, timber chars at $\sim 0.6\text{ mm/min}$ above $300\text{ }^\circ\text{C}$ during a one-off building evacuation. In a repeatedly cycled appliance, wood exposed continuously above $100\text{–}120\text{ }^\circ\text{C}$ undergoes slow exothermic pyrolysis, forming pyrophoric charcoal whose auto-ignition temperature drops as low as $150\text{–}180\text{ }^\circ\text{C}$. If any inner wood surface darkens or chars, the insulation or air gap has failed and the oven must be shut down immediately.

---

### 3.4 Engineering Verdict on the Hardwood Outer Body

*   **Verdict**: **Viable ONLY as a decoupled, ventilated outer cold shell ($T_{\text{w,in}} \le 80\text{ }^\circ\text{C}$, ideally $\le 45\text{ }^\circ\text{C}$ with a $15\text{ mm}$ ventilated air cavity).**
*   **Non-Negotiable Conditions**:
    1.  The inner vault must be continuous 304 stainless steel or cast refractory, backed by at least $75\text{–}100\text{ mm}$ of AES fibre blanket + $25\text{ mm}$ Calcium Silicate board + a foil-lined $15\text{–}20\text{ mm}$ ventilated air gap inside the staves.
    2.  **The mouth arch, front faceplate, landing, burner dock, and flue collar MUST stay 304 stainless steel or cast refractory.** No timber is permitted within $150\text{ mm}$ of the mouth opening, burner port, or uninsulated flue pipe.
    3.  The oven must be stored out of the rain or under a waterproof cover when cold.

---

## 4. Mandatory Certified-Buy Components (Do Not Fabricate)

In accordance with Australian gas installation and appliance safety practice (AS/NZS 5601 / AS/NZS 5263 / AGA certification marks **[Published]** on the Dome XL EU spec sheet as AGA / SANZ), the entire gas train must be purchased as a pre-engineered, certified assembly or harvested intact from a certified commercial outdoor LPG appliance:

1.  **Venturi Gas Burner Assembly** (matched to the target heat input: $\sim 3.4\text{–}3.7\text{ kW}$ for a $310\text{–}325\text{ mm}$ hearth, or $\sim 10.6\text{ kW}$ for a $724\text{ mm}$ hearth).
2.  **Calibrated Brass Injector Jet** (factory-drilled orifice matched to the burner and $2.75\text{ kPa}$ Australian Universal LPG regulator pressure; e.g., **[Published]** $0.95\text{–}0.98\text{ mm}$ for $3.4\text{–}3.7\text{ kW}$, $1.86\text{ mm}$ for $10.6\text{ kW}$ at $11\text{ in WC}$ / $2.74\text{ kPa}$).
3.  **Gas Control Valve with Integrated Flame Failure Device (FFD / Thermocouple Interlock)** and piezo/electronic igniter (shuts off gas automatically if the flame blows out).
4.  **Thermocouple Sensor Probe** (positioned directly in the pilot/main burner flame envelope).
5.  **AGA-Certified $2.75\text{ kPa}$ LPG Regulator and Braided/Elastomeric Hose Assembly** with LCC27 / POL cylinder connection, kept at least $50\text{ mm}$ clear of hot surfaces in a ventilated dock.
