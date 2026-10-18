# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-18T21:59:11Z
**Current Branch / Commit:** tools/opus-harness @ c122d4d
**Overall Status:** UNDER_REVIEW

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
