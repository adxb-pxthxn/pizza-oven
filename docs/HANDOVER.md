# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-20T10:45:00Z
**Current Branch / Commit:** design/stream-1-original, with origin/main @ 5254441
**Overall Status:** IN_PROGRESS

---

## 1. Executive Summary (10-Second Briefing)
Best oven on this branch is Caraxes: Grey Ghost's door and skin, with a finger hollow in the grip. 38.7 kg, pizza floor 305°C, cool-down 42 min, 0.67× the Tread. Shop sheet is `design/stream-1/caraxes/BUILD.md`. Inspiration pass 11 (Tokyo kamado benches, 2026-10-20) is in the shop sheet: the chamber is the case. Caraxes stays gas.

Stream 2 is on `main` as 5254441. Terrax is the current stack there: 34.1 kg, brow, tunnel, and door grips on mild pads, Quicksilver pintle. Shop sequence is `design/stream-2/terrax/BUILD.md`.

Morning and Moondancer are on `main`. Morning is the blackwood body, 19.12 kg ready. Moondancer is the aluminium shell, 15.57 kg ready. Both keep the Angas dome, mouth, and burner crescent. FreeCAD solids seat without unintended interference. The press fits are the Morning ferrules and the cinch dowels. CalculiX still matches the skin temperatures.

`tools/opus/` is a Claude Opus 5.5 harness for CAD, render, and build-doc tasks, merged from `main`. It resolves the model id from `GET /v1/models`, bills input, output, and cache tokens into `tools/opus/ledger.jsonl`, and treats `declare_done` as separate from a passing `check()`. The live model call was not made here: `ANTHROPIC_API_KEY` is not in this environment. Offline tests pass with `python3 tools/opus/test_opus.py`.

---

## 2. Completed in This Session
- [x] Shop stack and heat model in `cad/freecad/stream_physics.py`.
- [x] Stormcloud solid, interference gate, four views.
- [x] Tyraxes solid. Door xmax −337.8 mm, skin xmin −334.8 mm. Ferrule press fits only.
- [x] Arrax solid. Sill ymax −86.8 mm, steel ymin 40 mm, side gap 10 mm. 43 solids.
- [x] Vermax solid. Plate ymin 280 mm, broil bay 240 mm, 48 solids, ferrules only.
- [x] Tessarion solid. Door starts 3 mm above the deck. Sill top is 1 mm below it. Bread pose.
- [x] Opus harness in `tools/opus/opus.py`: bash, read, write, and wrappers for build, interference, thermal, mass, and render.
- [x] Budget ledger, $21 default cap, per-task caps, prompt-cache breakpoints on the system prompt and tool list.
- [x] Starter tasks: textured render, mass iteration under 20 kg, BUILD.md plus a cutting template.
- [x] `python3 tools/opus/test_opus.py` passes with no network.

## 2b. Stream 2 (from main)
Terrax is the current stack. The brow grip, the tunnel grip, and the door grip each stand on a 1.5 mm mild pad. The posts clear the skin by 1.5 mm. Quicksilver's pintle stays: the lower arm welds to the pit, and the brow lifts off the pin. Door face 53.7°C, door grip 23°C. Pit 11.0 kg. Hearth 9.1 kg. Brow 5.8 kg. Tunnel 8.3 kg. Ready 34.1 kg. Mouth 424 × 185. Hood skin 55.0°C, CalculiX agrees. Heat-up 11 min. Bread window 61 min. Pack cool-down 27 min with the door open. Wood stays 3.4 mm off hot steel. Flux stays 13.8 kW/m². The door grip pulls the door. It is not a lift. Stream 1 uses Stormcloud, Tyraxes, Vermax, Arrax, Tessarion, Sunfyre, Grey Ghost, and Seasmoke. Do not reuse those. The book dragons are now used on one stream or the other. Do not take a show name. Recheck stream 1 before any new name. The sheet module is 20 mm for the pads, the wind-back, and the rivet pitch. The mouth and the deck stay off it. Aluminium is flat blanks. The cowl is two plates with a gap at the joint. The bail lifts the hearth. The tailgate is the stand. Shop sequence is `design/stream-2/terrax/BUILD.md`. See `design/stream-2/README.md`.

