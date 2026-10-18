# Interference, Parameter, and View Inspection Report — Morning & Moondancer

## 1. Summary

Both early Angas prototypes — **Morning** (blackwood stave body, stainless base pan, brass cinch band, brass ferrules, jarrah feet) and **Moondancer** (aluminium skin and base pan, stainless cinch band, no ferrules, rubber feet) — were rebuilt in headless FreeCAD (`freecadcmd` 1.1.4) from `cad/freecad/build_variant.py` and checked against all pass criteria:

| Metric | Morning | Moondancer | Limit / Target |
|---|---|---|---|
| Fabricated solids | 41 | 37 | Burner allowance excluded |
| Total pairwise boolean checks | 820 | 666 | All pairs $(i < j)$ |
| Unintended interferences ($\ge 1.0\text{ mm}^3$) | **0** | **0** | $< 1.0\text{ mm}^3$ |
| Intended press fits ($\ge 1.0\text{ mm}^3$) | **8** | **4** | Named below with volumes |
| Non-zero overlaps in $(10^{-6}, 1.0)\text{ mm}^3$ | **0** | **0** | Zero residual slivers |
| FreeCAD fabricated mass | $17.268\text{ kg}$ | $13.717\text{ kg}$ | Analytical: $17.256\text{ kg}$ / $13.738\text{ kg}$ |
| Ready mass (with $1.85\text{ kg}$ burner allowance) | **$19.118\text{ kg}$** | **$15.567\text{ kg}$** | $\le 20.0\text{ kg}$ |
| Outer diameter / Body height | $\varnothing 571.8\text{ mm}$ / $260.1\text{ mm}$ | $\varnothing 546.8\text{ mm}$ / $247.7\text{ mm}$ | $> 517\text{ mm}$ tailgate deck |
| Stone $\varnothing 420 \times 15\text{ mm}$ radial pizza clearance | $19.5\text{ mm}$ | $19.5\text{ mm}$ | $\ge 19.5\text{ mm}$ |
| Burner crescent clearance to stone / liner | $5.657\text{ mm}$ / $4.000\text{ mm}$ | $5.657\text{ mm}$ / $4.000\text{ mm}$ | $> 0\text{ mm}$ (clear of both) |
| Temperatures (outer / inner wood / under / grip) | $50.0^\circ\text{C}$ / $65.0^\circ\text{C}$ / $60.0^\circ\text{C}$ / $25.3^\circ\text{C}$ | $55.0^\circ\text{C}$ / — / $60.0^\circ\text{C}$ / $26.2^\circ\text{C}$ | Within all thermal ceilings |

---

## 2. Pairwise Common Volume Table ($\ge 1.0\text{ mm}^3$)

Every pair of fabricated solids (`kind != "allowance"`) was intersected in 3D via `a.Shape.common(b.Shape).Volume`. Face-to-face contacts (`distToShape == 0.0 mm`, `Volume == 0.0 mm3`) are excluded as required.

### 2.1 Initial Audit (Before Fixes)

