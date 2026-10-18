You are modelling one pizza-oven prototype in your Linux sandbox. Write FreeCAD Python, run it, read the failures, and change the script. Repeat until the checks below pass. Do not stop after one attempt. Do not describe a fix you have not run.

The oven is Stormcloud. It is not Morning, not Moondancer, and not a hemisphere. Do not edit cad/freecad/masslib.py, cad/freecad/build_variant.py, or anything under design/variants/. Write one new script: cad/freecad/stream_build.py. Read the shop design from design/stream-1/optimizer.json key "stormcloud" "design", and construct a Vault from cad/freecad/stream_physics.py. Every placement is an expression of those fields plus one HARDWARE dict. No bare millimetre offsets that a reviewer cannot trace.

Cooking geometry, millimetres:
- Half-barrel axis along +Y. Axis height is the cooking surface. Mouth plane is Y=0. Rear head is Y=length (680). +Z is up. The arch is Z greater than or equal to the cooking surface. X is width, port is negative X.
- Internal radius 250. Internal length 680. Mouth 430 wide by 158 high, cut through the front end only, centred on X, sill at the cooking surface.
- Cooking floor is mild steel 450 by 500 by 6, free on six domed buttons. It is not bolted. Side gap to the liner spring is (2*radius - steel_w)/2. Front edge is at Y=landing (40). Rear edge is landing+steel_l. Leave at least 0.3 mm between the plate and every other solid.
- Sky plate is 1.2 mm stainless, in the pizza position, on two rails, about plate_drop (95) below the crown so its underside is radius-plate_drop above the cooking surface. Slide clearance 0.4 mm above the rails. It does not touch the liner.
- Ceramic fibre 75 mm on the arch and the ends, 50 mm under the floor. Aluminium skin 1.0 mm outside an 8 mm air gap. The air gap is empty. Fibre must not occupy the air gap or the liner.
- 304 liner 0.8 mm. Rear burner box is a stainless box outside the rear head, 0.5 mm clear of the liner, flame slot cut in the rear head above the steel. Do not model a jet, a valve, or a hose. Burner mass is an allowance, not a solid.
- Door is shut, in front of the mouth, 2 mm clear of the front skin. Hinge on the port side. Jarrah pull stood off the door face. Throat hood is a stainless lip inside the arch, above the mouth, 40 mm deep, clear of the sky plate.
- Handles: one each side, at handle_phi 42 degrees up from the spring line, at mid-length. Jarrah bar 140 long, 36 tall, 28 deep, parallel to Y, with a finger groove. Two stainless posts per grip, diameter 6, standoff from the design, PTFE washer 3 mm. Gidgee ferrules are the only press fit: 0.2 mm radial interference on the grip ends. Name that pair in the report.
- Four M5 rack bosses on the crown. Four M6 stand bosses under the base. Four rubber feet. Do not model the top rack or the stand.
- No cordierite, no galvanised zinc, no wood on the arch. Wood parts are the grips, the ferrules, the peel rest, and the door pull.

Pass criteria:
1. freecadcmd exits 0. Every solid isValid. A console observer records Report View errors, and any error fails the run.
2. Pairwise common volume under 1 mm3, except the named gidgee ferrule press fit. Print every pair at or above 1 mm3.
3. Measured bounding box within 15 mm of length 850, width 670, height 396, plus the feet. Mouth opening present. Steel thickness 6. Count of handle grips is 2.
4. Render front.png, side.png, top.png, section.png. Front looks at the mouth. Side looks along the hearth from the port side and shows a long barrel, not a circle. Top looks down and shows a long plan, not a round plan. Section is Y-normal through X=0 and shows the steel, the fibre under it, the air gap, the sky plate, and the mouth. Open each PNG. If the mouth is not on the front, the plan is round, the section misses the floor, or a view is mislabelled, fix it and write what you changed.
5. Write design/stream-1/stormcloud/gate.json with bbox, solid count, invalid names, interference pairs, press-fit volume, and one line per PNG saying what you saw.
6. Write FCStd and STEP beside the PNGs. Do not put STEP or FCStd bytes in the answer.

Install FreeCAD if freecadcmd is missing. Headless Part API only. No PartDesign. No EdgeN ids. If a boolean crashes the process, rebuild that part as a simpler primitive and try again.

In the final message, emit the script, gate.json, and each PNG under 200 KB with these markers only:

===== FILE relative/path/from/workspace =====
file text
===== END FILE =====

===== B64 relative/path/from/workspace =====
base64 one line
===== END B64 =====

End with this line only if the gates passed:
STORMCLOUD_PASS
