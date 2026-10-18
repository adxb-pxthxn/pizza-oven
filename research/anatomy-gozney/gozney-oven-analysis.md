# Arc Lite, Tread, Dome XL — first engineering pass

Private working paper for Adib. 18 October 2026.

This is a reverse-engineering study of three current Gozney ovens, written so a later open-source design can borrow the physics without borrowing their drawings, photos, or ornamental design. Nothing in this folder belongs in the git repository.

The ovens covered are the ones on sale on Gozney’s Australian site that day: **Arc Lite** (GOZ-3102), **Tread** (GOZ-1893), and **Dome XL Gen 2** (GOZ-2509). Older Dome and Roccbox are mentioned only where a current manual still pairs them with the XL.

---

## 1. How to read this

Published numbers come from Gozney product pages, the oven comparison tool, help-centre articles, UK/EU and US/CA technical manuals, the Australia/New Zealand Dome Gen 2 manual, the Tread specification sheet, and a Dome XL EU specification sheet mirrored by a retailer. Prices are the Australian retail prices shown on au.gozney.com on 18 October 2026.

Three kinds of statement are kept apart:

- **Published.** A figure Gozney or a manual prints.
- **Inferred.** A number derived from published envelopes (side-wall thickness, stone mass, mouth ratio). Gozney has not published insulation thickness, skin temperature, or a section drawing. Treat inferences as bounds, not as a teardown.
- **Modelled.** Steady-state wall temperatures from a one-dimensional calculation in `calcs/wall_model.py`. The repo’s `thermal_model.py` was used as a cross-check. These are design calculations for a future oven, not a claim about a measured Gozney shell.

Where Gozney’s own pages disagree, both numbers are kept and the conflict is named. No insulation thickness, burner jet, or skin temperature below was measured on a physical oven.

A full isometric cutaway of the three products would be an Epic figure and would also sit too close to their design rights. It was not built. The section drawing `gozney-section.svg` is an original sketch of the recommended first oven, with temperatures taken from the model.

---

## 2. The one idea the three ovens share

All three are low, wide chambers with a gas flame that enters from the left and is meant to roll along the ceiling, then leave. Gozney calls this a lateral rolling flame. The manuals say the flame should be yellow or orange and should roll along the top of the oven. That is the portable version of a wood-fired dome: radiation from a hot, sooty vault cooks the top of the pizza, the floor conducts into the base, and the moving gas strips the steam layer off the crust.

The geometry that makes the roll happen is published as three boxes:

| | Arc Lite | Tread | Dome XL Gen 2 |
|---|---:|---:|---:|
| External W × D × H, mm | 430 × 481 × 297 | 418 × 484 × 320 | 946 × 697 × 997 |
| Internal W × D × H, mm | 325 × 355 × 150 | 310 × 380 × 150 | 724 × 543 × 238 |
| Mouth W × H, mm | 325 × 85 | 310 × 85 (spec sheet) | 470 × 140 |
| Mouth height / apex | 0.57 | 0.57 | 0.59 |
| Mouth width / chamber width | 1.00 | 1.00 | 0.65 |
| Inferred side wall, mm | 52.5 | 54 | 111 |

Mouth height over apex is internal mouth height divided by internal chamber height. A traditional Neapolitan rule of thumb is about 0.63. All three Gozney chambers sit a little shorter than that, in the mid-0.50s to high-0.50s. Short enough to hold the gas in, tall enough to get a peel in. The compact ovens are not hemispheres. A 150 mm apex over a 310–325 mm width is a low vault. Radiation view factor to the pizza is high because the ceiling is close. There is also less room for a tall flame, which is why these ovens are fussy in wind: the manuals warn that wind blows the flame down into the dock and can push fire out the back.

The width ratio is the important split.

Arc Lite and Tread open the full width of the chamber. A 12 inch pizza is 305 mm. The published mouth is 310 mm (Tread spec sheet) or 325 mm (Arc Lite). Clearance beside the pizza is a few millimetres to about 10 mm a side. There is nowhere to park a wood fire. The burner is a ribbon on the left wall, above the stone. The Arc Lite manual says to slide the stone in until it touches the back of the core and not to hit the burner on the left.

Dome XL’s mouth is 470 mm inside a 724 mm chamber, about 65% of the width. An 18 inch pizza is 457 mm, so the mouth is sized around the pizza, and the extra chamber width is the fire’s home. The manual tells you to establish the wood fire and push it to the right, over the duct grate, until the flame rolls the roof. That is why this oven can burn wood and the other two are propane-only. The help centre says not to burn wood in Arc Lite, and not to use wood in Tread or convert Tread to natural gas.

External height of the XL is 997 mm, while the shipping carton is only 613 mm tall. The flue pipe, collar, top, and cap are in the box and go on after delivery. The 997 mm figure includes the assembled flue. It is not the height of the steel body alone.

---

## 3. Arc Lite

### What it is for

The cheapest, lightest, smallest current Gozney. One 12 inch pizza, propane only, tabletop. Australian price on 18 October 2026: **AUD $649**. UK price on the comparison tool: £349.99. Gozney’s help centre describes it as the compact everyday oven, and Tread as the one you carry away from home. The comparison tool marks Tread portable and Arc Lite not portable, even though Arc Lite is the lighter machine. “Portable” here means handles, a dock, and a quick-connect hose, not a lower mass.

### Body and manufacture

Help centre, 13 February 2026: stainless steel and die-cast aluminium, high-temperature paint and powder coat, water-soluble insulation, cordierite stone. That is less specific than the Tread and Dome XL spec sheets. There is no published gauge, no statement that the shell is a pressing, and no alloy for the die casting.

What the shape and the weight do say: 12.0 kg for a 430 × 481 × 297 mm body with a stone of about 2.9 kg (see below) leaves roughly 9 kg for steel, aluminium, burner, and insulation. That is a thin pressed or fabricated shell, not a casting of the whole oven. Die-cast aluminium is the landing or dock class of part, the same job the XL spec sheet assigns to a high-pressure die casting. Arc Lite has no user flue in the manual, and the help article that separates it from Arc and Arc XL lists the flue on Arc and Arc XL only.

Inferred side wall 52.5 mm has to hold outer skin, insulation, inner skin, and fit-up. A single insulation layer of roughly 35–45 mm is the only way that envelope works. Gozney’s own comparison calls it **1-layer insulation**. Thickness is still unpublished.

### Floor

12 mm removable cordierite. If the stone fills the published internal floor, 325 × 355 × 12 mm at a typical cordierite density of 2100 kg/m³ is **2.9 kg**. Heating that stone by 480 K at 950 J/kg·K stores **1.3 MJ**. At 3.4 kW and a rough 40% capture into the oven (the rest leaves with the exhaust), the stone alone is about 16 minutes. The comparison tool says 20–30 minutes to temperature, and the manual says to start on high for 20 minutes. The gap between 16 and 20–30 minutes is the liner, the insulation that soaks heat, and a capture fraction worse than 40% while the oven is still cold. The orders of magnitude agree. A 12 mm stone is why it is fast, and why the fourth pizza in a row will be slower than the first: there is little stored heat to recover from.

Cordierite is the right floor material at this temperature. Thermal effusivity sits near 2100 J/m²·K·s^½, close enough to dough that a 480°C floor browns a base in about a minute without the black burn a steel or cast-iron plate gives. The stone is loose. The manual has you slide it in. That is also the correct mechanical detail: a cordierite slab of this size grows about half a millimetre from 20°C to 500°C, while a stainless tray around it grows about 3 mm. Bolting the stone down cracks it. Gozney leaves it floating. Copy that.

### Heat path

Low vault, mouth/apex 0.57, flame from the left along the ceiling, exhaust out the mouth because there is no separate flue. Intake air comes in the lower part of the mouth, which is why the manuals forbid covering the mouth while a flame is lit (carbon monoxide, and a damaged oven). Wind is a first-order problem: orient the mouth downwind, and keep a windbreak more than 450 mm away.