Before editing `cad/freecad/build_variant.py`, running the pairwise boolean check on the initial script exposed **14 overlapping pairs on Morning** and **16 overlapping pairs on Moondancer**, plus missing press fits and floating parts:
- `post-{port,starboard}-{a,b}` $\leftrightarrow$ `washer-{port,starboard}-{a,b}`: **$84.8230\text{ mm}^3$** each (4 pairs per variant). The posts ran the full `standoff` ($16\text{ mm}$) through the $3\text{ mm}$ PTFE washers instead of seating against the washer inner face.
- `post-{port,starboard}-{a,b}` $\leftrightarrow$ `outer-dome`: **$0.0\text{ mm}^3$ with a $0.900\text{ mm}$ gap (Morning) and $0.154\text{ mm}$ gap (Moondancer)** because the posts started at `x = ±hr` at `y = ±40 mm` rather than projecting onto the curved dome surface at $x = \pm\sqrt{r_{\text{dome}}(z_h)^2 - y_{\text{post}}^2}$.
- `outer-dome` $\leftrightarrow$ `rack-boss-{0..3}`: **$19.0947\text{ mm}^3$** (Morning) and **$16.3124\text{ mm}^3$** (Moondancer) each (4 pairs per variant). The bosses were plain cylinders placed at $z(r_{\text{boss}})$ whose outer corners plunged into the curved dome shell.
- `outer-skirt` $\leftrightarrow$ `mouth-frame`: **$90.1554\text{ mm}^3$** (Morning) and **$88.1615\text{ mm}^3$** (Moondancer). A flat box at $y = -(\text{outer\_r} + 1.5)$ sliced chords through the cylindrical skirt while its outer corners floated in front of the shell.
- `mouth-frame` $\leftrightarrow$ `peel-landing`: **$504.0000\text{ mm}^3$** (Morning) and **$567.0000\text{ mm}^3$** (Moondancer). Both occupied the lower mouth border simultaneously, and the rectangular `peel-landing` floated $62.9\text{ mm}$ (Morning) / $50.4\text{ mm}$ (Moondancer) away from the curved outer skirt at $x = \pm 210\text{ mm}$.
- `wall-insulation` $\leftrightarrow$ `dowel-{a,b}` (Moondancer): **$23.5056\text{ mm}^3$** each (2 pairs) because the $2.0\text{ mm}$ embed depth exceeded Moondancer's $0.8\text{ mm}$ aluminium skin and poked $1.2\text{ mm}$ into the microporous insulation board.
- `handle-{port,starboard}` $\leftrightarrow$ `ferrule-{port,starboard}-{a,b}` (Morning): **$0.0\text{ mm}^3$ with a $0.200\text{ mm}$ radial clearance gap** because the ferrule bore radius was cut at $11.2\text{ mm}$ around an $11.0\text{ mm}$ radius jarrah grip instead of a press fit.
- `burner-envelope` $\leftrightarrow$ `liner-skirt`: **$146.664\text{ mm}^3$** because the rectangular box at $y \in [-80, +140]\text{ mm}$ clipped the curved $\varnothing 470\text{ mm}$ liner wall.

### 2.2 Final Audit (After Fixes — All Pairs $\ge 1.0\text{ mm}^3$)

#### Morning (41 fabricated solids, 820 pairs checked)

| Solid A | Material A | Solid B | Material B | Common Volume ($\text{mm}^3$) | Classification |
|---|---|---|---|---:|---|
| `outer-skirt` | `blackwood` | `dowel-a` | `ss` | `39.2162` | Intended press fit (cinch dowel into blackwood skin, $2.0\text{ mm}$ depth) |
| `outer-skirt` | `blackwood` | `dowel-b` | `ss` | `39.2162` | Intended press fit (cinch dowel into blackwood skin, $2.0\text{ mm}$ depth) |
| `cinch-band` | `brass` | `dowel-a` | `ss` | `23.5621` | Intended press fit (cinch dowel through $1.2\text{ mm}$ brass band) |
| `cinch-band` | `brass` | `dowel-b` | `ss` | `23.5621` | Intended press fit (cinch dowel through $1.2\text{ mm}$ brass band) |
| `handle-port` | `jarrah` | `ferrule-port-a` | `brass` | `109.5788` | Intended press fit (brass ferrule on jarrah grip, $0.2\text{ mm}$ radial interference) |
| `handle-port` | `jarrah` | `ferrule-port-b` | `brass` | `109.5788` | Intended press fit (brass ferrule on jarrah grip, $0.2\text{ mm}$ radial interference) |
| `handle-starboard` | `jarrah` | `ferrule-starboard-a` | `brass` | `109.5788` | Intended press fit (brass ferrule on jarrah grip, $0.2\text{ mm}$ radial interference) |
| `handle-starboard` | `jarrah` | `ferrule-starboard-b` | `brass` | `109.5788` | Intended press fit (brass ferrule on jarrah grip, $0.2\text{ mm}$ radial interference) |

*All other 812 pairs on Morning have $0.0000\text{ mm}^3$ common volume.*

#### Moondancer (37 fabricated solids, 666 pairs checked)

| Solid A | Material A | Solid B | Material B | Common Volume ($\text{mm}^3$) | Classification |
|---|---|---|---|---:|---|
| `outer-skirt` | `al` | `dowel-a` | `ss` | `15.6518` | Intended press fit (cinch dowel into $0.8\text{ mm}$ aluminium skin) |
| `outer-skirt` | `al` | `dowel-b` | `ss` | `15.6518` | Intended press fit (cinch dowel into $0.8\text{ mm}$ aluminium skin) |
| `cinch-band` | `ss` | `dowel-a` | `ss` | `15.7081` | Intended press fit (cinch dowel through $0.8\text{ mm}$ stainless band) |
| `cinch-band` | `ss` | `dowel-b` | `ss` | `15.7081` | Intended press fit (cinch dowel through $0.8\text{ mm}$ stainless band) |

