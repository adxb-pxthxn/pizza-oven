You are the design engineer for Adib's personal pizza oven. Write as an engineer who will be wrong in public if the arithmetic is wrong. Show every mass and temperature calculation. Label every price ESTIMATE, AUD, Adelaide, October 2026. Do not invent a machine the workshop list does not contain. Do not design a burner jet, orifice, or injector. Do not specify a galvanised or zinc-plated part in the hot gas path.

The coordinator will build the CAD, check your numbers, and reject anything that does not close. Prefer a design you can defend over a design that looks like a product render.

## What this oven is

Personal object first, open-source hardware second. Adib is a skilled metalworker, woodworker, and CAD user (Fusion 360, FreeCAD). He has a university engineering workshop and full access to Makerspace Adelaide, 223 Angas Street. Budget is low because of that access and because of second-hand parts from Gumtree and Facebook Marketplace in Adelaide. The finished oven must look and feel like an heirloom: real materials, visible craft, something he can show his grandchildren and still cook on.

Use: tailgating and car camping from a BYD Shark 6 ute. One or two people lift it. It rides in the tub, survives corrugations and a sudden stop, sets up fast, heats fast, shrugs off weather, and cleans on site.

## Hard requirements

- Fully circular domed body. Round in plan. Not a box, not a rounded rectangle.
- Cooks a 15 inch (381 mm) pizza with turning clearance. Cooking floor 420 mm diameter is the floor of the requirement, not the target. A peel has to rotate the pizza.
- Gas first. The burner, flame-failure valve, thermocouple, regulator, and hose are bought certified. Australian target: LCC27 regulator at 2.75 kPa, hose to AS/NZS 1869. Do not drill jets. Do not delete the flame-failure device. A backyard prototype on a portable bottle does not need AGA appliance approval. Selling it, or connecting it to fixed pipework, does. AS/NZS 5601.1 clearances still apply: treat 0.3 m sides and back and 1 m in front as the outdoor working clearance.
- Wood fire is optional and only if it does not compromise the gas flame roll, the floor, or the clean-up. Gas and wood are never alight together.
- Fast heat-up. A soaked floor in well under an hour is the point of a portable gas oven. State the thermal mass you are willing to heat and why.
- Premium finish. No painted mild-steel box, no visible self-tappers, no raw laser tab edges on a show face.

## The ute (published figures, use these)

BYD Shark 6 tub, both Premium and Performance, as published by canopy fitters and Auto Expert, October 2026:

- Tub length 1520 mm, width 1500 mm at the top, depth 517 mm, volume 1200 L.
- Width between the wheel arches about 1224 mm. That is the floor width that matters.
- Tailgate opening about 1370 mm wide (Chasing Cars). The lowered tailgate is only as deep as the tub is tall: about 517 mm of horizontal surface.
- Six tie-down points. 230 V socket in the tub (useful for a fan or a light, not for the burner).
- An oven wider than about 480 mm cannot sit fully on the lowered tailgate. Say so if your plan view is larger, and give it another way to stand (own legs on the ground, camp table). Stowed height, legs folded or removed, must go under 517 mm with a margin for a tonneau, so target a body under 460 mm tall unless you stow it in a different attitude and justify the stone.

## Makerspace Adelaide, fetched 18 October 2026

Published on makerspaceadelaide.org. Do not add machines.

Named:
- Thunder Nova35, 80 W CO2 laser, bed 900 × 600 mm. Cuts wood, acrylic, leather, card. It is not a stainless cutting tool.
- Trotec Q500, 60/120 W CO2 laser, bed 1300 × 900 mm. Same limitation. It can engrave.
- Bambu Lab P1S with AMS, 256 mm cube, PLA/ABS. Zortrax M300, 300 mm cube, ABS/HIPS. Up Box+, 255 × 205 × 205 mm, PLA/ABS.
- WorkBee CNC router. Bed size is not published. Assume a wood and plastics router, not a metal mill.
- Sewing machines and overlockers. Irrelevant to the oven except for a canvas cover.

