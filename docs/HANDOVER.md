# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-18T22:44:55Z
**Current Branch / Commit:** design/stream-1-original
**Overall Status:** IN_PROGRESS

---

## 1. Executive Summary (10-Second Briefing)
Best oven is Caraxes: Grey Ghost's door and skin, with a finger hollow in the grip. 38.7 kg, pizza floor 305°C, cool-down 42 min, 0.67× the Tread. Shop sheet is `design/stream-1/caraxes/BUILD.md`. Inspiration was re-read at 2026-10-18T22:37Z (five Wright lessons, then Klättermusen). Caraxes stands.

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

## 3. Immediate Next Steps (For Incoming Agent)
1. Caraxes is the oven to build. A further dragon needs a new measured fault, and a stable one gets its own `BUILD.md`.
2. Re-read `inspiration.md` in `/cursor/stores/store-97fe1fa0-fd19-44b4-ac7d-36d872774744/` every few iterations. It updates about every 3 hours. Wright is first. Weighed 2026-10-18, and the direction stays:
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
- Fuel is gas. Floor is normalised mild steel, free, no cordierite, no zinc.
- Skin aim 55°C, hard touch limit 60°C. Underside 60°C. Grip 40°C.
- Commit format: `feat(stream): subject [agent:cursor]`.

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `cad/freecad/stream_physics.py`, `design/stream-1/`, `tools/opus/`, `cad/freecad/`, `design/variants/`, `tools/freecad_mcp/`, `bom/bom.csv`. Web meshes sit beside the STEP files: `morning.glb`, `moondancer.glb`, and the matching STL.
- **Mass to believe:** FreeCAD solid plus the 1.85 kg burner allowance. Morning 19.12 kg. Moondancer 15.57 kg. Caraxes ready mass is 38.7 kg.