*All other 662 pairs on Moondancer have $0.0000\text{ mm}^3$ common volume.*

---

## 3. Intended Press-Fit List

Only the two expected press-fit families exist in the final models:

1. **Morning Brass Ferrules on Jarrah Grips (`handle-{port,starboard}` $\leftrightarrow$ `ferrule-{port,starboard}-{a,b}`):**
   - Grip outer diameter: $\text{grip\_d} = 22.0\text{ mm}$ ($r_{\text{grip}} = 11.0\text{ mm}$).
   - Ferrule outer diameter: $\text{ferrule\_od} = 26.0\text{ mm}$ ($r_{\text{out}} = 13.0\text{ mm}$), length $\text{ferrule\_len} = 8.0\text{ mm}$.
   - Radial press interference: $\text{ferrule\_press} = 0.2\text{ mm}$ ($r_{\text{bore}} = r_{\text{grip}} - \text{ferrule\_press} = 10.8\text{ mm}$).
   - Analytical overlap volume per ferrule: $\pi (11.0^2 - 10.8^2) \times 8.0 = 109.5788\text{ mm}^3$. FreeCAD boolean common volume: **$109.5788\text{ mm}^3$** ($\times 4$ ferrules on Morning; absent on Moondancer).

2. **Cinch Dowels Through the Cinch Band Into the Outer Skin (`dowel-{a,b}` $\leftrightarrow$ `cinch-band` and `outer-skirt`):**
   - Dowel pin diameter: $\text{dowel\_d} = 5.0\text{ mm}$ ($r_{\text{dowel}} = 2.5\text{ mm}$, cross-sectional area $\pi r_{\text{dowel}}^2 = 19.6350\text{ mm}^2$), located at $\theta \in \{140^\circ, 220^\circ\}$ at the band mid-height $z = \text{band\_z} + \text{band\_w}/2$.
   - **Through `cinch-band`:**
     - Morning ($1.2\text{ mm}$ brass band): $19.6350 \times 1.2 = \mathbf{23.5621\text{ mm}^3}$ per dowel.
     - Moondancer ($0.8\text{ mm}$ stainless band): $19.6350 \times 0.8 = \mathbf{15.7081\text{ mm}^3}$ per dowel.
   - **Into `outer-skirt`:**
     - Seated to $\min(\text{dowel\_skin\_depth}, \text{skin\_t})$ and trimmed against the inner skin cylinder $r = \text{skin\_r}$ so the pin never enters the microporous wall insulation:
     - Morning ($2.0\text{ mm}$ blind seat in $8.0\text{ mm}$ blackwood stave): **$\mathbf{39.2162\text{ mm}^3}$** per dowel.
     - Moondancer ($0.8\text{ mm}$ seat in $0.8\text{ mm}$ aluminium skin): **$\mathbf{15.6518\text{ mm}^3}$** per dowel.

---

## 4. Shared Parameter Block and Derived Placement Expressions

All hardware dimensions and named geometric parameters live in the single shared parameter block `HARDWARE` (aliased as `PARAMS`, with top-level named constants `HANDLE_ALPHA` and `EXPLODE_LIFT`) in `cad/freecad/build_variant.py`:

```python
HARDWARE = {
    "handle_alpha": math.radians(50.0),
    "grip_d": 22.0,
    "grip_len": 130.0,
    "post_d": 6.0,
    "post_end_inset": 25.0,
    "post_seat_embed": 2.0,
    "washer_d": 16.0,
    "washer_t": 3.0,
    "ferrule_od": 26.0,
    "ferrule_len": 8.0,
    "ferrule_press": 0.2,
    "dowel_d": 5.0,
    "dowel_len": 14.0,
    "dowel_skin_depth": 2.0,
    "dowel_angles": (140.0, 220.0),
    "band_clearance": 2.0,
    "frame_t": 0.8,
    "frame_border": 12.0,
    "frame_inset": 2.0,
    "throat_t": 0.6,
    "landing_depth": 40.0,
    "lip_h": 12.0,
    "burner_clear": 4.0,
    "burner_h": 24.0,
    "burner_span_ratio": 220.0 / 420.0,
    "foot_pcd_ratio": 0.72,
    "foot_angles": (30.0, 150.0, 270.0),
    "foot_wood_d": 28.0,
    "foot_wood_h": 12.0,
    "foot_rubber_d": 30.0,
    "foot_rubber_h": 8.0,
    "rack_pcd": 120.0,
    "rack_boss_d": 12.0,
    "rack_boss_h": 6.0,
    "rack_angles": (45.0, 135.0, 225.0, 315.0),
    "stand_pitch": 220.0,
    "stand_boss_d": 14.0,
    "stand_boss_h": 8.0,
    "explode_lift": 80.0,
}
```