No thermometer. The manual points you at an infrared thermometer for the stone. There is no door. Covering the mouth is prohibited while the burner is on.

### Burner

Lateral gas burner. UK/EU data plate: **3.4 kW (252 g/h)** for the listed propane categories, model GOZ-3102. Injector diameter on that plate changes with the gas category: 0.85 mm at 50 mbar propane, 0.90 mm in the butane/propane mixed category, 0.95 mm at 37 mbar. US/CA plate: 0.95 mm, **11,687 BTU/h** (3.43 kW), propane at 11 inches water column, conforming to ANSI Z21.58 and certified to CSA 1.6.

The comparison tool instead lists **273.8 g/h** and 3.4 kW. 273.8 g/h is the Tread spec-sheet consumption. At a propane lower heating value of 46.4 MJ/kg, 252 g/h is 3.25 kW and 274 g/h is 3.53 kW. At a gross value near 50.4 MJ/kg, 252 g/h is about 3.5 kW. The honest reading: the certified nominal output is **3.4 kW**, the UK plate’s mass-flow partner is **252 g/h**, and the comparison tool has reused Tread’s 273.8 g/h. Do not design from the comparison-tool flow.

Ignition is a push-and-turn dial with a clicking igniter. Hold the dial in for up to 30 seconds “to disengage the Flame Failure Device.” That is a thermoelectric flame-failure valve: the thermocouple has to get hot before it will hold the valve open. If it does not light, turn it off and wait before a retry (the manual says both 3 minutes and, in the warning, 5 seconds then 5 minutes — follow the longer wait). The hose is factory-fitted. The manual says not to disconnect it. Minimum bottle they recommend is 5 kg, because a small canister chokes as it refrigerates itself.

### Safety and service

Placement section: 0.3 m clearance at the back and sides and 1 m at the front from combustible construction. Not under or on a combustible structure. Accessible parts may be very hot. Cool at least 30 minutes before moving. Outdoor only. Do not burn wood. Do not modify sealed parts. Venturi cleaning is a vacuum through the dock with the stone and burner guard out, gas disconnected, oven rolled on its side. There is no published skin temperature. The clearances are the evidence that the shell is not a surface you put against a wall.

Australian certification: the help-centre table dated 23 October 2025 lists Arc, Arc XL, Tread, and Dome Gen 2 / XL for Australia and New Zealand. Arc Lite is absent. The article is older than the February 2026 Arc Lite material note. Before buying one in Australia, read the data plate on the actual unit for an Australian certification mark. A CE or CSA mark is not an Australian acceptance.

### Why it is built this way

Arc Lite is a cost and mass cut of the Arc, not a different cooking theory. Gozney’s own comparison: Arc and Arc XL have two insulation layers, a 20 mm stone, a digital stone thermometer, and a flue. Arc Lite drops to one layer, 12 mm, no gauge, no flue, and a lower burner (Arc is 4.5 kW, Arc XL 5.25 kW on the same tool). Heat-up is quoted as 20–30 minutes against 30–40 for Arc. You are paying less and carrying less, and you get a chamber that cools faster between pizzas and dumps more heat out of the mouth. At AUD $649 it is the number a home-built oven has to beat on purpose, not on price alone.

---

## 4. Tread

### What it is for

Same 12 inch, propane-only cooking job as Arc Lite, engineered to be carried and to cool down so you can pack it. Australian price **AUD $899**. UK £499.99. Oven mass **13.5 kg** on the spec sheet and product page. The placement warning in the US manual says the surface must hold **14 kg**. Use 13.5 kg as the product mass and treat 14 kg as a rounded structural minimum. Packaged mass on the product page is 16 kg (35.2 lb).

External 418 × 484 × 320 mm. Internal 310 × 380 × 150 mm. It is narrower and deeper than Arc Lite, and 23 mm taller. The extra depth is more stone in front of the flame. Inferred side wall 54 mm. Still a one-layer wall. Comparison tool: **1-layer insulation**, 12 mm cordierite, 15–20 minutes to heat.

### Body, materials, manufacture

The spec sheet is unusually explicit. Paraphrased by component:

- Top pressing: SPCC steel with a ceramic paint.
- Lower pressing: SPCC with a high-temperature powder coat.
- Mid-wrap: brushed 304 stainless.
- Trim: aluminium extrusion, high-temperature powder coat.
- Dock: SPCC, high-temperature powder coat.
- Landing: high-pressure die-cast aluminium, ceramic paint, with a 304 scratch guard.
- Mouth arch: 304, ceramic paint.
- Inner core: 304.
- Handles and clips: GF20 PPS (polyphenylene sulfide, 20% glass).
- Hose bracket: GF30 PA (glass-filled nylon).
- Dial: GF30 PP (glass-filled polypropylene).

SPCC is commercial cold-rolled steel. The big shells are pressed mild steel, not stainless. Stainless is spent where the flame and the hand meet the mouth, on the inner core, and on a visible band. The landing is a die casting because that threshold is a shaped, wear-prone part and aluminium saves mass. PPS on the handles is a high-temperature polymer, still only sane because the handles are outside the vault. Polypropylene on the dial only survives if the dock stays far cooler than the chamber. None of this is a makerspace process list you need to copy. It is evidence of a tooled consumer product: draw dies, a die-cast tool, an extrusion, and injection moulds. Container quantity on the spec sheet is 576. This oven is priced as moulded production, not as a fabricated one-off.

Insulation, spec sheet: non-carcinogenic, water-soluble, made from calcium and magnesium silicate fibres. That is biosoluble alkaline-earth-silicate fibre (the Superwool class), not older aluminosilicate refractory ceramic fibre. Gozney does not print the thickness. The 54 mm side wall is the constraint, same as Arc Lite.

### Floor, heat, airflow

12 mm cordierite. Same mass story as Arc Lite: about **3.0 kg** and **1.4 MJ** if the stone fills 310 × 380 mm. Stone-only time at 3.7 kW and 40% capture is about 15 minutes. The published 15–20 minutes matches, because the insulation is thin and does not add much soak.

Marketing line: heat in about 15 minutes and cool in about 20 minutes so you are not waiting to pack up. Thin insulation is the point. A Dome-class wall would still be hot at the end of the drive home.

There is a front flue. The manual says not to lift by it. Arc Lite’s manual has no flue. Tread keeps a short front throat so soot and exhaust have a path that is not only the mouth, which matters when the oven is used in the open, in wind, on a beach. It is still a low vault with mouth/apex 0.57 and a full-width mouth. Wood still does not fit.

Thermometer conflict, left unresolved: the spec sheet says the thermometer measures air temperature. The comparison tool says the Tread reading is the stone, analog. One of those pages is loose. Either way it is a single analog gauge, not the XL’s floor-and-air digital pair.

### Burner

Spec sheet: **3.7 kW | 273.8 g/h**, pressures 30/37/50 mbar, LPG, bottle 9 kg and up. US plate: injector **0.98 mm**, **12,500 BTU/h** (3.66 kW), propane, 11 in. w.c., ANSI Z21.58, CSA 1.6, control number 5030824. Comparison tool: 3.7 kW (12,621 BTU) and 273 g/h. The mass flow and the kilowatts agree with each other if you use a calorific value between net and gross (274 g/h is 3.53 kW net at 46.4 MJ/kg and 3.83 kW gross at 50.35 MJ/kg). Certified nominal output to design against: **about 3.7 kW**.

Same flame-failure hold, up to 30 seconds. Ignition is electric, with a battery, and the troubleshooting table tells you to replace that battery if the dial does not click. The hose is a quick-connect, because the oven is meant to leave the bottle behind in the car. Leak-test every reconnection with soapy water, never a flame. The manual is firm on that.

