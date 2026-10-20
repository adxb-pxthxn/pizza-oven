# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-20T10:49:00Z
**Current Branch / Commit:** design/stream-2-modular, with tools/opus from main @ 78d417d
**Overall Status:** IN_PROGRESS

---

## 1. Executive Summary (10-Second Briefing)
Morning and Moondancer are on `main`. Morning is the blackwood body, 19.12 kg ready. Moondancer is the aluminium shell, 15.57 kg ready. Both keep the Angas dome, mouth, and burner crescent. FreeCAD solids seat without unintended interference. The press fits are the Morning ferrules and the cinch dowels. CalculiX still matches the skin temperatures.

`tools/opus/` is a Claude Opus 5.5 harness for CAD, render, and build-doc tasks. It resolves the model id from `GET /v1/models`, bills input, output, and cache tokens into `tools/opus/ledger.jsonl`, and treats `declare_done` as separate from a passing `check()`. The live model call was not made here: `ANTHROPIC_API_KEY` is not in this environment. Offline tests pass with `python3 tools/opus/test_opus.py`.

---

## 2. Completed in This Session
- [x] Opus harness in `tools/opus/opus.py`: bash, read, write, and wrappers for build, interference, thermal, mass, and render.
- [x] Budget ledger, $21 default cap, per-task caps, prompt-cache breakpoints on the system prompt and tool list.
- [x] Starter tasks: textured render, mass iteration under 20 kg, BUILD.md plus a cutting template.
- [x] `python3 tools/opus/test_opus.py` passes with no network.

---

## 2b. Stream 2 (this branch)
Terrax is the current stack. The brow grip, the tunnel grip, and the door grip each stand on a 1.5 mm mild pad. The posts clear the skin by 1.5 mm. Quicksilver's pintle stays: the lower arm welds to the pit, and the brow lifts off the pin. Door face 53.7°C, door grip 23°C. Pit 11.0 kg. Hearth 9.1 kg. Brow 5.8 kg. Tunnel 8.3 kg. Ready 34.1 kg. Mouth 424 × 185. Hood skin 55.0°C, CalculiX agrees. Heat-up 11 min. Bread window 61 min. Pack cool-down 27 min with the door open. Wood stays 3.4 mm off hot steel. Flux stays 13.8 kW/m². The door grip pulls the door. It is not a lift. Stream 1 uses Stormcloud, Tyraxes, Vermax, Arrax, Tessarion, Sunfyre, Grey Ghost, and Seasmoke. Do not reuse those. The book dragons are now used on one stream or the other. Do not take a show name. Recheck stream 1 before any new name. The sheet module is 20 mm for the pads, the wind-back, and the rivet pitch. The mouth and the deck stay off it. Aluminium is flat blanks. The cowl is two plates with a gap at the joint. The bail lifts the hearth. The tailgate is the stand. The pit packs the rod bag, wind-back, broiler plate, and door. Coal uses the upper grate hooks. Shop sequence is `design/stream-2/terrax/BUILD.md`. See `design/stream-2/README.md`.

## 3. Immediate Next Steps (For Incoming Agent)
1. Export `ANTHROPIC_API_KEY` and run `python3 tools/opus/opus.py ping`, then `probe` if the worst-case line stays under $0.05.
2. Launch one task with `python3 tools/opus/opus.py run --task tools/opus/tasks/render-textured.yaml`. The other two files are `mass-under-20kg.yaml` and `build-doc.yaml`.
3. Read `design/variants/COMPARISON.md` before changing a thickness. The gauges are on the solver bounds.
4. Do not put either oven on the lowered tailgate. Plans are Ø572 and Ø547.
5. Rebuild with `FREECADCMD` pointing at FreeCADCmd: `python3 cad/freecad/drive.py morning`.

---

## 4. Guiding Invariants
- **No Premature Assumptions:** Fuel is gas. Cooking geometry is the Angas 430. New numbers live in `design/variants/optimizer.json`.
- **Material Safety Invariant:** No galvanised zinc in the hot path. Liner and stone pan are 304. Morning's wood inner face is 65°C.
- **OSHWA Compliance:** Hardware CERN-OHL-P v2. These notes CC-BY-4.0.
- **Commit Format:** Conventional commit with agent signature, e.g. `feat(cad): initial floor layout [agent:cursor]`.

---

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `tools/opus/`, `cad/freecad/`, `design/variants/`, `tools/freecad_mcp/`, `bom/bom.csv`. Web meshes sit beside the STEP files: `morning.glb`, `moondancer.glb`, and the matching STL.
- **Mass to believe:** FreeCAD solid plus the 1.85 kg burner allowance. Morning 19.12 kg. Moondancer 15.57 kg.