Every part placement is derived from the shared cooking constants (`CHAMBER_D`, `SKIRT_H`, `DOME_RISE`, `MOUTH_W`, `MOUTH_H`), the solver design vector (`liner_t`, `ins_t`, `skin_t`, `base_t`, `floor_ins`, `pan_t`, `stone_t`, `stone_d`, `band_t`, `band_w`, `standoff`), and `HARDWARE`:

- **Radial and vertical datum stations:**
  - $r = \text{CHAMBER\_D} / 2$, $\text{stack} = \text{liner\_t} + \text{ins\_t} + \text{skin\_t}$, $\text{outer\_r} = r + \text{stack}$
  - $\text{hearth} = \text{base\_t} + \text{floor\_ins} + \text{pan\_t} + \text{stone\_t}$, $\text{spring} = \text{hearth} + \text{SKIRT\_H}$
- **Stone shift and burner crescent:**
  - $\text{stone\_r} = \text{stone\_d} / 2$, $\text{stone\_shift} = (r - \text{stone\_r}) - \text{stone\_t}$ (shifts the stone $+10\text{ mm}$ to starboard so the port crescent is $35\text{ mm}$ wide while keeping $15\text{ mm}$ starboard clearance).
  - The burner allowance envelope is a curved crescent shell between $\text{stone\_r} + \text{burner\_clear}$ (centred at $x = \text{stone\_shift}$) and $r - \text{burner\_clear}$ (centred at $x = 0$) on the port side, maintaining $\ge 4.0\text{ mm}$ clearance to the liner and $5.657\text{ mm}$ to the stone.
- **Mouth cutter, conformal mouth frame, throat sleeve, and contoured peel landing:**
  - Mouth cutter depth: $(\text{outer\_r} - \sqrt{r^2 - (\text{MOUTH\_W}/2)^2}) + \text{stack}$, starting at $y = -(\text{outer\_r} + 0.5\,\text{stack})$, ensuring the full $420 \times 95\text{ mm}$ mouth opens cleanly through all three skirt layers to the inner chamber wall.
  - Peel landing: spans $x \in [-\text{MOUTH\_W}/2, +\text{MOUTH\_W}/2]$, $z \in [\text{hearth} - \text{base\_t}, \text{hearth}]$, from $y = -(\text{outer\_r} + \text{landing\_depth})$ to $y = -\sqrt{\text{outer\_r}^2 - (\text{MOUTH\_W}/2)^2}$, boolean-contoured against the outer cylinder `outer_r` so its rear edge mates flush against the outer skirt across the full $420\text{ mm}$ width.
  - Mouth frame: a conformal cylindrical faceplate ($r \in [\text{outer\_r}, \text{outer\_r} + \text{frame\_t}]$, border $\text{frame\_border}$, opening inset $\text{frame\_inset}$) trimmed against `peel-landing` and `cinch-band` and fused with the $\text{throat\_t} = 0.6\text{ mm}$ stainless throat tunnel lining the mouth cut through `stack`.
- **Cinch band and road dowels:**
  - $\text{band\_z} = \text{spring} - \text{band\_w} - \text{band\_clearance}$, dowel height $z = \text{band\_z} + \text{band\_w}/2$, dowel radial start $r_0 = \text{outer\_r} - \min(\text{dowel\_skin\_depth}, \text{skin\_t})$ trimmed by the inner skin surface $r = \text{skin\_r}$.
- **Handles, posts, washers, and ferrules:**
  - Shoulder station at angle $\alpha = \text{handle\_alpha}$: $z_h = \text{spring} + \text{DOME\_RISE}\sin\alpha$, $r_h = r_{\text{skin\_outer}}(z_h)$.
  - Grip axis: $x_{\text{grip}} = \pm(r_h + \text{standoff} + \text{grip\_d}/2)$, $y \in [-\text{grip\_len}/2, +\text{grip\_len}/2]$, $z = z_h$.
  - Ferrules (Morning): placed at the two grip ends $y_0 \in \{-\text{grip\_len}/2,\; +\text{grip\_len}/2 - \text{ferrule\_len}\}$ with bore radius $\text{grip\_d}/2 - \text{ferrule\_press}$.
  - Posts and PTFE washers: located at $y_{\text{post}} = \pm(\text{grip\_len}/2 - \text{post\_end\_inset})$. Each PTFE washer spans $x \in [r_h + \text{standoff} - \text{washer\_t},\; r_h + \text{standoff}]$ so its outer face is tangent to the grip at $r_h + \text{standoff}$. Each stainless post starts inside the local dome surface at $x_{\text{surf}} = \sqrt{r_h^2 - y_{\text{post}}^2} - \text{post\_seat\_embed}$, ends at the washer inner face $r_h + \text{standoff} - \text{washer\_t}$, and is boolean-trimmed by `_dome_volume(skin_o)` to form an exact saddle seat on the dome skin.