Approvals printed on the spec sheet: CE, UKCA, UKNI, ETL, CSA, GM. The October 2025 help article lists Tread as domestic-outdoors for Australia and New Zealand.

### Safety and service

Same 0.3 m back and sides, 1 m front, from the placement section. The US manual’s opening warning is stricter and different: never operate within **1.5 m** of any structure, combustible material, or other gas cylinder, and within 7.5 m of any flammable liquid. Those two instructions are both in Gozney’s documents. For a homemade oven, plan around the larger number until a measured skin temperature and the local rules say otherwise. Gozney also says accessible parts may be very hot, and to let the oven reach 45°C before moving, while another line says at least 20 minutes. The 45°C line is the one that matches a touch decision.

Service: four Torx screws, base panel off, wiring looms stay attached, vacuum the venturi. That is more user-serviceable than a sealed gas valve, and the manual still says parts sealed by the manufacturer are not for the user. The gas valve, injector, and hose spec are in that sealed set.

Venture stand: 4 kg, folds, quick release. Optional. Working height they recommend is about 1.2 m to the floor, elbow height.

### Why it exists beside Arc Lite

Arc Lite wins on price, mass, and “leave it on the table.” Tread spends another 1.5 kg and about AUD $250 on handles, a tougher shell stack, a front flue, a gauge, a quick-connect, a battery igniter, and polymer parts that survive being knocked about. The thermal design is deliberately similar and deliberately thin. Copying Tread’s moulded dock and PPS clips is a factory project. Copying the thermal lesson is easy: if the oven must cool in 20 minutes, one thin insulation layer is a choice, and pizza recovery will suffer.

---

## 5. Dome XL Gen 2

### What it is for

The large hybrid. Australian price **AUD $3,999**. UK £2,499.99. Marketing capacity: one 18 inch, or two 12 inch, or three 10 inch pizzas. The EU spec sheet’s shorter line says one 18 inch or two 12 inch. Propane, wood, or charcoal. Natural gas is offered in some regions as a version, not as a user conversion. The manual forbids converting the fuel and forbids changing gas connections.

Oven mass **73 kg** (161 lb) on the product page, the AU manual, and the spec sheet. Packaged **80.8 kg**. The UK comparison tool’s “weight” cell says 80.8 kg, which is the packaged figure. The AU comparison tool says 160.9 lb, which is the 73 kg oven. Use 73 kg for the appliance and 80.8 kg for the freight.

### Body and manufacture

EU spec sheet, paraphrased:

- Top pressing: aluminised steel, ceramic paint.
- Lower pressing: aluminised steel, high-temperature powder coat.
- Mid-wrap: brushed 304.
- Trim: aluminium extrusion, high-temperature powder coat.
- Dock: GF20 PP (glass-filled polypropylene, not the PPS used on Tread’s handles).
- Landing: high-pressure die-cast aluminium, ceramic paint, 304 scratch guard.
- Mouth arch: 304, ceramic paint.
- Inner core: 304.
- Dial: anodised 6063 aluminium.

Aluminised steel is carbon steel with an aluminium-silicon coating, used here as an **outer** pressing under ceramic paint. It is a corrosion and scale choice for a shell that should stay near the outside of the insulation. It is not a hot-face material. The inner core is 304, which is the correct food-side and flame-side alloy: stable well above 500°C, no zinc, no coating that becomes a fume in the vault. Welding aluminised sheet is a fume job (aluminium and iron). A DIY outer skin is simpler as plain mild steel, painted, with the 304 reserved for the core, the mouth, and the flue.

The shells are pressings. The landing is a die casting. The dock is an injection moulding sitting on the cool front, carrying the digital module. Container quantity on the spec sheet is 110. Still a production tool, but a much heavier one: 73 kg is steel, a thick stone, and a lot of fibre, not a clever alloy.

Inferred side wall **111 mm**, about twice Arc Lite. The comparison tool calls the insulation **3-layer**. The spec sheet names one fibre family only: the same calcium-magnesium silicate, non-carcinogenic, water-soluble wording as Tread. “Three layers” is Gozney’s count of layers, not three published materials and not a published thickness. A 111 mm side wall can hold on the order of 70–90 mm of blanket plus two skins and a fit gap. That is an inference from the envelope. It matches the behaviour below. It is not a measured stack-up.

### Floor

30 mm removable cordierite, pulled forward with a supplied hook if it shifts in transport. Retention wedges in the new oven are packaging and come out before the first fire. If the stone filled the whole internal floor, 724 × 543 × 30 mm would be about **25 kg** and **11.3 MJ** to climb 480 K. At 10.6 kW and 40% capture the stone alone is about **44 minutes**. The comparison tool says 40–45 minutes. The EU spec sheet is more graded and slower at the top end: **15 minutes to 300°C, 30 minutes to 400°C, 60 minutes to 500°C**. Both can be true if they are not measuring the same sensor. The XL has a floor probe and an air reading, and the manual says the floor probe lags during heat-up because the stone has to soak. A 30 mm stone is a storage battery. That is why this oven holds temperature for successive pizzas and for a roast after the flame is embers, and why it is not a 15-minute oven.

Do not bolt that stone down either. Differential growth against a stainless surround on a 700 mm length is several millimetres.

### Dome, flue, door, wood

Internal apex 238 mm, mouth height 140 mm, ratio **0.59**. Closer to the classic 0.63 than the compact ovens, in a much larger room. Mouth width 470 mm against an 18 inch (457 mm) pizza is deliberately tight. The peel has to be slim. Once the pizza is inside, the chamber is 724 mm wide, so the pizza can sit clear of the fire on the right.

Flue is a real assembly: pipe, collar, top, cap. The rain guard is designed with a **3 mm** gap off the top of the oven. The flue inlet sits at the front throat. Exhaust is taken after the gas has crossed the vault, which is the right order: roll first, then capture.

Door: sold as an option, and the manual is absolute. Do not use a door while the gas burner is on. On wood, let the fire die to embers with no naked flame, then the door may go on to hold heat. Never run gas and wood together. Never light the wood with the gas burner. Those rules protect the burner, the flue draught, and the carbon-monoxide case of a choked mouth.

Solid fuel sits on the right, on a **duct grate** that has to be fitted for any wood or charcoal fire. Primary air comes up through the grate. The manual’s wood size is small: about 140 mm long and 20–50 mm in section, moisture 10–20%, 16% called optimum. Kiln-dried hardwood (ash, alder, oak, beech, hickory, fruitwood). No pine, fir, cedar, redwood, spruce, fatwood, painted wood, or sappy wood, because of creosote in a metal core that has no masonry to forgive it. Charcoal: lumpwood 50–100 mm, hardwood or binchotan. No briquettes, no self-lighting charcoal, no damp charcoal. First fire kept moderate for 30–60 minutes so the stone does not shock. Do not throw fuel at the walls.

The Wood-Fire Control Kit is a separate accessory (about USD $200 on the US store). It is a fan module on a USB-C rechargeable battery, plus a stainless wood rack that holds the wood off the stone so air can get around it. Boost mode is more air, on demand. The manual says not to run the module without the rack. This is Gozney’s answer to “wood is hard to control”: under-fire air, metered, instead of a taller chimney only. It is also the part of the design that sits nearest their patent family, discussed below.

Digital dock: air temperature, floor temperature, timer, two meat probes. Floor probe is under the stone. Probe leads must stay out of the flame. Battery is the same quick-swap pack used by the fan kit.

### Burner

