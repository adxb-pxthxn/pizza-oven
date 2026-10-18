### Critique of the Three Concepts & Correction of the Stone-Removal Error

#### Correction of the False Sentence in Concept B (Stone Removal Geometry)
In the earlier pass on Concept B, I wrote that the $\varnothing 430 \times 20\text{ mm}$ cordierite stone could tilt $22^\circ$ and pass through the $395 \times 90\text{ mm}$ mouth because the rectangular diagonal is $\sqrt{395^2 + 90^2} = 405.1\text{ mm}$. **That statement is geometrically false.**

A circular disk of diameter $D = 430\text{ mm}$ and thickness $t = 20\text{ mm}$ cannot align with the diagonal of a rectangular slot of width $W$ and height $H$ unless its projected width $D\cos\theta + t\sin\theta \le W$ and its projected height $D\sin\theta + t\cos\theta \le H$ at the instant its full diameter crosses the mouth plane:
1. For $D = 430\text{ mm}$ and $W = 395\text{ mm}$:
   $$\theta = \arccos\left(\frac{395}{430}\right) = 23.28^\circ$$
   $$H_{\text{req}} = 430\sin(23.28^\circ) + 20\cos(23.28^\circ) = 169.9\text{ mm} + 18.4\text{ mm} = 188.3\text{ mm}$$
   A $188.3\text{ mm}$ projected height will not pass through a $90\text{ mm}$ mouth.
2. Even with the mouth widened to $W = 420\text{ mm}$ and raised to $H = 95\text{ mm}$:
   $$\theta = \arccos\left(\frac{420}{430}\right) = 12.38^\circ$$
   $$H_{\text{req}} = 430\sin(12.38^\circ) + 20\cos(12.38^\circ) = 92.2\text{ mm} + 19.5\text{ mm} = 111.7\text{ mm} > 95\text{ mm}$$

A one-piece $\varnothing 430 \times 20\text{ mm}$ stone **never** comes out through the mouth. The equatorial brass cinch band—which unlatches so the upper crown lifts vertically off the lower hearth pan—is the true mechanical access for installing and removing a one-piece stone, cleaning the deck pan, and inspecting the insulation.

---

### Attack on the Five Engineering Questions Before Locking Concept B

