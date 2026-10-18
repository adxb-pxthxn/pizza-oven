# Caraxes — Makerspace Adelaide

Shop sheet for the stable oven. Gas, 15 inch pizza, ready mass 38.7 kg, overall 1080 × 727 × 435 mm. Two people carry it by the side grips. The chamber is a rolled half-barrel, internal radius 250 mm, length 780 mm. Cooking surface is at Z = 86.4 mm. Barrel axis is +Y, mouth at Y = 0.

Hardware is CERN-OHL-P v2. This sheet is CC-BY-4.0.

The 20 mm module is the only grid in the build: rivets at 40 mm, and three scribed lines on the launch sill. The aluminium skin ships as the flat laser blank `skin.dxf`. Wood is the grips, the gidgee ferrules, the peel rest, and the door pull. The broil tray is a steel arm that parks outside the port skin.

General tolerance ISO 2768-mK. The fits below are tighter than that and are the ones to check.

## Safety

- Ceramic fibre is a respiratory irritant. Wear a P2 mask, gloves, and long sleeves. Cut it with a knife. Bag the offcuts. Do not blow it out with compressed air.
- No galvanised sheet, zinc-plated fasteners, or zinc anti-seize anywhere the gas can reach. Zinc fume and a food surface are both out. No paint on the liner, the plate, the sky plate, or the grate.
- TIG under argon, with the booth extraction on. Stainless filler for 304. Aluminium filler (4043 or 5356) for the base and the hinge post. Do not weld the two families together.
- The oven is 38.7 kg. Lift by the jarrah grips, two people. The grips are on the cheek straps.
- At a 500°C broil the aluminium skin is about 55°C and the bare bay underside about 56°C. The liner and the sky plate are at gas temperature. The grip is about 23°C.
- The hinge pin is a clearance fit. It stays unwelded so the door lifts off.

## Bought, not made

Certified gas burner, flame-failure device, regulator, and hose. Allow 1.85 kg. The rear box only covers them. AS/NZS 3678-250 normalised plate, 480 × 500 × 6 mm, if the merchant will cut it. 25 mm AES ceramic blanket, three layers on the crown and three under the whole floor. 304 sheet 0.8 mm and 1.2 mm. Aluminium 5052-H32, 1.0 mm. Jarrah and a gidgee offcut. PTFE washers. Four rubber feet, Ø32 × 10 mm.

## 1. Pizza steel

Machine: merchant shear, or the bandsaw. This plate is not a laser part.

1. Cut 480 × 500 × 6 mm. Deburr. Leave the faces bare.
2. Drill nothing. Weld nothing. The plate is free.
3. Growth across 480 mm at 320°C is 1.95 mm. The stops are set 4 mm off, so the plate can grow and still not walk onto the sill.
4. Season it on the first firing. No oil that is sold as a paint, and no zinc-rich coating.

Check: 480.0 × 500.0 × 6.0 mm. Flatness within 0.3 mm before the first fire. Side gap to the liner is 10 mm once it is sitting.

## 2. Liner

Machine: slip roll, then TIG. Cradle: two MDF half-rings, inside radius 250.8 mm, centres about 500 mm apart, so the seam sits up.

1. Roll 0.8 mm 304 to an inside radius of 250 mm. Developed mid-thickness arc is π × 250.4 mm. Length between end discs is 779.4 mm (0.3 mm seam at each end of the 780 mm chamber).
2. One longitudinal seam, TIG, full penetration, food side dressed flush. Argon, stainless filler.
3. Two half-discs, radius 250.8 mm, 0.8 mm. TIG them on.
4. Front disc: half-ellipse mouth, 430 mm wide × 158 mm high, centred on the axis. Laser the ellipse in the flat disc, nitrogen assist, before it is welded on.
5. Rear: burner slot 120 × 22 mm, centred, with its middle at Z = 241 mm. Nibbler or laser. The fibre and the skin get the same opening later, lined up on this one.

Check: mouth 430 × 158. No zinc. The seam does not print a ridge onto the blanket.

## 3. Fibre

Machine: knife and a straightedge on the bench. Templates can be drawn; do not cut blanket on the CO2 laser.

1. Three layers of 25 mm blanket on the arch, from the liner OD out to radius 325.8 mm. Three layers under the whole floor, 480 × 500 mm, from Z = 1 mm up to Z = 76 mm. The floor stack is the same thickness everywhere. A step would tilt the plate.
2. Keep an 8 mm air gap outside the crown blanket, out to the skin at radius 333.8 mm. Do not pack that gap.
3. Cut the mouth and the burner slot through the blanket to match the liner. The probe does not get a hole in the blanket.

## 4. Skin

Machine: laser for the blank, slip roll for the barrel, pan brake for the tabs.