UK/EU plate: Dome **9.3 kW (688 g/h)**, Dome XL **10.6 kW (784 g/h)**, for the I3P propane categories at 50, 37, and 30 mbar. Comparison tool: XL **10.6 kW (36,100 BTU)** and **0.75 kg/h**. Those two flows are not the same. 784 g/h is 10.1 kW at 46.4 MJ/kg net and 11.0 kW at 50.35 MJ/kg gross, so 10.6 kW sits between net and gross. 0.75 kg/h is 9.7 kW net and 10.5 kW gross. The spec sheet writes “10.6 kWh | 0.75 kg/h”, which mixes a power with an energy unit. Treat **10.6 kW** as the UK nominal and treat the gram-per-hour figures as messy.

Australia and New Zealand manual, same model numbers: gas pressure **2.75 kPa**, gas rate Dome **31.3 MJ/h** (8.7 kW) and Dome XL **36.1 MJ/h** (**10.0 kW**), ULPG, jet **1.58 mm** on the Dome and **1.74 mm** on the XL. Australian ULPG at 2.75 kPa is a different injector and a slightly lower nameplate than the UK 10.6 kW. A single jet size does not cross the world. That fact alone is why a homemade injector is a bad idea.

Same push-turn ignition and flame-failure hold: the AU manual says hold at the 7 o’clock position for up to 30 seconds until the flame-failure device has disengaged. Flame should be yellow and roll the roof. Minimum bottle 9 kg, and over 13 kg for best performance, because this burner will freeze a small cylinder.

Spec-sheet approval line: CE, ETL, AGA, SANZ. The October 2025 help article: Dome Gen 2 / XL is domestic-outdoors in Australia and New Zealand (and, in the EU column, commercial indoor and outdoor as well). The AU manual points outdoor installation at **AS/NZS 5601**. AGA on the spec sheet is the Australian gas-appliance certification mark family. Confirm the mark on the data plate of the unit in front of you.

### Safety and service

Opening warning in the AU manual: never within **1.5 m** of any structure, combustible material, or gas cylinder; never within 7.5 m of flammable liquid; outdoors only; not commercial use. Placement section of the same manual: **30 cm** back and sides and **1 m** front from combustible construction. Both are published. They are not the same rule. The shell is insulated well enough that Gozney allows a 300 mm side clearance in one paragraph and forbids 1.5 m in another. No skin temperature is published. “Accessible parts may be very hot.” Cool to 45°C, and allow at least 3 hours, before moving a 73 kg oven that is still heat-soaked in 30 mm of stone.

Water on the stone is called out specifically: it can crack the stone and soak the insulation, which then heats slowly. Fibre that has been wetted is a worse insulator until it is fully dried. That is a real maintenance limit of blanket insulation, and it is one of the reasons a wood outer shell that can trap a wet blanket is a bad partner for it.

Stone, grate, flue, and probes are user-serviceable. The gas connections are not a user conversion.

### Why it is built this way

The XL is a restaurant-shaped chamber brought indoors to a backyard: enough floor for a fire beside the food, enough stone to ride through a batch, enough insulation that the outside can be a painted pressing rather than a masonry dome, a flue that finishes the roll, and a door that is only legal once the flame is gone. The gas burner is there so a weeknight pizza does not start with kindling. The wood path is there so the same box can do the long cook. They are mutually exclusive in the manual because the air, the flue, and the burner were not designed to be on together. The digital floor probe exists because a 30 mm stone lies to your hand for a long time.

The 10 kW burner is sized to that mass. It is not a bigger Arc Lite burner for its own sake. Three and a half kilowatts into an 11 MJ stone would be an hour-plus heat-up even before losses.

---

## 6. Side by side

| | Arc Lite | Tread | Dome XL Gen 2 |
|---|---|---|---|
| Model | GOZ-3102 | GOZ-1893 | GOZ-2509 |
| AUD, 18 Oct 2026 | $649 | $899 | $3,999 |
| Job | Tabletop 12 inch gas | Carry-out 12 inch gas | Backyard batch, three fuels |
| Oven mass | 12.0 kg | 13.5 kg (manual also says 14 kg) | 73 kg |
| Pizza | 1 × 12 inch | 1 × 12 inch | 1 × 18 / 2 × 12 / 3 × 10 inch |
| Fuel | Propane | Propane | Propane, wood, charcoal. NG version in some regions |
| Burner | Lateral, 3.4 kW | Lateral, 3.7 kW | Lateral, 10.6 kW UK / 36.1 MJ/h (10.0 kW) AU |
| Flame failure | Yes, ~30 s hold | Yes, ~30 s hold | Yes, ~30 s hold |
| Stone | 12 mm cordierite, loose | 12 mm cordierite, loose | 30 mm cordierite, loose |
| Insulation as sold | 1 layer, fibre type not fully specified | 1 layer, Ca-Mg silicate fibre | “3 layer”, same fibre sentence, thickness unpublished |
| Inferred side wall | 52.5 mm | 54 mm | 111 mm |
| Mouth / apex | 0.57 | 0.57 | 0.59 |
| Room for a wood fire | No | No | Yes, on the right, over a grate |
| Flue | None in the manual | Front flue | Flue pipe, collar, cap, 3 mm rain-guard gap |
| Door | No | No | Yes. Gas off. Naked wood flame out |
| Gauge | None | Analog. Air vs stone is contradicted across Gozney pages | Digital air and floor, two probes |
| Outer shell | Paint and powder on steel and die-cast aluminium | Pressed SPCC, ceramic paint on top, powder coat below, 304 band | Pressed aluminised steel, ceramic paint / powder coat, 304 band |
| Inner | Stainless, help-centre wording | 304 core and mouth | 304 core and mouth |
| Heat-up as published | 20–30 min (manual: 20 min high) | 15–20 min | 40–45 min, or 15 / 30 / 60 min to 300 / 400 / 500°C |
| Max published | 500°C | 500°C | 500°C |
| Move when | ≥ 30 min | To 45°C, or ≥ 20 min | ≥ 3 h, to 45°C |
| Stand | Optional, not the intended life | Venture stand, 4 kg | Stand expected, floor near 1 m, structure must hold 73 kg |
| AU status | Missing from the Oct 2025 certification table | Domestic outdoors | Domestic outdoors. Spec sheet lists AGA. Manual cites AS/NZS 5601 |

Stone-only energy, using published internal floor as if it were all stone, density 2100 kg/m³, specific heat 950 J/kg·K, rise 480 K:

| | Stone mass | Stored | Minutes at nameplate × 0.40 |
|---|---:|---:|---:|
| Arc Lite, 3.4 kW | 2.9 kg | 1.3 MJ | ~16 |
| Tread, 3.7 kW | 3.0 kg | 1.4 MJ | ~15 |
| Dome XL, 10.6 kW | ~25 kg | 11.3 MJ | ~44 |

Published heat-up times sit on top of these stone-only estimates. That is the check that the public dimensions, the public kilowatts, and the public minutes belong to the same machines.

---

## 7. Why Gozney chose it

**Low vault, ratio just under 0.63.** A tall dome wastes a portable envelope and puts the radiating ceiling further from the pizza. Their compact ovens are 150 mm inside and under 320 mm outside. The XL grows the apex to 238 mm because the floor got wider, not because they changed theory. The roll still has to stay in the room and exit high at the front.

**Lateral flame rather than a rear poke.** A rear burner hides behind the pizza and blows out the mouth into the cook. A left-side ribbon leaves the floor clear in a small oven and lets you watch the cornicione. In the XL the same idea becomes a wood fire parked to the right of a narrower mouth. The cook still looks in from the front.

**Cordierite, loose, thicker as the oven gets more serious.** 12 mm is a heat-up and mass decision. 30 mm is a recovery and holding decision. Nobody at Gozney used a steel plate. At 500°C a steel floor’s effusivity burns the base before the top is done.

