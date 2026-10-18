Critique the two locked early prototypes below. One round for Morning, then one round for Moondancer. Do not invent a third oven. If a temperature or a mass below is wrong, show the corrected arithmetic. If it is right, say what you tried to break and why it held.

Names follow chronology, not mass. Angas is the pre-dragon baseline. Morning and Moondancer are both early-stage, so both names are young dragons. Do not rename them to a great dragon.

## Shared geometry, kept from the Angas 430

Chamber Ø470. Mouth 420 × 95. Apex 165 (skirt 120, dome rise 45). Mouth/apex 0.576. Stone does not pass the mouth. Crown lifts at a cinch above the arch. Burner is a bought allowance of 1.85 kg, not a jet. Gas only. Microporous board, k = 0.030 W/m·K, density 250 kg/m³, same thickness on wall and crown. 1D model: 500°C gas, 20°C air, h_in = 25, h_ext = 10. Underside uses a 430°C deck through the pan, the floor board, and the base. Grip: four Ø6 stainless posts, 3 mm PTFE washers, two Ø22 × 130 jarrah bars, cooled at h = 10.

scipy.optimize SLSQP minimised ready mass. Bounds are the DFM floor: 0.6 mm liner, 15 mm stone minimum (12 mm dumps the deck), stone diameter 420 to 430, wood stave at least 8 mm, aluminium skin at least 0.8 mm, aluminium base at least 0.9 mm. Constraints: ready mass ≤ 20 kg, metal skin ≤ 55°C, wood inner face ≤ 75°C, wood outer ≤ 50°C, underside ≤ 60°C, grip ≤ 40°C.

## Morning, wood body, blackwood skin, stainless base, brass cinch

Optimised: liner 0.6, blackwood 8.0, base 0.8, pan 0.6, wall/crown board 42.3, floor board 27.7, stone Ø420 × 15, brass band 14 × 1.2, handle standoff 16. Ready mass 19.10 kg. Wood outer 50.0°C, wood inner face 65.0°C, underside 60.0°C, grip 25.3°C. Plan Ø572. Body height 260. Pizza radial clearance 19.5 mm. Part masses, kg: base pan 1.623, lip 0.136, floor board 1.210, stone pan 0.822, stone 4.364, liner skirt 0.652, liner dome 0.897, wall board 1.625, crown board 2.544, wood skirt 0.884, wood dome 1.565, brass band 0.258, mouth frame 0.095, throat 0.248, landing 0.106, grips 0.081, posts 0.014, washers 0.005, ferrules 0.041, jarrah feet 0.018, rack bosses 0.021, stand bosses 0.039, dowels 0.004, burner 1.85.

The wood is segmented rings or staves on the table saw and thicknesser, trued on the WorkBee. No bowl lathe. University workshop TIG's the 0.6 mm liner. Makerspace lathe turns the ferrules, the grips, and the small feet.

## Moondancer, no aesthetic constraint, aluminium skin and base, stainless cinch

The solver tried aluminium and stainless skins and kept aluminium because it was lighter and the skin is at 55°C, far below where the alloy softens. Liner and stone pan stay 304. Optimised: liner 0.6, aluminium skin 0.8, aluminium base 0.9, pan 0.6, board 36.9 wall/crown, floor board 27.7, stone Ø420 × 15, stainless band 12 × 0.8, standoff 16. Ready mass 15.58 kg. Skin 55.0°C, underside 60.0°C, grip 26.2°C. Plan Ø547. Body height about 247.

## What to return

For each variant: three attacks (mass double count, a temperature over the limit, pizza clearance, handle heat, a machine the shop does not have, crown lift, stone too thin). Then either "holds" or the one number you would change, with the new mass. End with the CalculiX targets: outer skin °C and grip °C the mesh should recover within 3°C, and confirm the rack bosses (4 × M5 on a 120 mm pitch circle on the crown) and the stand bosses (4 × M6 on a 220 mm square on the base) are the right interfaces to leave in the solid without adding the rack or the stand.
