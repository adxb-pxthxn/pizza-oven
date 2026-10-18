# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-18T15:45:00Z
**Current Branch / Commit:** cursor/angas-dragon-variants-d981
**Overall Status:** DESIGN_DRAFT

---

## 1. Executive Summary (10-Second Briefing)
Angas 430 stays the baseline on `design/tailgate-oven`. Two early prototypes sit on `cursor/angas-dragon-variants-d981`: Morning, the blackwood body, 19.2 kg ready, and Moondancer, the aluminium shell, 15.8 kg ready. Both keep the Angas dome, mouth, and burner crescent. Both are under 20 kg with the stone in. FreeCAD writes the FCStd and STEP. CalculiX matches the skin temperatures.

---

## 2. Completed in This Session
- [x] scipy SLSQP mass minimum for both variants, skin temperature as a constraint.
- [x] FreeCAD solids through the freecad-mcp headless runner. FCStd, STEP, GA sheets.
- [x] Gmsh + CalculiX steady check. Slab, both walls, both grips.
- [x] One Argon critique round per variant. Both held. `design/tailgate/argon/05-critique.md`.
- [x] Comparison in `design/variants/COMPARISON.md`. BOM rows MR-* and MD-*.

---

## 3. Immediate Next Steps (For Incoming Agent)
1. Read `design/variants/COMPARISON.md` before changing a thickness. The gauges are on the solver bounds.
2. Do not put either oven on the lowered tailgate. Plans are Ø572 and Ø547.
3. Do not add the rack or the stand. The bosses are the interface. Their mass is already in.
4. Rebuild with `FREECADCMD` pointing at FreeCADCmd: `python3 cad/freecad/drive.py morning`.

---

## 4. Guiding Invariants
- **No Premature Assumptions:** Fuel is gas. Cooking geometry is the Angas 430. New numbers live in `design/variants/optimizer.json`.
- **Material Safety Invariant:** No galvanised zinc in the hot path. Liner and stone pan are 304. Morning's wood inner face is 65°C.
- **OSHWA Compliance:** Hardware CERN-OHL-P v2. These notes CC-BY-4.0.
- **Commit Format:** Conventional commit with agent signature, e.g. `feat(cad): initial floor layout [agent:cursor]`.

---

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `cad/freecad/`, `design/variants/`, `tools/freecad_mcp/`, `bom/bom.csv`.
- **Mass to believe:** FreeCAD solid plus the 1.85 kg burner allowance. Morning 19.2 kg. Moondancer 15.8 kg.
