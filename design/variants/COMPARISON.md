# Morning and Moondancer

Angas stays the baseline. These two are early prototypes, so the names are young dragons, not the great ones. Morning is the wood body. Moondancer is the light shell. The names follow the order of the work, not the mass.

Both keep the Angas dome: chamber Ø470, mouth 420 × 95, apex 165, crown lifting off a cinch above the arch, burner in the crescent beside the stone. The stone does not pass the mouth. Gas only. The burner, valve, regulator, and hose stay bought.

The mass target is 20 kg with the stone in. scipy.optimize (SLSQP) minimised that mass. Skin temperature is a constraint, not a result that was allowed to float. Gauges sit on a floor a shop can actually make: 0.6 mm liner, 8 mm wood staves, 0.8 mm aluminium skin, 15 mm stone. A 12 mm stone was refused because it dumps its heat on the first pizza.

## Comparison

Mass is the FreeCAD solid plus the 1.85 kg burner allowance. The analytical total the solver printed is in brackets. Costs are ESTIMATE, AUD, Adelaide, October 2026, bottle excluded. Skin temperature is the CalculiX result, which matched the 1D sum.

| | Tread, benchmark | Angas 430, baseline | Morning | Moondancer |
|---|---|---|---|---|
| Ready mass | 13.5 kg | 37.6 kg | **19.2 kg** (19.1) | **15.8 kg** (15.6) |
| Cost, AUD | 899, retail | 530–845 | 620–710 | 470–560 |
| Outer skin | Hot. Not this oven. | 53–55°C | **50°C** wood | **55°C** aluminium |
| Build | Bought | Hard. Rolled 1.2 mm gore dome | Hard. Segmented wood, thin TIG liner | Moderate. Thin sheet, university roll and TIG |

Neither plan sits on the lowered tailgate. Morning is Ø572. Moondancer is Ø547. The tailgate is 517 mm deep, and a flame there has no clearance to the ute. Both bodies are about 250 mm tall, so they ride in the tub. Short feet sit them on a camp table. The stand is a later part.

## Where the kilograms came out

Angas ready was 37.56 kg: steel 18.3, AES 6.33, calcium silicate 2.34, stone 6.10, brass 2.11, jarrah 0.53, burner 1.85. The base pan alone was about 4.2 kg because it was Ø675 × 1.5 mm.

Morning, analytical parts, 19.10 kg:

| Part | kg |
|---|---|
| Stone Ø420 × 15 cordierite | 4.36 |
| Microporous board, wall 42.3, crown 42.3, floor 27.7 | 5.38 |
| 304 liner, pan, mouth, posts, bosses | 4.55 |
| Blackwood skirt and dome, 8 mm | 2.45 |
| Burner allowance | 1.85 |
| Stainless base pan and lip, 0.8 mm | 1.76 |
| Brass cinch 14 × 1.2 and ferrules | 0.30 |
| Jarrah grips and feet | 0.10 |
| PTFE washers | 0.01 |

Against Angas that is about 13.8 kg less steel (thinner gauges and a smaller plan), 3.3 kg less insulation (30 mm-class microporous board at k = 0.030 and 250 kg/m³, instead of 100 mm of AES plus calcium silicate), 1.7 kg less stone, 1.8 kg less brass, and 0.4 kg less handle and foot timber, then 2.4 kg added back as the wood shell.

Moondancer drops the wood shell and the stainless pan. Aluminium skin 0.8 mm and aluminium base 0.9 mm, stainless cinch 12 × 0.8, wall board 37.0 mm. Analytical total 15.58 kg. The FreeCAD solid is 13.92 kg before the burner allowance, 15.77 kg ready. The 0.15 kg gap is the mouth boolean against the rectangular area the solver subtracted.

The extra mass over the Tread is the 15 inch stone and the cool skin. A 12 inch, 12 mm stone plus a hot single layer is how 13.5 kg is reached. This oven does not take that trade.

## Temperatures

1D model, 500°C gas, 20°C air, h_in = 25, h_ext = 10. Underside uses a 430°C deck. CalculiX, meshed in Gmsh, recovered the wall to the tenth of a degree. A homogeneous 30 mm slab at k = 0.030 came back at 62.11°C against 62.11°C from the resistance sum, which is the check that the film and the element faces are wired correctly.

| | Morning | Moondancer |
|---|---|---|
| 1D outer skin | 50.0°C wood | 55.0°C, 54.95°C after the board was rounded up to 37.0 mm |
| CalculiX outer skin | 50.0°C | 54.95°C |
| Wood inner face | 65°C, limit 75°C | no wood |
| Underside | 60°C | 60°C |
| Grip, 1D network | 25.3°C | 26.2°C |
| Grip, CalculiX mean / max | 21.3 / 27.4°C | 21.5 / 28.6°C |

The handles sit on the dome shoulder, about 50° up the dome curve from the spring line, stood off 16 mm on four Ø6 stainless posts with 3 mm PTFE washers. The bars are Ø22 × 130 jarrah. The hottest point on a bar in the mesh is under 29°C.

## Shop

Morning's wood is segmented rings or staves. Table saw, thicknesser, WorkBee. No bowl lathe will swing this drum, and none is assumed. The makerspace lathe turns the ferrules, the grips, and the three short jarrah feet. The 0.6 mm 304 liner is university workshop TIG. The CO2 lasers cut templates, not steel.

Moondancer has no wood shell. The same university shop rolls and TIG-welds the liner and the aluminium skin. The board is trimmed on the WorkBee. The grips are turned at the makerspace.

## Left for later, already in the solid

Four M5 bosses on a 120 mm pitch circle on the crown, for a top rack. Four M6 bosses on a 220 mm square under the pan, for a Tread-style stand. Their mass is in the total. The rack and the stand are not.

## Files

- `cad/freecad/optimize.py` — the mass minimisation
- `cad/freecad/drive.py` — FreeCAD through the freecad-mcp headless runner
- `design/variants/morning/` and `design/variants/moondancer/` — FCStd, STEP, exploded STEP, GA sheet
- `design/variants/thermal-fea.json` — slab, wall, and grip results
- `design/tailgate/argon/05-critique.md` — one critique round each. Both held.