File: `skin.dxf`. Layers are ROLL, TAB, RIVET, FASCIA, MARK. Kerf is about 0.2 mm; the DXF is the finished profile, so compensate in the laser. Sheet is 5052-H32, 1.0 mm, blank 1074.2 × 779.4 mm.

1. The two long ROLL lines are the spring lines. The arc between them is 1050.2 mm, the mid-thickness development at radius 334.3 mm. Roll that region to an inside radius of 333.8 mm. A cardboard half-template at three stations along the 779.4 mm length is the check. Crown up, seam gap 0.3 mm at each end.
2. Brake each 12 mm tab 90° down, along the ROLL line, after the roll. Inside radius 1 mm, K = 0.40, V-die 8 mm. Bend allowance for that fold is 2.2 mm and it is already inside the 12 mm tab, so do not lengthen the arc. Hole centres sit 6 mm off the bend, which clears the 3.5 mm minimum.
3. Rivet holes are Ø4.2 on a 40 mm pitch, 20 mm off each end, both spring lines. 4 mm aluminium rivets, grip for two 1.0 mm sheets. They fix the tabs to the base walls in section 6.
4. The MARK layer is the underside line, for transfer onto the base. Do not cut it through this skin.

The burner slot is cut after the skin is on the stack, nibbled to the liner slot. It is not in the DXF.

## 5. Fascia

Same laser job. Two half-rings, outer radius 334.8 mm, inner radius 252.8 mm.

1. The inner radius clears the liner (radius 250.8 mm) by 2 mm. Keep that gap all round. The ring covers the fibre end and sits 8 mm off the fibre face, across the air gap.
2. Clamp each ring to its barrel end. Transfer the outer-rim holes (40 mm along the arc, at 0.96 of the outer radius). Drill Ø4.2 in the skin edge and rivet.
3. Rivet the ring to the skin only. A rivet into the liner would bridge the hot shell to the cladding.

## 6. Base

Machine: laser or guillotine, pan brake or a riveted corner, TIG for the bosses and the hinge land.

1. Floor 669.6 × 949.6 × 1.0 mm. The mouth end is the short edge at the front.
2. Four walls, 1.0 mm, 85.1 mm high, so the rim stops 0.3 mm under the deck. Long walls run the full 949.6 mm. Short walls fit between them. Rivet the corners, or TIG them with aluminium filler. The spring-line tabs of the skin rivet to the top of the long walls.
3. Four stand bosses, Ø14 × 8 mm aluminium, on the underside, at X = ±160 mm and 50 mm in from each end. TIG them. They are the stand interface, M6.
4. Four rack bosses, Ø12 × 6 mm, on the crown of the skin at X = ±40 mm, Y = 390 ± 80 mm. TIG or rivet to the skin only.
5. Scribe the underside, centre of the floor, 0.3 mm deep, mirrored so it reads when the oven is lifted: `be vigilant. don't die.` Use the MARK layer. Height about 6 mm. Not on the cooking steel, and not on the sill.

## 7. Hinge post

Machine: bandsaw or mill for the sole, TIG to the base. Do this before the floor blanket goes in, so the lap is reachable.

The pin axis is at X = −379.6 mm, Y = −90.8 mm, vertical.

1. Aluminium post. A 10 mm stile stands just inboard of where the parked door will lie. It comes down to the floor. A sole 40 × 25 × 8 mm laps the inside of the front port corner.
2. TIG the sole and the foot to the base floor and the front wall. The fusion wants to be on the order of 2200 mm³. A tack into the 1 mm wall alone is not the joint.
3. Two eyes, bore Ø8.8 mm (pin Ø8 mm plus 0.4 mm radial clearance), on that axis. The pin drops through and lifts out. Do not weld the pin. No zinc anti-seize; dry graphite is enough.

## 8. Floor stack

With the tub upright:

1. Lay the three floor blankets, 480 × 500 × 75 mm, starting 40 mm back from the mouth plane.
2. Six stainless buttons, Ø10 × 4 mm, domed, on a 3 × 2 grid. X = −200, 0, +200 mm. Y = 80 and 500 mm. They sit on the blanket. The plate rests on them with a 0.4 mm float, so do not fasten it and do not shim the float out.
3. Four stops, 2 mm 304, 3 mm high, 4 mm off the plate, tops below the deck. One across the front, one across the rear, one each side. They stop a launch walking the plate out. They are not fasteners.
4. Drop the plate on. It must slide the 4 mm gap by hand, cold.

## 9. Sky plate, rails, grate, tray

Machine: laser or guillotine for the plate, TIG for the rods.