**Insulation thickness is the product split, not a hidden material secret.** Tread and Arc Lite are one layer because they must be light and, in Tread’s case, cool enough to pack. The XL is three layers and roughly twice the side-wall stack because a 25 kg stone and a 10 kW fire would otherwise make the pressing into a hazard and a fuel bill. The fibre chemistry they are willing to name is biosoluble calcium-magnesium silicate. They do not use a masonry dome, because a masonry dome cannot be a 12 kg product and cannot be pressed in lots of 576.

**Outer metal is ordinary steel with a coating. Inner metal is 304.** Stainless on the whole shell would dominate the bill of materials and the mass. Aluminised or painted SPCC survives outdoors once it is on the cold side of the blanket. The mouth, the core, and the scratch guard are 304 because they see flame, food, and a peel.

**Die-cast aluminium landings and polymer docks.** Those parts are outside the vault, shaped, and made in the thousands. They are not a better hot-face than steel. They are a cheaper, lighter production method. A one-off oven should fabricate the landing from 304 and skip the casting.

**Gas hardware is certified, regional, and sealed.** Jets change from 0.85 mm to 1.74 mm across this range and across countries. Flame failure is on every current manual. Hoses are either captive (Arc Lite) or a specified quick-connect. The manuals say not to modify sealed parts and not to convert the gas. That is the correct scope line for an open-source build too.

**Wood is a separate air system, not a second burner running at once.** Grate, small hardwood, moisture window, door only on embers, optional fan. They spent design effort keeping wood from wrecking the gas train.

**Clearances instead of a promise that the shell is cold.** No page gives a skin temperature. Every manual says accessible parts may be very hot, and every manual keeps the oven off combustible structure. Insulation here is about fuel and about not setting the table alight at 300 mm. It is not a claim that you can rest a hand on the vault at 500°C.

---

## 8. Builder lens

You have a metal shop, a wood shop, CAD, a makerspace, and a university workshop. You are in Adelaide. New is acceptable, second-hand is better, and a gas valve is not a place to save money.

| Choice in these ovens | Can you reproduce it here? | Sensible DIY path | Money | Risk |
|---|---|---|---|---|
| Low vault, mouth near 0.6 of apex, front flue | Yes. Sheet metal, CAD, a brake or a weld | Your own panels. Do not trace their outline | Mostly time | Low if the mouth is tall enough to light and short enough to hold the roll |
| 304 inner core | Yes. Laser or plasma, fold, weld | 1.0–1.5 mm 304. Offcuts from an Adelaide fab shop | New sheet often a few hundred dollars. Offcuts much less | Galvanised sheet in the hot path is a fume and food hazard. Do not take it off Gumtree for the core |
| Painted mild-steel shroud | Yes | 1.0–1.2 mm mild steel, high-temp paint on the cold side | Tens of dollars in scrap, up to about $120 new | Paint on the inner core will burn off and smoke |
| Pressed SPCC shell, die-cast landing, extruded trim, PPS clips | No, not as tooling | Fabricate. A cast landing is a factory part | Tooling is thousands | Copying the look also collides with design rights |
| 12 mm stone | Yes, and it is the wrong first stone for a backyard oven | Buy a 20 mm cordierite kiln shelf | See BOM | Granite, marble, slate, pavers, and glass can spall when trapped moisture flashes |
| 30 mm cordierite | Yes, as one thick shelf or two | Interdec in Adelaide cuts kiln shelves. Walker sells 20–30 mm shelves | $90–$180 new for a 400 mm class shelf. Used shelves show up on Gumtree | A cracked stone is a consumable. Keep it floating |
| AES blanket | Yes, with the right product name | 75 mm total, in 25 mm layers, kept dry | A 25 × 610 × 7200 mm ceramic-fibre roll was $58.50 (was $79.40) at Ceramicraft | Many “ceramic fibre” rolls are refractory ceramic fibre, which is treated as carcinogenic. Prefer a blanket sold as biosoluble AES. Respirator either way. Keep fibre out of the food path |
| “3-layer” as a mystery stack | You do not need their stack | Thickness plus a foil standoff does the job. See section 9 | Blanket is the cheap part | A gap with no foil radiates. The repo calculator treats a gap as still air at k = 0.035 and will overstate the benefit |
| Lateral gas burner, jet, valve, FFD, regulator, hose | Buy the certified appliance. Do not build this | Wood-fired first oven. Gas only as a complete certified oven | Arc Lite at $649 is the real gas option | An uncertified LPG train is how hoses come off and how carbon monoxide gets made. Overseas CE or CSA marks are not Australian acceptance |
| Wood grate and side fire | Yes | A 304 grate on the right, small hardwood, 10–20% moisture | Scrap steel and firewood | Creosote in a steel vault if you burn pine. Embers in a fibre gap if the grate is absent |
| Fan-assisted under-fire air | Mechanically yes, legally careful | Leave it out of the first published design. See patents | A small fan is cheap | Publishing a floor-inlet plus perforated fuel support plus a door used as the damper tracks a live Gozney patent family |
| Digital probes | Yes, later | A type-K on the stone and one in the air | $25–$60 | Leads in the flame die |
| 73 kg hybrid as a first build | Poor use of the budget | Build the 400 mm wood oven below. Buy an XL only if you want that exact appliance | $3,999 vs a few hundred in materials | A first weldment that weighs 73 kg and has a 10 kW gas train is a certification project |

### What has to be bought certified

In Australia a Type A gas appliance needs acceptance before it is sold. Certification bodies named by the Gas Technical Regulators Committee include AGA, SAI Global, IAPMO, Global-Mark, and BSI. The relevant appliance standard for a domestic outdoor cooker is **AS/NZS 5263.1.7**. Installations follow **AS/NZS 5601**, which is the standard the AU Dome manual already points at. Energy Safe Victoria states that a CE mark or a CSA mark is not Australian certification. NSW Fair Trading states that supplying an unapproved gas appliance is an offence. Queensland has warned specifically about unapproved portable LPG cookers whose hoses separated. Second-hand appliances still need to have been certified, and modification can void that acceptance.

So, for this project, in plain language:

- Do not machine an injector, including the 0.85–1.74 mm figures printed on Gozney plates. Those numbers are there to show that the jet is part of a certified, region-specific burner.
- Do not assemble a regulator, hose, valve, and thermocouple from marketplace parts and call it a pizza-oven burner.
- Do not “improve” a certified oven’s gas train. Gozney says sealed parts stay sealed, and the regulators say alteration can cancel acceptance.
- A recycled gas cylinder is a pressure vessel. Cutting one that has not been properly purged is an explosion. It is also a poor oven: thin, painted, uninsulated, and the wrong shape for a side fire. Skip it.
- Wood and charcoal, with no gas fittings at all, are the fuels that keep this build out of the gas-appliance system. Smoke, clearances, and where you light it are still your problem, and a balcony or a timber deck is the wrong site.

Adelaide sourcing that is actually local or national and was on the public web:

- **Interdec Australia**, phone 08 8371 4100, kiln shelves cut to size, cordierite rated 1300°C, price on application. This is the shelf supplier to talk to before drawing the floor.
- **Ceramicraft**, cordierite squares including 400 mm at $88.10 and 450 mm at $110.95, and a 25 mm × 610 mm × 7200 mm fibre roll at $58.50. Thickness of those shelves is not stated on the listing. Freight to Adelaide is extra. One buyer review on that fibre page mentions delivery to Adelaide.
- **Walker Ceramics**, 20–30 mm cordierite shelves from $146.08, size not fixed by that “from” price.
- Gumtree and Facebook Marketplace in Adelaide are where 304 offcuts, old kiln shelves, angle iron, and seasoned hardwood actually get cheap. The repo’s sourcing tool can generate queries, and its offline mode invents listings. Do not treat a simulated listing as a seller. Anything galvanised, zinc-plated, or described as a granite pizza stone is a reject.

---

## 9. Materials Gozney did not use, and the hardwood body

