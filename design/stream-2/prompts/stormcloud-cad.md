Write the FreeCAD builder for Stormcloud, the first modular prototype.

Return the file with these markers and no other files:

===== FILE cad/freecad/build_stack.py =====
...complete python...
===== END FILE =====

The builder runs under freecadcmd:

python3 -c is not available inside FreeCAD. The driver will exec this module and call build("stormcloud").

Contract
- Import Stack, parts, PRESS_FITS, and evaluate from cad.freecad.stacklib. The driver puts the repository root on sys.path.
- The only design is Stack(dragon="Stormcloud", deck_t=4.0, ins_t=26.4, floor_ins=18.0, belly_ins=22.0, liner_t=0.6, skin_t=0.6, pit_t=1.0, front_h=256.0, soffit_h=118.0, air_gap=12.4, standoff=55.0).
- Build every solid from parts(design). Do not invent a second set of dimensions, and do not drop or merge parts.
- Boxes: Part.makeBox(dx, dy, dz, App.Vector(x, y, z)) using corner and size. All sizes are positive.
- Tubes: a cylinder of r_out and length along the given axis, then cut a concentric cylinder of r_in when r_in > 0. Axes are only [1,0,0], [0,1,0], or [0,0,1]. Origin is the centre of the start face.
- Revolves: GRIP profile is (axial_mm, radius_mm). Close the profile to the axis, make a face, and revolve 360 degrees about the part axis through the part origin. Support axis [1,0,0] and [0,1,0].
- No fillets. No sketches. No PartDesign. Select nothing by Edge or Face index.
- Add each solid as a Part::Feature. Label is "{id}|{module}|{material}|{zone}".
- Skip material "keepout" for the mass sum but still build it and include it in interference. Its volume is not steel.

Gates, all written to design/stream-2/stormcloud/gate.json. Raise SystemExit on failure.
- After recompute, every shape isValid and has a positive volume. Install a console observer and fail if the report contains "Error", "Recompute failed", or "subshape".
- Part count equals len(parts(design)). Ids match.
- Pairwise common() volume. Volume is in mm^3. Any pair not in PRESS_FITS with common volume > 1.0 fails, and the message names both ids and the volume. Each PRESS_FITS pair must have common volume > 1.0.
- Bounding box within 3 mm of evaluate(design)["bbox_mm"] on every side.
- Sum of solid masses from the same densities as stacklib, ignoring keepout, within 3% of evaluate(design)["ready_kg"] minus the 1.85 kg burner allowance.

Drawings
- Write design/stream-2/stormcloud/stormcloud.FCStd and stormcloud.step (compound of every solid except keepout).
- Also write stormcloud-pit.step containing only module "pit" except the keepout, for the fire-pit configuration.
- Section: copy the compound, cut it with a box that removes x > 0, and draw that as the section.
- Views, same projection method as the attached build_variant.py (_oriented_view, _render_png, _sheet): front looks at the mouth from -Y, side from -X, top from +Z, section is the cut solid from -X.
- Write front.png, side.png, top.png, section.png, and ga-arrangement.svg in design/stream-2/stormcloud/.
- Title the sheet "Stormcloud — modular stack". Note the three modules, the floating deck, the rear gutter, and the soffit. Dimensions in mm. Do not claim a stone or a dome.

Origin: mouth plane on the deck centreline, +X right, +Y into the oven, +Z up, deck top at Z = 0.

Do not add explanatory prose outside the file markers.
