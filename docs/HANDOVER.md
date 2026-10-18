# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-18T12:40:00Z
**Current Branch / Commit:** cursor/parametric-cad-toolchain-25df
**Overall Status:** READY_FOR_NEXT_AGENT

---

## 1. Executive Summary (10-Second Briefing)
A build123d toolchain is in place for a placeholder oven envelope (floor slab, half-cylinder shell, insulation layer). Dimensions are named millimetre fields in `cad/parameters.py`. `python3 -m cad.build` writes STEP AP214 and STL into gitignored `cad/output/`. Those numbers are not a design: fuel, materials, and real dimensions are still unset.

## 2. Completed in This Session
- [x] Parametric package: `cad/parameters.py`, part builders, placeholder assembly.
- [x] Pinned `build123d==0.13.0` and `cadquery-ocp-novtk==8.0.1.1.0`, with macOS arm64 wheel notes in `cad/README.md`.
- [x] Unit tests for volume, bounding box, parameter propagation, and STEP/STL export.
- [x] Agent skill `.agents/skills/cad/SKILL.md` and AGENTS.md build/test notes.
- [x] Cloud VM install of the pinned wheels succeeded (Python 3.12, Linux x86_64). The default image still does not preinstall them.

## 3. Immediate Next Steps (For Incoming Agent)
1. Wait for the user to specify fuel, capacity, materials, and dimensions before replacing the placeholder.
2. To regenerate geometry: install `cad/requirements.txt`, then `python3 -m cad.build`.
3. To check the model: `python3 -m unittest cad.tests.test_placeholder_assembly`.

## 4. Invariants & Physical Gotchas
- **Placeholder:** Do not copy a commercial oven's dimensions into `cad/parameters.py`.
- **Units:** Millimetres. STEP export is AP214 with `SI_UNIT(.MILLI.,.METRE.)`.
- **Kernel:** `cadquery-ocp-novtk` only. Do not also install the VTK package `cadquery-ocp`.
- **Outputs:** `cad/output/` is gitignored. Do not commit STEP or STL.
- **OSHWA:** Placeholder solids are not BOM rows. Add `bom/bom.csv` rows when a real part is specified.
- **Material safety:** When materials are chosen, verify food contact (FDA / EU 1935/2004) and keep galvanized zinc out of heated zones.

## 5. Active Locks & Touched Files
- **Active Locks:** None.