Gozney’s outer skin is pressed steel because steel is stable, non-combustible, dimensionally dull, and cheap once the die exists. A one-off builder can choose differently. Most of the romantic options fail for a specific reason.

**Refractory castable (calcium-aluminate cement, proper refractory aggregate).** A real insulating castable can be the dome. It is heavy, it has to be formed and cured, and the first fires must be slow or the water blows it apart. Hardware-store concrete and ordinary Portland cement are the wrong binder. They spall. Use a refractory castable sold for furnaces, or a home mix only if you already know the recipe and the cement is calcium aluminate. Good for a permanent backyard dome. Slow to heat. Not portable. Food-side surface still wants a cordierite floor rather than the castable itself.

**Perlite or vermiculite concrete.** k around 0.2 W/m·K, several times worse than blanket. At 100 mm with an 18 mm hardwood skin in contact, the model puts the wood’s inner face near **145°C** and the outside near 75°C. At 200 mm the inner face is still about **97°C**. It can be a structural backyard dome if it is thick and the outside is cement sheet or steel. It does not rescue a timber skin. It holds water. First fires steam.

**Ceramic fibre or AES blanket.** This is the material the portable ovens are already using. 128 kg/m³, 25 mm layers. Ceramicraft prints conductivity **0.09 W/m·K at 400°C and 0.16 at 800°C** for their roll. The design calculations below use **k = 0.10** as a working mean for a blanket whose cold face is in the 100–150°C range, and they show what happens if the blanket is really at 0.16. Blanket sags if it is not supported. It loses badly when wet. It is the right primary insulation.

**Microporous board.** k near 0.03 W/m·K. 30–40 mm plus a foil gap can put a cool face on a wood skin in the model (wood inner face about 87°C at 30 mm, about 75°C at 40 mm, still above a prudent long-term limit). The board is expensive, it hates being wet, and it is easy to crush. A possible later upgrade for a compact oven. Not the first purchase.

**Calcium silicate board.** Rigid, k near 0.07, useful as a floor under the stone and as a mouth surround that fibre cannot hold a shape in. It is not lighter than a thin steel shroud, and it is brittle.

**Firebrick.** Fine as a wall in a masonry oven. Heavier and more conductive than blanket, so the outside of a firebrick dome is still hot unless you add insulation outside it. Joints open. A firebrick floor works at 500°C and is cheaper than cordierite, with a higher effusivity, so it is a little less forgiving than a kiln shelf. Keep the joints tight and the bricks dry.

**Cast iron.** Excellent door frame or a bread oven that lives at 250°C. As a pizza floor at 450–500°C the effusivity is about 13,000 J/m²·K·s^½ and the base burns in well under half a minute. Do not use it as the hearth.

**Spun aluminium.** Loses strength well below pizza temperature and melts near 660°C. The mechanical-engineering rules for this repo ban aluminium in the inner chamber and the flame path. Gozney’s die-cast aluminium is the landing, outside the vault, with a stainless wear strip. Spinning a dome is also a specialist lathe, not a free makerspace trick. Aluminium as a cool outer skin is possible only after the steel shroud underneath has been measured.

**Composite or fibreglass shells.** The resin is the fuel. They belong nowhere near a 500°C liner.

**Recycled kegs.** A purged stainless keg can be a round cooking chamber for a first experiment. The steel is thin, the mouth geometry fights you, insulation has to go outside, and any lining or paint has to be gone before food goes in. It does not become a Dome XL. It is a prototype shell at most.

### The turned hardwood body

The proposal: a turned or coopered hardwood shell as the outer cover, insulation inside it, no metal shroud over the clay or the blanket.

**Verdict: do not build it as the structure.** A hardwood sleeve is only defensible as a removable, ventilated, non-structural jacket around a steel shroud whose skin you have already measured. Even then it is a finish, it costs more than paint, and it is the first thing to delete if the measured skin is warmer than the model.

The reason is the inner face of the wood, not the face you can touch.

Wood does not have one ignition temperature. For short exposures, Babrauskas’s review puts ignition near **250°C** at the lowest heat flux that will ignite, and piloted flaming ignition often at **300–365°C** (*Journal of Fire Protection Engineering*, 2002). That is the number people quote, and it is the wrong number for a shell that is warmed every time you cook, for years. The same author’s later paper on long-term heating concludes that a hot surface of **77°C or higher**, left against wood for a protracted time, is a documented self-heating hazard, and that 77°C already has no safety factor (*Fire and Materials*, 2006; the pyrophoric-carbon discussion). The mechanism he describes is slow formation of reactive char where oxygen is poor, then ignition when a crack finally lets air in. A timber shell sealed over insulation is a good imitation of that geometry. Cyclic heating, which a pizza oven does every Saturday, is called out as harsher than a steady temperature. Discolouration and slow pyrolysis also start well below 250°C. A surface that looks merely warm on the outside can be doing this on the inside.

The calculation is steady-state conduction plus radiation across any air gap. Chamber 500°C, still air, inner film coefficient 30 W/m²·K, hardwood 18 mm at k = 0.17 W/m·K across the grain, clay liner 12 mm at k = 1. The script is `calcs/wall_model.py`.

Wood in contact with the blanket, k = 0.10, ambient 20°C:

| Blanket | Heat flux | Wood inner face | Wood outer face |
|---:|---:|---:|---:|
| 40 mm | 760 W/m² | 161°C | 80°C |
| 80 mm | 460 W/m² | 110°C | 61°C |
| 100 mm | 390 W/m² | 96°C | 56°C |
| 150 mm | 270 W/m² | 76°C | 47°C |
| 220 mm | 200 W/m² | 61°C | 40°C |

The outside at 80 mm of blanket is a comfortable 61°C. The wood where it touches the insulation is 110°C. That is the failure. To get the inner face down near 60°C you are at about **220 mm** of blanket. At k = 0.16, which is the hot end of the Ceramicraft table, 150 mm still leaves the inner face at about **100°C**. On a 35°C Adelaide afternoon the same 220 mm stack is warmer again: 300 mm of blanket still left the inner face near 64°C in the sweep. A turned body with a 50 mm wall cavity, which is what Arc Lite’s entire side wall is, would put the timber inner face above 150°C.

A foil-faced gap between blanket and wood helps, and it does not rescue a thin wall. At 75 mm of blanket plus a 15 mm gap faced with a low-emissivity sheet (emissivity 0.15 against the blanket’s 0.80), the wood inner face is still about **99°C**. The foil belongs on the cold side. It is aluminium or stainless shim, not a hot-face reflector sitting in the flame. Aluminium foil at a 150°C cold face is fine. Aluminium foil that has slipped against the liner is not.

Putting the wood outside a steel shroud, sealed, is worse than it looks. The recommended steel stack below has a bare skin near 60°C. Seal an 18 mm hardwood sleeve over a 20 mm unventilated gap on that same stack and the model moves the steel from 60°C to **128°C**, the wood inner face to **96°C**, and the wood outer face to **56°C**. The sleeve feels acceptable. It has turned the shroud into a hot plate and buried a 96°C timber face where you will not look. A sealed decorative jacket undoes the insulation.

What would have to be true before any hardwood is on this oven:

- The structural cover is steel or a cement-board shroud. Wood carries no load and holds no blanket up.
- The sleeve is open at the bottom and the top so air moves. The day you enclose it, you have built the sealed case above.
- It comes off without tools, so you can put a thermocouple on the steel and on the back of a stave.
- Mouth, flue, base, and every penetration are metal or calcium silicate. The broad-wall sum is irrelevant at a flue collar. A steel fastener through the stave is a thermal bridge and a char point.
- The inner face of the timber stays at or below **60°C** in a measured soak, which is under the 77°C long-term figure and level with the metal touch threshold in ISO 13732-1. If you cannot measure it, you cannot claim it.
- No film finish is asked to be a fire barrier. Polyurethane will blister and smoke. Oil will not keep a 120°C face from pyrolysing.