- **Feet, rack bosses, stand bosses, and exploded crown lift:**
  - Feet: placed on pitch circle radius $\text{outer\_r} \times \text{foot\_pcd\_ratio}$ at $z \in [-\text{foot\_h}, 0]$ abutting `base-pan`.
  - Top rack bosses: 4×M5 bosses placed on radius $\text{rack\_pcd}/2$ at angles $\text{rack\_angles}$, starting below the local dome profile $z(r_{\text{rack}} + r_{\text{boss}})$ to $z(r_{\text{rack}}) + \text{rack\_boss\_h}$ and boolean-trimmed against `_dome_volume(skin_o)` for a flush saddle seat on the crown.
  - Stand bosses: 4×M6 bosses at $(\pm\text{stand\_pitch}/2,\; \pm\text{stand\_pitch}/2)$ under `base-pan` at $z \in [-\text{stand\_boss\_h}, 0]$.
  - Exploded STEP crown lift: translates all `crown=True` parts by $+Z = \text{EXPLODE\_LIFT}$.

*Parametric verification test:* We ran `build("morning", {"standoff": 28.0, "band_w": 18.0, "grip_len": 160.0})` in `freecadcmd` and verified that the grip moved to $y \in [-80, +80]\text{ mm}$ at $x_{\text{inner}} = -303.08\text{ mm}$, the ferrules moved to $[-80, -72]\text{ mm}$ and $[+72, +80]\text{ mm}$, the posts and washers moved to $y = \pm 55.0\text{ mm}$ with washer outer faces at $x = -303.08\text{ mm}$, and the cinch band and dowels automatically tracked the $18.0\text{ mm}$ band width.

---

## 5. PNG Rendering and Visual Inspection Notes

Four standalone PNGs (`front.png`, `side.png`, `top.png`, `section.png`) were rendered for both Morning and Moondancer and inspected visually. Below is what we observed across our iterations and what we changed after looking:

1. **Iteration 1 — Camera Orientation and Mislabelled Views (`TechDraw.projectToSVG` Axes):**
   - *What we saw:* In the original `build_variant.py`, `_write_sheets` called `TechDraw.projectToSVG(compound, App.Vector(0, 1, 0))` for `"front"`. Because OpenCASCADE's HLR projector chooses its 2D projection frame with $+Z$ mapped horizontally when given a $+Y$ direction vector, the original `"front"` view rendered the oven rotated $90^\circ$ on its side, and the original `"mouth_cutter"` depth (`stack + 24.0`) left two vertical uncut wall edges inside the mouth opening because it failed to reach the inner chamber radius at $x = \pm 210\text{ mm}$.
   - *What we changed:* We explicit-rotated copies of the 3D compound before projecting along $+Z$ (`App.Vector(0, 0, 1)`) so every view has exact, unambiguous screen axes:
     - `front`: rotated $-90^\circ$ about $X$ so screen $+X$ is starboard, screen $-X$ is port, screen $+Y$ (up) is $+Z$, looking directly into the mouth along $+Y$.
     - `side`: rotated $+90^\circ$ about $Z$ then $-90^\circ$ about $X$ so the camera looks from the port side ($-X$) along the hearth toward $+X$, with $+Z$ up and the mouth/peel-landing on the right ($-Y$).
     - `top`: unrotated projection from $+Z$ looking down on the circular XY plan, with the mouth and peel landing at the bottom ($-Y$) and symmetric handles on port ($-X$, left) and starboard ($+X$, right).
     - `section`: cut by a half-space box removing $X < 0$ (the port half) so the cut plane lies squarely on the mouth centreline $X = 0$, viewed from port ($-X$) toward $+X$.
   - We also fixed `_mouth_cutter` so its depth spans $(\text{outer\_r} - \sqrt{r^2 - (\text{MOUTH\_W}/2)^2}) + \text{stack}$, eliminating the vertical wall remnants blocking the left and right sides of the mouth opening.

