You are modelling two early pizza-oven prototypes in your own Linux sandbox. Write FreeCAD Python, run it, read the failures, and change the scripts. Repeat until both models pass the checks below. Do not stop after one attempt. Do not describe a fix you have not run.

The files already mounted under /workspace are the current design. Edit those. Keep the dragon names Morning and Moondancer. Angas is the baseline and is not one of these two.

Locked cooking geometry, from cad/freecad/masslib.py. Do not change these:
- Chamber diameter 470 mm, skirt height 120 mm, dome rise 45 mm, apex 165 mm.
- Mouth 420 mm wide by 95 mm high.
- Stone diameter 420 mm, stone thickness 15 mm. A 15 inch pizza must keep at least 19.5 mm radial clearance.
- Burner mass allowance stays 1.85 kg. It is not a fabricated solid. Do not include a burner box in the interference check. Keep the crescent clear of the stone and the liner.
- Gauges, insulation thicknesses, species, and band sizes come from design/variants/optimizer.json. Do not thin a part to make a clearance. Morning is the blackwood body with a stainless base, a brass band, brass ferrules, and jarrah feet. Moondancer is the aluminium skin and base, a stainless band, no ferrules, and rubber feet. Grips are jarrah on both.
- Ready mass, FreeCAD solid plus the 1.85 kg allowance, stays at or under 20 kg. Morning is about 19.2 kg. Moondancer is about 15.8 kg.
- Temperatures already checked stay inside their limits: Morning wood outer 50 C, wood inner face at or under 75 C, Moondancer metal skin at or under 55 C, underside at or under 60 C, grip at or under 40 C. Do not change insulation to chase this round.
- Handles sit high on the dome shoulder, both sides, jarrah grip diameter 22 mm and length 130 mm, standoff 16 mm, four stainless posts diameter 6 mm, PTFE washers. The handle angle is a named parameter.
- Future top rack: four M5 bosses only. Future stand: four M6 bosses only. Do not model the rack or the stand.
- No galvanised zinc. Liner and stone pan stay stainless. Fuel is gas. No jet is drawn.
- The crown still lifts in the exploded STEP. The lift distance is one named parameter.
- Plans stay wider than the lowered tailgate. Do not shrink the oven onto a 517 mm deck.

What is wrong in cad/freecad/build_variant.py:
- Positions use bare millimetre offsets: mouth cutter depth stack+24, frame at outer_r+1.5, landing 40 mm, stone shift 10 mm, grip ends at y -65 and +40, ferrules at -65 and +57, feet at 0.72 times the outer radius, band 2 mm under the spring, rack radius 60, stand corners at 110, explode 80. Replace each placement with an expression of the shared parameters (chamber, stack, hearth, spring, outer radius, mouth, band width, standoff, grip length, boss pitch, stand pitch). Part sizes that are real hardware (post diameter, boss diameter, grip diameter) live in one parameter block with a name.
- Parts occupy each other. Posts, washers, ferrules, dowels, bosses, the mouth frame, and the landing need a real seat on the skin or under the pan. A boss buried in the dome, a post that starts inside the shell because it is offset in Y from the profile station, and a frame floating in front of the mouth are failures.
- The general-arrangement sheet fits three views, and the view named front still reads as a side profile. Render four separate PNGs and look at them.

Pass criteria, both Morning and Moondancer:
1. Pairwise common volume between every fabricated solid is under 1 mm3, which is the zero-volume tolerance for a boolean. Print every pair at or above that tolerance. Intended press fits are allowed only if you name them in the report and give their overlap volume. Expected press fits, if the geometry actually overlaps: Morning brass ferrules on the jarrah grips, and the cinch dowels through the band into the skin. Face contact is not a press fit. The burner allowance is not a part.
2. Every placement is derived from the shared parameter block. A reviewer must be able to change standoff, band width, or grip length in that block and have the posts, washers, ferrules, and grip follow.
3. Render front, side, top, and section PNGs for each variant. Front looks at the mouth. Side looks along the hearth from the port side. Top looks down on the circular plan. Section is a cut through the mouth centreline and shows the floor, the dome, and the mouth opening. Open each PNG and check it. Fix the camera or the model when the mouth is not centred on the front, the handles are not a symmetric pair, the section misses the axis, the top is not a round plan, or a view is mislabelled. Write what you saw in the report, including what you changed after looking.

Write these files in the sandbox:
- The updated FreeCAD scripts under /workspace/cad/freecad/.
- /workspace/design/variants/interference-report.md with the pair table, the press-fit list, the parameter block, and the PNG inspection notes for both dragons.
- /workspace/design/variants/morning/front.png, side.png, top.png, section.png
- /workspace/design/variants/moondancer/front.png, side.png, top.png, section.png
- FCStd and STEP beside the existing exports, regenerated from the scripts you ran.

Install FreeCAD in the sandbox if freecadcmd is missing. Use the FreeCAD Python API headless. If the install or the import fails, stop and put the exact error in the report. Do not invent volumes or claim a render you did not open.

In your final message, after the checks pass, emit the sources and the report so they can be copied out. Use this framing and nothing else around each file. Do not put STEP or FCStd bytes in the message. Do put each PNG if it is under 200 KB; otherwise say which path was too large.

===== FILE relative/path/from/workspace =====
file text
===== END FILE =====

===== B64 relative/path/from/workspace =====
base64 one line
===== END B64 =====

End with two lines, only if that variant passed:
INTERFERENCE_PASS morning
INTERFERENCE_PASS moondancer
