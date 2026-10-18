# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Current Branch / Commit:** research/argon-anatomy
**Overall Status:** STUDY_READY_FOR_REVIEW

---

## 1. Executive Summary (10-Second Briefing)
A reverse-engineering study of Gozney Arc Lite (GOZ-3102), Tread (GOZ-1893), and Dome XL Gen 2 (GOZ-2509) is on `research/argon-anatomy`. It does not lock a project design. `bom/bom.csv` is still the empty template. The study report, solids, and a proposed first oven live under `research/argon-anatomy/`.

Argon (`tools/argon/argon.py`) calls `gemini-4-argon` at thinking level HIGH by default. Cheap-model grunt work stays off that default.

---

## 2. Completed in This Session
- [x] Argon orchestrator with per-call thinking level or budget, default HIGH for gemini-4-argon.
- [x] Four HIGH worker analyses: geometry, why, materials, build.
- [x] Parametric reconstructions in `cad/reconstructed/` exporting STEP AP214 and STL.
- [x] Dome XL body height set to the 520 mm inference. The 219 mm callout is not the hearth.
- [x] Hardwood shell cases in `research/argon-anatomy/calcs/hardwood_shell.py`.
- [x] Section SVGs, STL renders, Dome XL anatomy figure.
- [x] Integrated report: `research/argon-anatomy/REPORT.md`.

---

## 3. Immediate Next Steps (For Incoming Agent)
1. Wait for Adib to choose a build. The study recommends the Adelaide Folded-Vault 14. Do not copy that into `bom/bom.csv` until he says so.
2. Gas parts stay bought certified (FFD, regulator, hose). Do not add injector geometry.
3. Read `research/argon-anatomy/REPORT.md` before changing `cad/reconstructed/spec.py`.

---

## 4. Guiding Invariants
- **No Premature Assumptions:** The Gozney study was an explicit request. It is not the oven this repository is building yet.
- **Material Safety Invariant:** No galvanised zinc in the hot path. Hardwood inner face stays under 80°C in the sealed-wall model (case C passes, A and B fail).
- **OSHWA Compliance:** Study CAD is CERN-OHL-P v2. The report is CC-BY-4.0.
- **Commit Format:** Conventional commit with agent signature, e.g. `feat(cad): initial floor layout [agent:cursor]`.

---

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `tools/argon/`, `cad/reconstructed/`, `research/argon-anatomy/`.
