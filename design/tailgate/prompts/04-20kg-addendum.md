The coordinator is adding constraints to the Angas 430 rework you are locking. Keep the cooking geometry, the 20.0 kg cap, the surface limits, and the two-variant split. Do not start a third concept.

## Names

Dragon names follow project chronology, not mass. Angas is the pre-dragon baseline and keeps the name Angas. These two variants are both early-stage prototypes, so each one takes one of the smallest, youngest, weakest dragons. Do not use a great dragon (not Balerion, Vhagar, Meraxes, Caraxes, Syrax, Meleys, Vermithor, Silverwing, Sunfyre, Dreamfyre, Tessarion). Morning and Sheepstealer are the tier to think in: young or slight, not the monsters. Sheepstealer itself is a bit large for this stage; prefer two that are smaller than that, for example Morning, Moondancer, Arrax, Vermax, Tyraxes, Stormcloud, Shrykos, Morghul. Pick exactly two, one per variant. The lighter variant does not automatically get the smaller name. State the names in the locked parameter blocks as `name`.

## What the coordinator will run after you lock the numbers

Say, in a short section, what each of these must be given so the check is meaningful. Do not redesign the oven around the tool.

1. FreeCAD, driven through the freecad-mcp headless runner (`execute_code_headless` / `freecadcmd`). The script builds both variants as native FCStd documents, exports STEP, and generates the general arrangement from the FreeCAD model. Mac headless is the target. No GUI click-path.

2. A mass minimisation with scipy.optimize. Decision variables are the thicknesses you are willing to move (sheet gauges, insulation thickness, stone thickness, stone diameter if it stays at or above 420 mm). Constraint: ready mass ≤ 20.0 kg, and the 1D outer-skin temperature at or under the limit you already set (bare metal ≤ 60°C, wood inner face ≤ 80°C). Objective: minimise ready mass. Report the starting point, the bounds, and the optimum you expect the solver to find. If your locked design is already on that optimum, say so and give the bounds anyway.

3. A steady-state thermal check, Gmsh mesh, CalculiX (ccx) solver. Two solids are enough: a slice or a simplified axisymmetric-equivalent wall stack through the side wall, and a handle bar with its standoff and thermal break. Verify the outer skin and the grip, not the whole oven. State the temperatures the solve should match, within a few degrees of your 1D result. If the 3D grip is hotter than a bare hand can hold, change the break now, in this note, and show the new mass.

## Return

Only the delta from a finished design, not a retelling of the whole oven:

- The two dragon names, and which variant wears which.
- Any number that changes because of the grip check or the optimiser bounds.
- The scipy decision variables, bounds, and the mass and skin temperature at the optimum.
- The CalculiX boundary temperatures (gas side, ambient, grip) you want the mesh to recover.
- The locked ready mass of each named variant, still ≤ 20.0 kg, stone included.

If you have not finished the part tables yet, finish them in this same reply and then apply this note. Arithmetic still has to sum in view of the reader.