Movement and moisture reject a turned shell even if the temperatures were kind. A body this size is coopered staves or nothing. Hardwood tangential shrinkage from green to dry is often around a tenth of the width. Adelaide outdoor humidity will keep moving a finished stave for the life of the oven. A closed hoop over a soft blanket either opens a gap at the joint or crushes the fibre. Pizza steam and rain wet the blanket. Wet blanket conducts more, and a timber lid over a damp blanket is the start of rot and of the oxygen-starved char path. Gozney’s own XL manual warns that soaking the insulation drops the temperature and slows heat-up. Their outer skin is steel so the blanket can be wrapped, dried, and replaced. A turned hardwood cover fights every one of those repairs.

Finishes do not change the verdict. A char layer is not a designed ablation. Fire-retardant paint is not rated as the sole barrier between a 500°C liner and a timber structure.

**Use the wood shop on the stand, the peel, the door handle, and a removable sleeve you can take off and point a thermometer at. Keep the oven itself in metal and fibre.**

### A steel stack that does meet a 60°C skin

Same model, 1.2 mm 304 inside, blanket at k = 0.10, 1.2 mm painted steel outside, ambient 20°C:

| Stack | Skin |
|---|---:|
| 40 mm blanket, no gap | 91°C |
| 75 mm blanket, no gap | 67°C |
| 90 mm blanket, no gap | 62°C |
| 75 mm blanket + 12 mm foil-faced gap | 60°C |
| Same 75 mm + foil gap, ambient 35°C | 71°C |
| 75 mm at k = 0.16, no gap | 84°C |

Forty millimetres, which is the most a 52 mm Arc Lite side wall can be hiding, does not produce a 60°C shell in this model. That lines up with Gozney refusing to claim a cool shell and publishing clearances instead. Seventy-five millimetres plus a foil standoff is the thinnest stack I would draw for a backyard oven, and the first real fire has to confirm it with a thermocouple. If the blanket you actually bought is closer to 0.16 W/m·K at the mean temperature you reach, add another 25 mm before any timber, including a sleeve, comes near the skin. On a 35°C day the same stack is about 71°C. Gloves, and no timber screen hard against the vault.

The repo’s `thermal_model.py`, using its built-in k = 0.08 for ceramic fibre, gives 82°C outside a 40 mm blanket and 60°C outside 75 mm. That matches this script at k = 0.08. Use 0.10 for design. Use 0.08 only as a best-case cross-check.

Floor insulation wants the same duty as the dome, plus a non-combustible deck and an air gap under that, because the stone is sitting on it. A timber table is the wrong piece of furniture. Arc Lite’s manual already forbids a combustible structure under the oven.

---

## 10. Recommended first oven

Build a stationary backyard wood oven that takes the XL’s lessons and the compact ovens’ size, and that does not take their gas train or their outline.

**Fuel.** Hardwood only, small splits, 10–20% moisture, on a grate at the right side of the chamber. No gas fittings. Add gas later only by buying a certified oven, not by drilling this one.

**Floor.** One 400 × 400 mm cordierite kiln shelf, 20 mm if you can get it, 15 mm if that is what Interdec has. Floating, on a fibre-paper or calcium-silicate slip, with at least 4 mm clearance to the steel all round. One 12–14 inch pizza with room to turn it. An 18 inch floor is a different project and a much heavier stone.

**Vault.** Apex about 220 mm. Mouth height about 140 mm, which is 0.64 of the apex. Mouth width about 360 mm so a peel fits. Chamber wider than the mouth so the fire has a bay on the right and the pizza is not in it. Front-throat flue, 304, taken off after the roll. No door on the first version. A door is a later heat-soak tool and it stays off while any flame is visible.

**Wall.** 1.2 mm 304 inner. 75 mm AES blanket in three 25 mm layers, or the biosoluble product you can actually buy. A 12 mm standoff with stainless or aluminium foil on the cold face only. 1.0–1.2 mm mild-steel shroud, high-temperature paint. Same under the floor. Thermocouple on the shroud at the first serious fire. If the skin is over 70°C, add blanket before you build a timber anything nearby.

**Base.** Steel stand at about 1 m to the floor, on a surface that does not burn. Cement sheet as a heat shield if the patio is timber, with an air gap. Clearance planning number **1.5 m** to combustible structure, taken from the stricter sentence in Gozney’s own XL warning, until you have measurements and have read the South Australian rules. Do not adopt their 300 mm side figure as a DIY target.

**What this refuses.** No turned hardwood structure. No galvanised anything in or near the core. No aluminium liner. No cast-iron floor. No pine. No fibre exposed at the mouth. No copied Gozney silhouette. The lateral-flame idea and the front flue are old dome practice. The specific combination in Gozney’s patent family is not.

**Patents, plainly.** WO 2021165706 / US 2023/0106404, inventor Thomas Gozney, assignee Gozney Group Ltd, priority 19 February 2020, has an Australian family member AU 2021223087. The published description covers a multi-fuel open-flame oven with a floor, a loading door, controlled inlet and outlet air, and a solid-fuel support fed by air through that inlet, plus steam and smoke accessories in the broader disclosure. A classic side-fire wood dome with a chimney is much older than that filing. A published open-source design that implements a floor air inlet, a perforated fuel rack fed by that inlet, and a door used as the damper would need an Australian patent attorney before it is released. This recommendation leaves the fan, the floor plenum, and the door out, on purpose. Design patents also cover the look of their ovens. Make this one look like a shop-built vault.

**OSHWA, when you later want it in the repo.** Editable CAD, STEP, DXF, a real `bom/bom.csv`, CERN-OHL-P for the hardware, CC-BY-4.0 for the text. This paper stays private until you decide the design is yours and not a teardown of theirs. Do not commit teardown notes, this PDF, or the section drawing.

---

## 11. Rough bill of materials, AUD

Ranges mix prices read on 18 October 2026 with estimates marked as such. Freight to Adelaide is not included. Second-hand is a hope, not a quote.

| Part | Spec | New | Second-hand / scrap | Notes |
|---|---|---:|---:|---|
| Cordierite floor | ~400 × 400 × 15–25 mm | $90–$180 | $20–$80 if a kiln shelf appears | Ceramicraft 400 mm square listed at $88.10, thickness unstated. Walker 20–30 mm from $146. Interdec Adelaide on application |
| AES or ceramic-fibre blanket | 25 mm, enough for 75 mm all round | $60–$180 | Rarely worth buying used | One Ceramicraft roll is 4.4 m² at $58.50–$79.40 and is more than a small oven needs. Confirm AES vs RCF |
| Calcium silicate under the stone | ~25 mm | $40–$80 estimate | Fireplace offcuts | Rigid floor, fibre does the dome |
| 304 sheet | 1.0–1.5 mm for core, mouth, flue, grate | $150–$350 estimate | $50–$150 offcuts | Gumtree “304 sheet offcut”. Reject galv |
| Mild steel shroud and stand | 1.0–1.2 mm and angle | $40–$150 estimate | $0–$50 | Makerspace scrap is realistic |
| Foil or stainless shim | Cold side of the gap | $15–$40 | — | Not a hot-face reflector |
| Cement sheet shield | Under the stand if the deck is timber | $20–$40 | — | Air gap above it |
| Type-K thermometer | One stone, one air is better | $25–$60 | — | The instrument that checks this paper |
| A2 fasteners, anti-seize | M5/M6, coarse holes in the hot zone | $25–$40 | — | No zinc plating in the core. No nylon-insert nuts in the hot zone |
| Refractory mortar | Small tub, for the mouth only | $20–$40 | — | Not ordinary cement |
| Hardwood sleeve | Optional, ventilated, removable | $80–$300 | Gumtree slabs | Buy only after the skin is measured |
| Firewood | Seasoned hardwood | $0–$80 a boot-load | Arborist offcuts | 10–20% moisture. Not pine |