1. Sky plate 368 × 480 × 1.2 mm 304. Deburr. No holes. It slides on two rails.
2. Rails: two lengths of 304, about 8 × 8 mm, 690 mm long, full travel from Y = 70 mm to Y = 760 mm. Fix them to the liner, under the plate edges. Forward, the plate covers the deck. Rear, it leaves a 240 mm bay and the front edge sits at Y = 280 mm.
3. Five grate rods, Ø4 mm 304, 212 mm long, at X = −120, −60, 0, +60, +120 mm. Centre height is 20 mm below the mouth crown (Z = 224 mm). Tack the ends to the liner. The plate passes about 15 mm above them when it is forward.
4. Tray 160 × 120 × 1.5 mm 304, in the bay at Z = 176 mm, about 44 mm under the grate. Arm is Ø10 mm, 140 mm long, from a lug on the port liner. Parked, the tray sits outside the port skin, ahead of the grip (X beyond −384 mm, Y from 40 to 160 mm). Steel only.

## 10. Door

Machine: laser for the skins, knife for the blanket, TIG for the straps.

The door is the mouth, not a wing out to the pin.

1. Two 0.8 mm 304 skins, half-ellipse, 466 mm wide × 173 mm rise, with 12 mm of ceramic fibre between them. Overall thickness 13.6 mm.
2. Two straps, 2 × 16 mm 304, about 160 mm long, from the port jamb to the pin. Bore Ø8.8 mm. TIG the straps to the outer skin.
3. Jarrah pull, 90 × 22 × 16 mm, on the outer face, stood off 12 mm. It is what has to clear the skin when the door parks, which is why the pin sits at X = −379.6 mm.
4. Shut, the door bottom clears the sill by 3 mm, and the panel covers the arch from X = −388 mm to X = +233 mm. Open is a +90° swing about the pin, laying the door along the port side. Parked, the door's inner face is at X = −366 mm, 31 mm clear of the skin at X = −335 mm.
5. Hinge the pin only. Confirm it lifts out.

## 11. Handles

Machine: bandsaw and a spindle or the lathe. The hollow is a small cove cutter or a drum sander in a jig.

1. Cheek straps first. 2 mm 304, 40 mm along the barrel, centred at Y = 390 mm. The strap follows the skin from the spring line up to 55° above the axis, 0.4 mm clear of the aluminium, and a tab of the same strap runs down the base wall to the floor. Rivet or TIG the tab to the base wall. Posts land on this strap. They do not land on the 1 mm skin, and the strap does not touch the liner.
2. Two jarrah bars, 140 × 28 × 36 mm. In the middle 120 mm only: an 11 mm radius finger hollow on the lower inner corner, and a 3 mm chamfer on the top inner arris. The top stays full. Each end 8 mm, plus 2 mm of land, stays a sharp rectangle.
3. Four gidgee ferrules, 8 mm long, 2 mm wall. Bore is 0.2 mm under the 28 × 36 end (27.6 × 35.6 mm). Press them on. That is the only press fit in the oven, about 200 mm³ of interference each.
4. Four Ø6 mm stainless posts, 20 mm long, 28 mm in from each grip end, through a PTFE washer Ø16 × 3 mm, into the cheek strap. The grip axis is 42° up from the horizontal.

## 12. Sill, peel rest, probe, feet

1. Launch sill, 400 × 80 × 1.2 mm 304. Its top is 1 mm under the deck (Z = 85.4 mm). It sits in front of the mouth and does not touch the plate (the cold plate starts at Y = 40 mm; the sill ends at Y = −87 mm). Scribe three lines at 20 mm pitch, 0.3 mm deep, across the sill only.
2. Peel rest, jarrah, 430 × 14 × 18 mm, in front of the sill, centred on the base wall. It stays a ledge. It is not a handle and it is not a door prop.
3. Probe gland: 4 mm K-type, in a stainless gland Ø12 × 8 mm, beside the arch in the mouth frame (about 14 mm outside the mouth, 70 mm above the deck). The gland is 0.4 mm clear of the liner face and about 5 mm clear of the fibre. Drill the frame. Do not drill the blanket.
4. Four rubber feet, Ø32 × 10 mm, 50 mm in from the corners.
5. Fit the burner into the 160 × 48 × 70 mm 304 box behind the rear skin. The box is a cover. The gas train stays the certified one.

## 13. Checks before the first fire

- Plate is 480 × 500 × 6 mm, free on six buttons, 0.4 mm float, 4 mm to each stop, 10 mm to the liner each side.
- Fascia inner edge is 2 mm clear of the liner. No rivet touches the liner.
- Door lifts off the pin. Shut gap to the sill is 3 mm. Parked door clears the skin by about 31 mm.
- Grips: hollow only in the middle 120 mm, ferrules pressed on square ends, posts on the straps.
- Underside line reads from below. Sill carries the 20 mm lines. Cooking steel is bare.
- No galvanised part, no paint, no cordierite, no timber on the skin.
- First fire with the plate forward and the door shut, then open. Pizza gas 360°C holds the floor near 305°C. Bread gas 230°C, door shut, holds near 216°C. Open cool-down from the pizza floor to 60°C is about 42 minutes.