2. **Iteration 2 — Faceted Polygonal Dome Rings vs. Smooth BSpline Revolution:**
   - *What we saw:* Upon opening the first set of PNGs (`test_front.png`, `test_side.png`, `test_top.png`, `test_section.png`), the 48-segment polyline in `_dome` produced 48 concentric rings across `top.png` (inflating `top.png` to $>260\text{ KB}$) and dense horizontal stripes across the dome in `front.png`, `side.png`, and `section.png`.
   - *What we changed:* We updated `_dome` to interpolate smooth `Part.BSplineCurve` splines through the inner and outer profile points before revolving $360^\circ$. Re-rendering and opening the PNGs confirmed that the 48 facet lines disappeared completely, leaving crisp architectural outlines and reducing every PNG to $2.6\text{ KB}\text{–}3.9\text{ KB}$ (well under the $200\text{ KB}$ threshold).

3. **Iteration 3 — Moondancer Thin-Shell Post Cut Artifact:**
   - *What we saw:* Upon inspecting `moondancer/top.png` and `moondancer/section.png` after Iteration 2, we noticed that `post-port-a` was missing its two horizontal projection lines in `moondancer/top.png` and left a small circular ring inside the dome in `moondancer/section.png`. Inspecting the B-Rep faces in `freecadcmd` revealed why: Moondancer's aluminium outer dome is only $0.8\text{ mm}$ thick, so starting the post $2.0\text{ mm}$ inside `skin_o` and cutting only with the thin shell `outer_dome_shape` left a tiny detached stub inside the inner wall of `outer_dome_shape`!
   - *What we changed:* We added `_dome_volume(skin_o)` (a solid revolution of the outer skin profile down to the $Z$ axis) and trimmed both the handle posts and the crown rack bosses against `dome_solid_envelope`. Re-running and inspecting `moondancer/top.png` and `moondancer/section.png` confirmed that all four posts (`port-a`, `port-b`, `starboard-a`, `starboard-b`) render symmetrically in `top.png` and the stray circle in `section.png` is completely gone.

4. **Final Visual Check of All 8 PNGs:**
   - `morning/front.png` ($2.8\text{ KB}$) & `moondancer/front.png` ($2.8\text{ KB}$): Mouth ($420 \times 95\text{ mm}$) is dead-centre on the front elevation, framed by the conformal mouth frame and peel landing; port and starboard handles, posts, PTFE washers (and Morning's brass ferrules) are a symmetric pair on the dome shoulder; 4×M5 rack bosses sit symmetrically on the crown; 3 feet and 4×M6 stand bosses sit flush under the base pan.
   - `morning/side.png` ($2.8\text{ KB}$) & `moondancer/side.png` ($2.6\text{ KB}$): Looking along the hearth from the port side ($-X$); the port jarrah grip (with brass ferrules at both ends on Morning, plain cylinder on Moondancer) sits centred on the dome shoulder; the cinch band and road dowels sit just below the spring line; the mouth frame and peel landing project cleanly to the right ($-Y$).
   - `morning/top.png` ($3.9\text{ KB}$) & `moondancer/top.png` ($3.9\text{ KB}$): True circular plan ($\varnothing 571.8\text{ mm}$ Morning, $\varnothing 546.8\text{ mm}$ Moondancer); peel landing at the bottom ($-Y$); symmetric port and starboard handles with all four posts and PTFE washers visible; 4×M5 rack bosses on the $\varnothing 120\text{ mm}$ pitch circle at the crown centre; two cinch dowels at $140^\circ$ and $220^\circ$ on the port-rear quadrants.
   - `morning/section.png` ($3.5\text{ KB}$) & `moondancer/section.png` ($3.3\text{ KB}$): Cut cleanly along the mouth centreline ($X = 0$); clearly shows the base pan, floor insulation, stainless stone pan, $\varnothing 420 \times 15\text{ mm}$ cordierite stone, three-layer skirt and dome stack (stainless liner, microporous insulation, blackwood/aluminium outer skin), the $95\text{ mm}$ high mouth opening lined by the stainless throat sleeve, and the peel landing at hearth level.

## 6. Checkout re-run

The scripts in this commit were run again with FreeCAD 1.1.4. Morning came back at 17.268 kg and Moondancer at 13.717 kg. A pairwise common-volume check on the saved documents found the same hits and the same volumes as section 2.2: Morning 820 pairs and 8 press fits, Moondancer 666 pairs and 4 press fits. No other pair reached 1 mm³.