#### 1. Mouth Width and Height: $395 \times 90\text{ mm}$ vs. $420 \times 95\text{ mm}$ on a $\varnothing 470\text{ mm}$ Chamber
A $395\text{ mm}$ mouth leaves $(395 - 381)/2 = 7\text{ mm}$ per side for a $381\text{ mm}$ (15") pizza. Launching stretched dough off a $381\text{ mm}$ peel through a slot with $7\text{ mm}$ side clearance invites catching the peel edge on the stainless mouth jambs and dumping toppings onto the hot stone. Widening the mouth to **$420\text{ mm}$ wide $\times 95\text{ mm}$ high** gives **$19.5\text{ mm}$ per side** and keeps the mouth-to-apex ratio at:
$$\frac{H_{\text{mouth}}}{H_{\text{apex}}} = \frac{95\text{ mm}}{165\text{ mm}} = 0.576$$
This preserves a $70\text{ mm}$ deep inverted weir (flame pocket) above the lintel so the buoyant gas ceiling jet rolls across the dome before spilling.

**Quantifying the thermal penalty of widening from $395 \times 90\text{ mm}$ to $420 \times 95\text{ mm}$:**
- With $R = 25\text{ mm}$ upper corner radii, the open area increases from:
  $$A_1 = (0.395 \times 0.090) - (4 - \pi)(0.025)^2 = 0.03501\text{ m}^2$$
  to:
  $$A_2 = (0.420 \times 0.095) - (4 - \pi)(0.025)^2 = 0.03936\text{ m}^2 \quad (\Delta A = +0.00435\text{ m}^2, \text{ or } +12.4\%)$$
- **Radiation loss penalty:** At an effective cavity temperature $T_{\text{cav}} = 480^\circ\text{C}$ ($753\text{ K}$) radiating to $T_{\text{amb}} = 20^\circ\text{C}$ ($293\text{ K}$) with effective mouth emissivity $\varepsilon_{\text{eff}} = 0.85$:
  $$q_{\text{rad}} = 0.85 \times 5.67 \times 10^{-8} \times (753^4 - 293^4) = 15,154\text{ W/m}^2$$
  $$Q_{\text{rad},1} = 531\text{ W}, \qquad Q_{\text{rad},2} = 596\text{ W} \implies \Delta Q_{\text{rad}} = +65\text{ W}$$
- **Buoyant doorway spill penalty:** Natural-convection orifice spill scales with $W \cdot H^{3/2}$:
  $$\frac{420 \times 95^{1.5}}{395 \times 90^{1.5}} = 1.0633 \times 1.0845 = 1.153 \quad (+15.3\%)$$
  On an estimated $1.4\text{ kW}$ mouth flue gas exit stream, the incremental convective heat loss above the neutral plane is $\approx +215\text{ W}$.
- **Combined penalty:** $+280\text{ W}$ ($4.8\%$ of a $5.8\text{ kW}$ burner). That costs roughly $1.5\text{ minutes}$ on heat-up and is well worth paying to eliminate peel-launch collisions.
- **Chamber intersection geometry check:** On a $\varnothing 470\text{ mm}$ inner chamber ($R = 235\text{ mm}$), as long as the inner liner rises as a vertical cylinder to the $z = 95\text{ mm}$ springline before curving into the dome cap ($z = 95\text{ mm}$ to $165\text{ mm}$), the $420\text{ mm}$ mouth chord intersects the cylinder cleanly at $x = \sqrt{235^2 - 210^2} = 105.5\text{ mm}$ forward of the chamber center without cutting into the compound dome curvature.

#### 2. Floor Diameter: Keep $\varnothing 430\text{ mm}$ or Spend the Mass for $\varnothing 450\text{ mm}$?
On a $\varnothing 430\text{ mm}$ stone, a $381\text{ mm}$ pizza has $(430 - 381)/2 = 24.5\text{ mm}$ radial clearance around its entire perimeter ($49\text{ mm}$ total diameter margin). By comparison, commercial portable gas ovens give $9.5\text{–}10\text{ mm}$ per side.
- Going to a $\varnothing 450 \times 20\text{ mm}$ stone ($\rho = 2100\text{ kg/m}^3$) increases stone mass from:
  $$m_{430} = \pi (0.215)^2 (0.020)(2100) = 6.10\text{ kg} \quad \text{to} \quad m_{450} = \pi (0.225)^2 (0.020)(2100) = 6.68\text{ kg} \quad (+0.58\text{ kg})$$
- However, expanding the chamber by $+20\text{ mm}$ (to $\varnothing 490\text{ mm}$) to fit the $\varnothing 450\text{ mm}$ stone expands the entire outer shell from $\varnothing 625\text{ mm}$ to $\varnothing 645\text{ mm}$, adding **$+1.15\text{ kg}$** to the permanent shell and increasing stone thermal capacity by $+9.5\%$ ($\approx 2.5\text{ minutes}$ slower soak).
- **Decision:** Keep the **$\varnothing 430 \times 20\text{ mm}$ floor** ($24.5\text{ mm}$ radial clearance is generous for turning with a $\varnothing 180\text{ mm}$ turning peel) and add a **$420 \times 45\text{ mm}$ external 304 stainless landing lip** flush with the stone top at the mouth sill ($+0.22\text{ kg}$).

#### 3. Outer Skin Temperature: $62\text{–}65^\circ\text{C}$ vs. Dropping the Crown Under $55^\circ\text{C}$
Using the 1D steady-state network ($T_{\text{gas}} = 500^\circ\text{C}$, $T_{\text{amb}} = 20^\circ\text{C}$, $\Delta T = 480\text{ K}$, $h_{\text{in}} = 25\text{ W/m}^2\text{K} \implies R_{\text{in}} = 0.040\text{ m}^2\text{K/W}$, $h_{\text{ext}} = 10\text{ W/m}^2\text{K} \implies R_{\text{ext}} = 0.100\text{ m}^2\text{K/W}$, neglecting $0.00015\text{ m}^2\text{K/W}$ for two $1.2\text{ mm}$ 304 skins):
- **Sidewall ($50\text{ mm}$ AES at $k=0.08$ + $25\text{ mm}$ CalSil at $k=0.065$):**
  $$R_{\text{wall}} = 0.040 + \frac{0.050}{0.08} + \frac{0.025}{0.065} + 0.100 = 0.040 + 0.6250 + 0.3846 + 0.100 = 1.1496\text{ m}^2\text{K/W}$$
  $$q_{\text{wall}} = \frac{480}{1.1496} = 417.5\text{ W/m}^2 \implies T_{\text{skin,wall}} = 20 + (417.5 \times 0.100) = 61.8^\circ\text{C}$$
- **Previous Crown ($75\text{ mm}$ AES only):**
  $$R_{\text{crown,75}} = 0.040 + \frac{0.075}{0.08} + 0.100 = 1.0775\text{ m}^2\text{K/W} \implies q = 445.5\text{ W/m}^2 \implies T_{\text{skin,crown}} = 64.5^\circ\text{C}$$
- **What it takes to get the crown under $55^\circ\text{C}$:**
  For $T_{\text{skin,crown}} \le 55.0^\circ\text{C}$, the heat flux must not exceed:
  $$q_{\max} = \frac{55.0 - 20.0}{0.100} = 350.0\text{ W/m}^2 \implies R_{\text{total,req}} = \frac{480}{350.0} = 1.3714\text{ m}^2\text{K/W}$$
  Subtracting $R_{\text{in}} + R_{\text{ext}} = 0.140\text{ m}^2\text{K/W}$ leaves $R_{\text{AES,req}} = 1.2314\text{ m}^2\text{K/W}$:
  $$t_{\text{AES,req}} = 1.2314 \times 0.08 = 0.0985\text{ m} = 98.5\text{ mm}$$
  Using **$100\text{ mm}$ of AES** (four $25\text{ mm}$ blanket layers):
  $$R_{\text{total,100}} = 0.040 + \frac{0.100}{0.08} + 0.100 = 1.390\text{ m}^2\text{K/W} \implies q = 345.3\text{ W/m}^2 \implies T_{\text{skin,crown}} = 54.5^\circ\text{C}$$
- **Mass penalty of the $100\text{ mm}$ AES crown:**
  - Extra $25\text{ mm}$ AES layer over the crown ($A_{\text{mean}} = 0.28\text{ m}^2$, $\rho = 128\text{ kg/m}^3$): $0.28 \times 0.025 \times 128 = +0.90\text{ kg}$.
  - Extra $25\text{ mm}$ height on the $1.2\text{ mm}$ 304 outer skirt ($\pi \times 0.625 \times 0.025 \times 0.0012 \times 7900$): $+0.47\text{ kg}$.
  - **Total mass penalty:** **$+1.37\text{ kg}$** (and $+25\text{ mm}$ body height, from $315\text{ mm}$ to $340\text{ mm}$, still well below the $460\text{ mm}$ target).
- **Decision:** **Adopt the $100\text{ mm}$ AES crown ($54.5^\circ\text{C}$).** Intentional continuous-grip surfaces are solely the oiled jarrah side handles, the jarrah gas valve knob, and the jarrah-collared feet (all $<38^\circ\text{C}$), while an accidental brush against the top crown meets $54.5^\circ\text{C}$ rather than $64.5^\circ\text{C}$.

#### 4. Securing the Removable Crown on Corrugated Roads
A flat friction band around a smooth cylinder will walk off under 3–5 $g$ vertical vibration on dirt corrugations. The joint is locked mechanically as follows:
1. **Rolled Rim Beads + Internal Spigot:** At the horizontal parting line ($z = 115\text{ mm}$ above the base pan bottom), both the lower pan upper edge and the upper dome lower edge have a **$6\text{ mm}$ outward horizontal flange bead** rolled at the university workshop (rotary jenny on $1.2\text{ mm}$ 304). Inside the joint, a $20\text{ mm}$ tall $1.2\text{ mm}$ 304 spigot sleeve welded to the lower pan telescopes inside the upper dome and compresses a $\varnothing 10\text{ mm}$ braided ceramic/E-glass rope seal.
2. **Captive V-Channel Retainers Inside the Brass Band:** Six $50\text{ mm}$ long segments of $1.5\text{ mm}$ 304 stainless channel ($14\text{ mm}$ wide $\times 8\text{ mm}$ deep) are riveted with solid $\varnothing 4\text{ mm}$ brass rivets to the inside face of the $35 \times 3\text{ mm}$ C26000 brass band at $60^\circ$ intervals. When the band closes around the equator, those six channels straddle both the upper and lower $6\text{ mm}$ rim beads like a V-band clamp. The crown is positively captured in $Z$ and cannot walk vertically unless the band expands radially by $>8\text{ mm}$.
3. **Over-Center Toggle Latch with Captive Night Pin:** The brass band hinges at the front-left ($150^\circ$ from the rear centerline) and closes at the rear via a 304 stainless over-center draw latch on an M8 trunnion bolt. A captive $\varnothing 5\text{ mm}$ spring-loaded stainless ball-lock pin passes through a $\varnothing 5.5\text{ mm}$ cross-hole in the closed toggle handle: you can pull or insert the pin by feel in pitch darkness without tools, and the toggle cannot vibrate open on corrugations.
4. **Load Path Isolation:** Both jarrah side lift handles bolt strictly to the **lower hearth pan** ($40\text{ mm}$ below the parting line), so carrying or strapping down the lower body puts zero tensile load through the brass cinch band.

#### 5. What Concept B Steals from Concepts A and C (Costing $+0.42\text{ kg}$, Not $+20\text{ kg}$)
- **From Concept A:** The **$420 \times 45\text{ mm}$ 1.5 mm 304 front peel landing lip** at the mouth sill ($+0.22\text{ kg}$) and a **Trotec-engraved C26000 brass maker's plate** ($90 \times 35 \times 2\text{ mm}$) riveted above the mouth lintel with solid copper rivets.
- **From Concept C:** Every touchpoint becomes **jarrah + brass**: a turned jarrah gas control knob ($\varnothing 48 \times 35\text{ mm}$) with a turned C36000 brass ferrule on an extended insulated valve stem, plus turned jarrah grip collars with brass ferrules on the three stub feet ($+0.20\text{ kg}$).

---

### 1. Concept Comparison Table

All prices are **ESTIMATE, AUD, Adelaide, October 2026**.

| Metric | Concept A — Cooper's Dome (Cask-430) | Concept B — Angas 430 (Refined & Locked) | Concept C — Angas Binnacle (Hybrid) |
| :--- | :--- | :--- | :--- |
| **Plan Diameter** | $\varnothing 765\text{ mm}$ (belly) | **$\varnothing 625\text{ mm}$** (shell); $695\text{ mm}$ over handles | $\varnothing 768\text{ mm}$ (blackwood ring) |
| **Stowed Height** | $455\text{ mm}$ (legs off) | **$405\text{ mm}$** (on integrated stub feet) | $410\text{ mm}$ (leg tubes out) |
| **Mass (Stone-Out)** | $42.60\text{ kg}$ (legs & stone out) | **$27.72\text{ kg}$** (stone out, feet on) | $45.00\text{ kg}$ (stone & leg tubes out) |
| **Mass (Ready to Cook)** | $52.60\text{ kg}$ (with tripod & stone) | **$33.82\text{ kg}$** (table mode); $37.22\text{ kg}$ w/ tripod | $54.00\text{ kg}$ (ready with stone & legs) |
| **One-Person Lift?** | No ($42.6\text{ kg}$ requires two people) | **Yes** ($27.72\text{ kg}$ via jarrah side handles) | No ($45.0\text{ kg}$ requires two people) |
| **Sits on Shark Tailgate?** | No ($\varnothing 765 > 517\text{ mm}$ depth) | **No** ($\varnothing 625 > 517\text{ mm}$ depth; also violates $300\text{ mm}$ AS/NZS 5601.1 ute clearance) | No ($\varnothing 768 > 517\text{ mm}$ depth) |
| **Heat-Up (to $450^\circ\text{C}$ stone)** | $24\text{–}28\text{ min}$ ($6.8\text{ kW}$ burner) | **$22\text{–}25\text{ min}$** ($5.8\text{ kW}$ burner, $6.10\text{ kg}$ stone) | $26\text{–}30\text{ min}$ ($6.5\text{ kW}$, $\varnothing 450$ stone) |
| **Shell Temp a Hand Meets** | $44.7^\circ\text{C}$ wood staves; $<38^\circ\text{C}$ handles | **$54.5^\circ\text{C}$ crown**, **$61.8^\circ\text{C}$ wall**, **$<38^\circ\text{C}$ jarrah handles/knob/feet** | $42^\circ\text{C}$ wood ring ($78.5^\circ\text{C}$ inner face if choked) |
| **Durability on Dirt Road** | Fair: 24 dry-coopered staves move seasonally across $382\text{ mm}$ radius; hoops need retightening | **Excellent:** All-304 double skin, CalSil compression shell, V-channel locked brass cinch band, stone stowed in padded bag | Good, but heavy ($45\text{ kg}$) on M10 standoff brackets; pebbles can foul the $15\text{ mm}$ air gap |
| **Safety (Gas, Touch, Ute)** | Certified gas w/ FFD; wood inner face $69.3^\circ\text{C}$ ($<80^\circ\text{C}$ limit); ground tripod keeps $>1\text{ m}$ from ute | **Zero combustible material in thermal stack; certified FFD gas train; crown $<55^\circ\text{C}$; camp table or tripod $>1\text{ m}$ from ute** | Certified gas w/ FFD; relies on $15\text{ mm}$ air slot staying unblocked ($78.5^\circ\text{C}$ choked margin is $1.5^\circ\text{C}$ from $80^\circ\text{C}$ limit) |
| **Heirloom Character** | High: 24-stave blackwood barrel & brass hoops | **High: Brushed 304 dome, $35 \times 3\text{ mm}$ C26000 brass equatorial band, quarter-sawn jarrah handles/knobs with turned brass ferrules** | High: Marine binnacle aesthetic, blackwood drum around stainless cupola |
| **Build Difficulty (Makerspace + Uni Shop)** | Very High: 24 compound-bevel staves + custom tapered hoops + Uni sheet-metal crown | **Moderate-High:** Makerspace woodwork/lathe/laser templates; University workshop 304 rolling, bead-rolling & TIG | High: Requires building both a complete stainless oven AND a coopered blackwood drum |
| **AUD Cost Band (ESTIMATE, Oct 2026)** | $\$980\text{–}\$1,120\text{ AUD}$ | **$\$530\text{–}\$845\text{ AUD}$** | $\$920\text{–}\$1,150\text{ AUD}$ |

**Recommendation:** Model and build the refined **Concept B (Angas 430)**—a one-person ($27.72\text{ kg}$ stone-out) double-skin 304 stainless dome cinched at the equator by a V-channel-keyed $35 \times 3\text{ mm}$ brass band with quarter-sawn jarrah and brass at every human touchpoint—which refuses to carry $20\text{ kg}$ of structural timber insulation or cook dangerously on a $517\text{ mm}$ ute tailgate.

---

### 2. Locked Dimensions for CAD Modelling & Mass Delta

#### Locked CAD Parameters (All Dimensions in Millimetres)

```text
// 1. HEARTH & CHAMBER GEOMETRY
floor_stone_diameter           = 430.0   // One-piece (or optional 2-piece D-split) cordierite
floor_stone_thickness          = 20.0    // Density 2100 kg/m3, mass 6.10 kg
inner_chamber_diameter         = 470.0   // 1.2 mm 304 stainless cylinder to springline
inner_chamber_springline_z     = 95.0    // Vertical wall height above stone top face
inner_chamber_apex_z           = 165.0   // Dome crown height above stone top face (70 mm dome rise)
burner_slot_arc_angle_deg      = 110.0   // Rear-left curved slot in stainless deck pan
burner_slot_radial_width       = 32.0    // Stone offset +12 mm toward front-right (8 mm opp. gap)

// 2. MOUTH & FRONT LANDING
mouth_width                    = 420.0   // 19.5 mm clearance per side for 381 mm (15") pizza
mouth_height                   = 95.0    // Flush with chamber springline
mouth_corner_radius            = 25.0    // Top left and right corners
mouth_to_apex_ratio            = 0.576   // 95.0 / 165.0 (70 mm flame hood pocket)
mouth_tunnel_depth_centerline  = 77.4    // Through sidewall stack at front centerline
peel_landing_lip_width         = 420.0   // 1.5 mm 304 stainless sill extension outside mouth
peel_landing_lip_projection    = 45.0    // Projects forward of outer shell plane at z = 0

// 3. INSULATION & SHELL STACKS
inner_liner_thickness          = 1.2     // 304 stainless steel (all hot-face sheets)
outer_skin_thickness           = 1.2     // 304 stainless steel (brushed orbital finish)
floor_calsil_thickness         = 50.0    // 2x 25 mm Calcium Silicate board (250 kg/m3) under stone
floor_aes_thickness            = 25.0    // 1x 25 mm AES blanket (128 kg/m3) under CalSil
sidewall_aes_thickness         = 50.0    // 2x 25 mm AES blanket against inner liner
sidewall_calsil_thickness      = 25.0    // 1x 25 mm slotted/kerfed CalSil backing board
crown_aes_thickness            = 100.0   // 4x 25 mm AES blanket (gives 54.5 C crown skin)

// 4. OUTER BODY & EQUATORIAL CINCH JOINT
outer_body_diameter            = 625.0   // 470 + 2*(1.2 + 50 + 25 + 1.2) = 624.8 -> 625.0 mm
parting_line_height_from_base  = 115.0   // 20 mm above stone top plane (clears stone for removal)
rim_flange_bead_projection     = 6.0     // Rolled outward on both upper and lower 1.2 mm skins
internal_spigot_sleeve_height  = 20.0    // 1.2 mm 304 sleeve welded inside lower pan, 10 mm overlap
equatorial_gasket_diameter     = 10.0    // Braided ceramic/E-glass rope compressed in spigot step
brass_band_width               = 35.0    // C26000 half-hard brass strip
brass_band_thickness           = 3.0     // Rolled to ID 626 mm
v_channel_keeper_count         = 6       // 50 mm long x 14 mm wide x 8 mm deep 1.5 mm 304 clips
toggle_lock_pin_diameter       = 5.0     // Captive stainless ball-lock detent pin for night lock

// 5. JARRAH HANDLES & TOUCH HARDWARE
side_handle_timber_diameter    = 34.0    // Quarter-sawn jarrah (840 kg/m3), turned on metal lathe
side_handle_grip_length        = 240.0   // 280 mm overall with two 20 mm C36000 brass ferrules
side_handle_standoff_clearance = 35.0    // Knuckle clearance to outer 304 skin (bolted to lower pan)
plan_width_over_handles        = 695.0   // 625.0 + 2*(35.0) across side handle outer faces
control_knob_diameter          = 48.0    // Turned jarrah + brass ferrule on Rear-Left valve box

// 6. LEGS, TRIPOD & STOWED ENVELOPE
body_shell_height              = 340.0   // Base pan bottom to outer crown apex
stub_foot_height               = 65.0    // 3x fixed/bayonet stub legs w/ jarrah collars & Viton pads
under_pan_valve_box_drop       = 55.0    // Protected 10 mm above stub foot bottom plane
stowed_height_total            = 405.0   // 340.0 + 65.0 (112 mm margin under 517 mm Shark 6 tub)
stowed_plan_footprint          = 695.0   // Fits easily inside 1224 mm width between Shark 6 arches
optional_tripod_working_height = 780.0   // 3x 750 mm x OD 31.8 x 1.6 mm 304 bayonet leg tubes
```

#### Mass Delta from Concept B Baseline ($25.76\text{ kg} \rightarrow 27.72\text{ kg}$)

| Change vs. Earlier Concept B | Calculation (Volumes & Densities) | Mass Delta |
| :--- | :--- | :--- |
| **Baseline Concept B (Stone-Out)** | $\varnothing 625 \times 315\text{ mm}$ body, $395 \times 90\text{ mm}$ mouth, $75\text{ mm}$ AES crown | **$25.76\text{ kg}$** |
| **1. Widen Mouth ($395 \times 90 \rightarrow 420 \times 95\text{ mm}$)** | $-\Delta A (0.00435\text{ m}^2)$ steel ($-0.083\text{ kg}$) & insulation ($-0.055\text{ kg}$) $+ 35\text{ mm}$ tunnel wrapper ($+0.026\text{ kg}$) | **$-0.11\text{ kg}$** |
| **2. Upgrade Crown ($75\text{ mm} \rightarrow 100\text{ mm}$ AES for $54.5^\circ\text{C}$)** | $+25\text{ mm}$ AES over $0.28\text{ m}^2$ at $128\text{ kg/m}^3$ ($+0.90\text{ kg}$) $+ 25\text{ mm}$ outer 304 skirt at $7900\text{ kg/m}^3$ ($+0.47\text{ kg}$) | **$+1.37\text{ kg}$** |
| **3. Corrugation-Lock Cinch Hardware** | $6\times$ 304 V-channel bead retainers + rolled $6\text{ mm}$ rim flanges + captive $\varnothing 5\text{ mm}$ pin latch | **$+0.28\text{ kg}$** |
| **4. Stolen Heirloom Touch Hardware (from A & C)** | $420 \times 45 \times 1.5\text{ mm}$ 304 peel lip ($+0.22\text{ kg}$) + jarrah/brass valve knob & foot collars ($+0.20\text{ kg}$) | **$+0.42\text{ kg}$** |
| **Locked Design Mass (Stone-Out, One-Person Lift)** | Sum of permanent oven assembly | **$27.72\text{ kg}$** |
| **Cordierite Stone ($\varnothing 430 \times 20\text{ mm}$)** | $\pi \times (0.215\text{ m})^2 \times 0.020\text{ m} \times 2100\text{ kg/m}^3$ (carried in padded canvas bag) | **$+6.10\text{ kg}$** |
| **Locked Design Mass (Ready to Cook, Table Mode)** | Oven ($27.72\text{ kg}$) + Stone ($6.10\text{ kg}$) | **$33.82\text{ kg}$** |

---

### 3. Five Things the CAD Model Must Not Get Wrong

1. **Stone Access via the Equatorial Cinch Joint (Not the Mouth):**
   Do not model the stone as sliding in through the $420 \times 95\text{ mm}$ mouth ($H_{\text{req}} = 111.7\text{ mm} > 95\text{ mm}$). Model the parting line at **$z = 115\text{ mm}$ above the base pan bottom** ($20\text{ mm}$ above the top face of the $20\text{ mm}$ stone) so that when the brass cinch band is unpinned and the upper dome lifts straight up, the top $20\text{ mm}$ of the $\varnothing 430\text{ mm}$ stone stands exposed above the lower inner pan rim (or provide two $25 \times 15\text{ mm}$ finger-hook notches in the stainless stone retaining ring) so bare hands can lift the cold stone straight up before driving.

2. **Differential Thermal Expansion Between the $500^\circ\text{C}$ Inner Liner and $60^\circ\text{C}$ Outer Skin:**
   At $\alpha_{304} = 17.2 \times 10^{-6}\text{ K}^{-1}$, the $\varnothing 470\text{ mm}$ inner liner expands radially by $\Delta R = 235 \times 17.2 \times 10^{-6} \times 480 = 1.94\text{ mm}$ ($\Delta D = 3.88\text{ mm}$) relative to the outer shell, and grows vertically by $1.36\text{ mm}$. **Never weld the inner dome crown rigidly to the outer dome crown, and never weld the mouth tunnel solidly across both skins without a slip joint.** The mouth tunnel wrapper must be TIG-welded to the inner liner and telescope with a $3\text{ mm}$ slip overlap (sealed with $\varnothing 6\text{ mm}$ ceramic rope) behind the outer skin's hemmed mouth flange. The upper dome inner liner hangs from three slotted tangential 304 tab brackets with M6 shoulder bolts and wave washers.

3. **Certified Gas Train Only (No Custom Jets, No Deleted FFD, Zero Zinc in the Hot Path):**
   Model the rear-left under-pan mounting bay to accept a **bought, AGA-certified 5.5–6.5 kW LPG curved/tubular oven burner assembly complete with factory venturi/injector, thermocouple, piezo igniter, and Flame-Failure Device (FFD) gas control valve**, coupled to an Australian **LCC27 $2.75\text{ kPa}$ regulator and AS/NZS 1869 Class A hose**. Do not model a home-drilled brass orifice, and specify 100% 304/316 stainless fasteners (M5/M6 A2-70/A4-80) inside the casing—zero zinc-plated or galvanised hardware anywhere near the burner or casing.

4. **Wood Movement Isolated Strictly to the Unconstrained Handles and Knobs:**
   Quarter-sawn jarrah ($\varnothing 34 \times 240\text{ mm}$) shrinks and swells tangentially/radially by $\approx 0.4\text{ mm}$ with Adelaide seasonal humidity and rain. In the CAD model, the central $\varnothing 10\text{ mm}$ 304 through-rod passing through each jarrah handle must clamp against **internal shoulders on the two stainless standoff brackets** (leaving $1.5\text{ mm}$ axial end-float inside the $20\text{ mm}$ deep C36000 brass ferrules cushioned by an EPDM O-ring), so the timber is never crushed axially or split when wet.

5. **The BYD Shark 6 Tailgate Geometry and Clearance Reality:**
   The BYD Shark 6 lowered tailgate is $517\text{ mm}$ deep; this oven has a $\varnothing 625\text{ mm}$ shell and a $430\text{ mm}$ foot-circle diameter. Even if the three feet were pushed inward to sit on $517\text{ mm}$ of sheet metal, firing a $5.8\text{ kW}$ gas oven on the tailgate violates the **AS/NZS 5601.1 $300\text{ mm}$ rear/side clearance** to the ute's composite tub liner, tail-lights, and wiring harness. Model the three lower leg sockets to accept both:
   - **Short $65\text{ mm}$ stub feet** (for stowing in the $1224\text{ mm}$ wide $\times 517\text{ mm}$ deep tub with $112\text{ mm}$ vertical margin under the tonneau, and for cooking on a heavy steel/aluminium camp table), and
   - **Three $750\text{ mm}$ bayonet-locking $\varnothing 31.8 \times 1.6\text{ mm}$ 304 tripod tubes** ($12^\circ$ splay, $780\text{ mm}$ stone height) so the oven stands independently on the ground $>1.0\text{ m}$ clear of the Shark 6.

---

### 4. Open Questions for Adib (Maximum 8)

Each answer directly locks a CAD dimension or a purchase before cutting metal:

1. **Specific Donor Gas Burner Selection (Changes burner slot radius and under-pan valve box cutout):**
   Do you want to buy the **Gozney Roccbox/Arc replacement LPG burner + FFD assembly** ($\approx \$215\text{ AUD}$ ESTIMATE, rear-entry vertical flame throw) or a **Bromic / commercial $6.0\text{ kW}$ curved tubular burner + SIT 800/Pelican FFD valve kit** ($\approx \$185\text{ AUD}$ ESTIMATE, $110^\circ$ side-rear arc slot)? We must hold the physical burner in hand and measure it before cutting the deck pan slot.
2. **One-Piece vs. Two-Piece Split Cordierite Stone (Changes stone-retaining ring geometry):**
   A one-piece $\varnothing 430 \times 20\text{ mm}$ stone ($6.10\text{ kg}$) requires unpinning the brass cinch band and lifting the $13.2\text{ kg}$ upper crown to remove the stone for transport. If we cut the stone into **two semi-circular D-halves ($430 \times 215 \times 20\text{ mm}$, $3.05\text{ kg}$ each)**, each half slides straight out the $420 \times 95\text{ mm}$ mouth without opening the cinch band, at the cost of a hairline center seam across the deck. Which do you prefer?
3. **University Workshop Dome-Forming Process (Changes crown gore segmentation in CAD):**
   Does your university engineering workshop have a **power slip-roller + rotary jenny/bead roller** that can roll a 6-gore lobster-back/petal crown in $1.2\text{ mm}$ 304 stainless for TIG welding and planishing, or do you want the upper outer crown designed as a **rolled $1.2\text{ mm}$ cylinder wall meeting a shallow conical/spun-dish cap**?
4. **Wood-Fire Option Deletion (Locks out top flue chimney penetration):**
   All three concepts deleted auxiliary wood burning to avoid cutting a chimney hole through the crown insulation (which ruins the gas ceiling flame roll and adds soot/ash cleanup in the ute). Confirm that **100% LPG gas (zero wood fire)** is locked.
5. **Primary Cooking Support on Site (Changes whether we build the $3.40\text{ kg}$ tripod tube set now):**
   Will you set the oven on a camp table you already carry in the Shark 6 (using only the $65\text{ mm}$ stub feet), or should we include the **three $750\text{ mm}$ $\varnothing 31.8\text{ mm}$ 304 stainless bayonet tripod legs** in the initial build?
6. **Timber Species in Your Stash (Changes handle/knob density and lathe blank sizes):**
   We specified reclaimed **quarter-sawn Jarrah** ($\rho \approx 840\text{ kg/m}^3$) for the two $280\text{ mm}$ side handles, valve knob, and foot collars. Do you already have seasoned $45 \times 45\text{ mm}$ Jarrah, River Red Gum ($\rho \approx 920\text{ kg/m}^3$), or Tasmanian Blackwood ($\rho \approx 640\text{ kg/m}^3$) in your shed?
7. **Built-In Dial Thermometer Placement (Changes binnacle boss hole in upper shell):**
   Do you want a mechanical bi-metal dial thermometer ($\varnothing 52\text{ mm}$ face, $150\text{ mm}$ probe reading ambient cavity gas temperature) mounted in a turned brass boss on the front-right upper dome, or do you rely strictly on a handheld IR thermometer gun on the cordierite stone and prefer an unbroken stainless dome?
8. **Tub Tie-Down Interface in the BYD Shark 6 (Changes lower pan eye-nuts):**
   Do you want the oven to strap directly to the Shark 6's floor tie-down points using **four M8 304 stainless lifting eyes** bolted to the lower pan base ring, or will it ride inside a dedicated plywood/canvas cradle box bolted to a tub slide?