Shops that exist, machines not named:
- Woodworking, with an induction. A Creative Spaces listing for this workshop names a table saw, drop saw, thicknesser, scroll saw, and workbenches. The homepage names Carbatec power tools. No wood-lathe swing is published. Do not assume a lathe that can swing a 600 mm drum.
- Metalworking, with an induction. The 2025 induction text names a cold cut saw, a welder (process not named), a lathe (swing not published), a mill, and hand tools. There is a metal lathe course. A community lathe will take rings, bushes, handles, and a badge. It will not chuck a 500 mm hoop. No press brake, fibre laser, waterjet, English wheel, or metal spinning lathe is published.
- Painting and finishing.
- Electronics.

Adib also has a university engineering workshop. Treat that as the place for TIG of stainless, rolling or braking 1.2–1.5 mm 304, and anything the makerspace list cannot do. Do not name a university machine you have not been given. Where a part needs the university shop, say "university workshop, process: …".

Design the wood body so it can be coopered or segmented with a table saw and thicknesser, trued on the WorkBee or by hand, and finished without a bowl lathe. A lathe pass is a bonus, not the method.

## Thermal facts from the previous study (the code is the number)

1D steady wall, 500°C gas, 20°C air, h_in = 25 W/m²K, h_ext = 10 W/m²K.

Case C in research/argon-anatomy/calcs/hardwood_shell.py, which passes:
- 20 mm castable (k = 1.5) + 75 mm AES (k = 0.08) + 50 mm calcium silicate (k = 0.065) + 20 mm hardwood (k = 0.16)
- Wood inner face 74.4°C. Flux about 242 W/m². Wood outer face about 44°C.
- The castable resistance is only 0.013 m²K/W. Dropping it and keeping a 1.5 mm 304 liner moves the wood inner face by about 1°C. The stack that matters is 75 mm AES + 50 mm calcium silicate.

Ventilated cavity in that script holds the wood inner face near 26°C only while the cavity air is 30°C. If the slots choke, the wall returns to the sealed case. Do not rely on a drawing of slots. A sealed air gap between a hot metal skin and wood is a radiation problem, not insulation: two surfaces at ε ≈ 0.9 a hundred degrees apart exchange on the order of 1 kW/m².

Wood inner-face limit: 80°C. Char is not a design state. Touch surfaces you expect a bare hand to rest on should sit near or under 60°C. Handles must stay cooler than the shell. Mouth, flue, and any landing the flame can see are non-combustible.

No household fibreglass. No GRP near the heat. No cement sheet as a hot face. No granite, marble, slate, or concrete paver as a deck. Cordierite floor, not steel and not cast iron (effusivity burns the dough). 20 mm cordierite is the portable soak; 12 mm dumps its heat mid-pizza; 30 mm is slow.

AES density 128 kg/m³. Calcium silicate insulating board: state the density you use (a fair figure is 250 kg/m³) and keep it consistent. Cordierite 2100. 304 stainless 7900. Hardwood: jarrah about 820–860 dry, red gum often over 900, blackwood about 640. Use the species you specify.

Species that make sense in Adelaide: red gum, sugar gum, blackwood, jarrah. Design for movement across a 400 mm+ radius, for rain on a tailgate, for a hot cycle every cook, and for a film finish that will not crack off. End grain, hoop hardware, and the joint between wood and metal are the design, not a texture.

## Gas scale, from the Gozney study, not as something to copy

Arc Lite: 3.4 kW, 252 g/h propane, hearth about 325 × 355 mm, 12 kg, mouth 85 mm on a 150 mm apex (ratio 0.57), one thin AES layer, shell runs hot. Tread is the same idea plus a crash base. Dome XL: 10.6 kW, 73 kg, three AES layers, wood and gas never together.

The mouth is where the kilowatts leave. A bigger floor wants more burner than 3.4 kW if heat-up is to stay in the same class. Name a power band and a bought-in burner type (commercial oven burner bar, certified, with FFD). Do not draw the jet.

## What good work looks like

- One coherent object. Every part has a process and a machine.
- Masses from volumes and densities, not from a vibe.
- A plan-view diameter, a body height, a floor diameter, a mouth width and height, and a mouth-to-apex ratio, all in millimetres, that fit the tub rules above.
- The thing a grandchild notices: the joint, the band, the mouth, the handle. Describe those in hardware, not adjectives.