**Total without a wood sleeve: about $450–$1,100 if you buy small quantities new, and about $250–$700 if the stone and the 304 are surplus.** Arc Lite at $649 remains the rational purchase if what you want is propane on a balcony this month. This build is the rational one if what you want is a repairable wood oven with a thicker floor, a real flue, and no gas certificate to void. Dome XL at $3,999 is the appliance you buy when you want their hybrid and their warranty, not a target to beat on the first weldment.

Difficulty for a skilled metalworker: the core, mouth, and flue are a serious weekend or two on a brake and a TIG or MIG. The blanket and the stone are an afternoon. The risk is not the fold. The risk is a combustible deck, a wet blanket, pine smoke in a steel vault, and any later decision to add gas.

---

## 12. Open questions

These should be answered before any CAD goes into the repository. This paper does not put them there.

1. Is the first oven wood-only, or do you actually want gas on weeknights? If gas, the rational object is a certified Arc Lite or Arc, not a fabricated burner.
2. Is it stationary in a backyard, or does it have to move? Stationary allows 75 mm of blanket and a 20 mm stone. Portable pushes you back toward Tread’s thin wall and its fast cooldown.
3. Pizza size. 400 mm floor is assumed here because it matches a stock kiln shelf and a 12–14 inch pizza. A 16 inch floor changes the stone, the stand, and the heat-up.
4. Balcony or ground? A balcony brings strata rules, a weight limit, wind, and a hard ban on a combustible soffit overhead. Gozney forbids use under a balcony or deck.
5. Is the hardwood sleeve an aesthetic you care about, or was it a hope of avoiding sheet metal? The metal is the safe structure. The sleeve is optional and last.
6. Natural gas on the property, or only 9 kg ULPG? Irrelevant for the wood oven. Decisive if you later buy a certified gas oven, because the jets differ.
7. Budget ceiling. Under about $700 all-in, stay with one kiln shelf, scrap steel, and three layers of blanket. Do not start the XL-sized floor.
8. Are you willing to have a patent attorney look at AU 2021223087 before any fan-assisted floor grate is published?

---

## 13. Sources

Gozney, read 18 October 2026:

- Arc Lite product page, https://www.gozney.com/products/arc-lite
- Tread product page, https://www.gozney.com/products/tread
- Dome XL Gen 2 product page, https://www.gozney.com/products/dome-xl-gen-2
- Comparison tool, https://www.gozney.com/pages/oven-comparison-tool and https://au.gozney.com/pages/oven-comparison-tool
- Australian range and prices, https://au.gozney.com/collections/pizza-ovens
- Arc Lite UK/EU manual, https://www.gozney.com/cdn/shop/files/Arc_Lite_Manual_-_UK_EU.pdf
- Arc Lite US/CA manual, https://us.gozney.com/cdn/shop/files/Arc_Lite_Manual_-_US_CA.pdf
- Tread spec sheet, https://www.gozney.com/cdn/shop/files/Tread_Spec_Sheet.pdf
- Tread US/CA manual, https://us.gozney.com/cdn/shop/files/Tread_Technical_Manual_-_US_CA.pdf
- Dome Gen 2 AU/NZ manual, https://au.gozney.com/cdn/shop/files/Dome_Gen_2_Series_Manual_-_Australia_and_New_Zealand.pdf
- Dome XL EU spec sheet mirror, https://www.450c.com/wp-content/uploads/2025/11/DOC-095901Dome-XL-Specification-Sheet-EUDoc.pdf
- Help centre: Arc Lite specifications; Arc Lite materials; Arc Lite versus Arc; Tread fuel; product certification table (23 October 2025); Arc Lite versus Tread
- Wood-Fire Control Kit, https://us.gozney.com/products/wood-fire-control-kit

Patents, abstracts and bibliographic data only:

- WO 2021165706, US 2023/0106404, EP 4298967, family includes AU 2021223087. Inventor Thomas Robert Llewelyn Gozney, assignee Gozney Group Ltd. Priority 19 February 2020.

Gas acceptance:

- Gas Technical Regulators Committee, certification and second-hand rules, https://gtrc.gov.au/
- Energy Safe Victoria, Australian compliance plate, CE and CSA not sufficient, https://www.energysafe.vic.gov.au/industry-guidance/gas-and-pipelines/gas-appliances-equipment-and-manufacturers/gas-appliances-online-sales
- NSW Fair Trading, gas appliance supply offences, https://www.nsw.gov.au/legal-and-justice/consumer-rights-and-protection/safety/gas-safety-requirements-and-consumer-rights
- Resources Safety and Health Queensland, unapproved portable LPG cookers, https://www.rshq.qld.gov.au/safety-notices/petroleum-and-gas/unsafe-unapproved-lpg-cookers
- AS/NZS 5263.1.7 domestic outdoor gas cooking appliances, listed via the Australian Business Licence and Information Service
- AS/NZS 5601, as cited in the Gozney AU Dome manual

Wood ignition:

- Babrauskas, V. Ignition of Wood: A Review of the State of the Art. *Journal of Fire Protection Engineering* 12 (2002).
- Babrauskas, V. Ignition Handbook. Fire Science Publishers, 2003.
- Babrauskas, V. ‘Pyrophoric Carbon’ and Long-term, Low-temperature Ignition of Wood, and the related *Fire and Materials* paper on prudent clearances (2006). The 77°C long-term figure is his conclusion from the case record, and he is explicit that it includes no safety factor.

Materials, prices as listed that day:

- https://www.ceramicraft.com.au/kiln-shelves
- https://www.ceramicraft.com.au/ceramic-fibre-insulation-blanket-australia
- https://shop.walkerceramics.com.au/ (20–30 mm shelves)
- https://interdec-australia.com.au/shop/kiln-shelves/kiln-shelves/

Standards used as design rules, not as a claim that these ovens were tested to them in this study: ISO 13732-1 for the 60°C bare-metal contact threshold, and the food-contact position already in this repo (304 in the hot chamber, no galvanised steel, no PTFE, no aluminium in the flame).

---

## 14. Calculations and what is still unknown

Script: `calcs/wall_model.py`. Output: `calcs/wall_model_output.txt`. Cross-check: `.agents/skills/oven-thermodynamics/scripts/thermal_model.py` at k = 0.08.

Assumptions that move the answer:

- Blanket k = 0.10 W/m·K as a design mean. The product you buy may be 0.09 at 400°C or 0.16 at 800°C. The table in section 9 shows that swing.
- Still air, emissivity 0.88 on painted steel, inner film 30 W/m²·K. Wind cools the skin and does not cool the wood face that is sealed inside.
- One-dimensional. Corners, the mouth, the flue, and fasteners are hotter than the broad wall. Those details are the ones that start fires.
- Stone density 2100 kg/m³ and specific heat 950 J/kg·K. A real shelf can be 1800–2300 kg/m³. Mass scales with it. The 25 kg XL figure assumes the stone fills the entire published internal floor, which may be generous.
- Draft capture of 40% is a sketch, used only to see whether published kilowatts and published minutes can belong together. They can.

Still unpublished, and worth a measuring tape if you ever have the ovens in front of you: insulation thickness and number of distinct layers, sheet gauges, whether Arc Lite’s inner core is 304 or a cheaper stainless, skin temperature at a 500°C stone, and the Australian data plate for Arc Lite. None of those gaps change the recommendation. The compact ovens are thin and gas-only because their mouths are as wide as their chambers. The XL is heavy because the stone and the firebox are doing a different job. A hardwood shell does not replace the steel shroud unless the blanket is hundreds of millimetres thick, which is no longer the oven you were trying to build.