## 3. Immediate Next Steps (For Incoming Agent)
1. Caraxes is the oven to build on this branch. A further dragon needs a new measured fault, and a stable one gets its own `BUILD.md`.
2. Re-read `inspiration.md` in `/cursor/stores/store-97fe1fa0-fd19-44b4-ac7d-36d872774744/` every few iterations. It updates about every 3 hours. Wright is first. Pass 11 (2026-10-20, Tokyo) is adopted only where it fits a gas oven:
   - The chamber is the transport case. Order is hose, bagged mild plate, sky plate, door as the lid. The cotton bag is ST-220.
   - Spring-line joint gets a soft silicone bead. Vertical fascia joints are dressed flush. The sill falls 1 mm toward the front. The spring-line tabs are the drip edge.
   - Coal hook heights are for a wood fire bed. This oven is gas. The sky plate's two poses stay the heat settings.
   - The door does not grow legs. The peel rest stays a ledge. A tapered captive seat would close the 3 mm sill gap. The pin still lifts out.
   - Weighed 2026-10-18, and this still stands:
   - 20 mm module stays. It divides a 1200 mm sheet and the 480 mm plate, and it is scribed on the sill only.
   - No board-and-batten on the skin. The skin is 55°C, the carry is already 38.7 kg, and the long barrel is the horizontal line. Wood stays on the grips, ferrules, peel rest, and door pull.
   - The broil tray stays parked outside the port skin. A flush recess would pocket a hot tray in the cladding. The sky plate is the mode change.
   - No side flues. Gas leaves by the mouth. A chimney would open the bread equilibrium.
   - No levelling screws under the plate. It grows 1.95 mm and stays free on the buttons.
   - No baffle that touches both the liner and the skin. The blanket stays continuous.
   - Grips stay fixed on the cheek straps.
3. The sky plate stays removable. Argon answers text. Do not pull a sandbox over `/workspace`.
4. Export `ANTHROPIC_API_KEY` and run `python3 tools/opus/opus.py ping`, then `probe` if the worst-case line stays under $0.05.
5. Launch one task with `python3 tools/opus/opus.py run --task tools/opus/tasks/render-textured.yaml`. The other two files are `mass-under-20kg.yaml` and `build-doc.yaml`.
6. Read `design/variants/COMPARISON.md` before changing a thickness. The gauges are on the solver bounds.
7. Do not put either oven on the lowered tailgate. Plans are Ø572 and Ø547.
8. Rebuild with `FREECADCMD` pointing at FreeCADCmd: `python3 cad/freecad/drive.py morning`.

## 4. Guiding Invariants
- Fuel is gas. Stream 1 floor is normalised mild steel, free, no cordierite, no zinc. Stream 2 cooking geometry stays with its own optimizer. New Angas numbers live in `design/variants/optimizer.json`.
- Skin aim 55°C, hard touch limit 60°C. Underside 60°C. Grip 40°C. No galvanised zinc in the hot path. Liner and stone pan are 304 where a stone is used. Morning's wood inner face is 65°C.
- Hardware CERN-OHL-P v2. These notes CC-BY-4.0.
- Commit format: conventional commit with an agent signature, e.g. `feat(stream): subject [agent:cursor]`.

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `cad/freecad/stream_physics.py`, `design/stream-1/`, `design/stream-2/`, `tools/opus/`, `cad/freecad/`, `design/variants/`, `tools/freecad_mcp/`, `bom/bom.csv`. Web meshes sit beside the STEP files: `morning.glb`, `moondancer.glb`, and the matching STL.
- **Mass to believe:** FreeCAD solid plus the 1.85 kg burner allowance. Morning 19.12 kg. Moondancer 15.57 kg. Caraxes ready mass is 38.7 kg. Terrax ready mass is 34.1 kg.
