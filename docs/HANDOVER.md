# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Current Branch / Commit:** design/tailgate-oven
**Overall Status:** DESIGN_DRAFT

---

## 1. Executive Summary (10-Second Briefing)
Adib's tailgate oven is the Angas 430 on `design/tailgate-oven`: a circular double-skin 304 dome, brass cinch, jarrah handles, Ø675 × 340 mm, 31.5 kg without the stone. It does not sit on the Shark tailgate. The wood body (Cask-430) and the wood-ring hybrid (Angas Binnacle) are concepts only. Gas parts stay bought certified. The draft PR targets `research/argon-anatomy`, not `main`.

---

## 2. Completed in This Session
- [x] Four Argon HIGH passes: wood body, unconstrained optimum, hybrid, critique. Files in `design/tailgate/argon/`.
- [x] Comparison and the recommendation in `design/tailgate/CONCEPTS.md`.
- [x] Parametric model `cad/tailgate/`, STEP AP214 and STL in `design/tailgate/models/`.
- [x] GA sheets in `design/tailgate/drawings/`, shaded views in `design/tailgate/concepts/`.
- [x] BOM in `bom/bom.csv`. Figures are AUD. The required cost column keeps its schema name.
- [x] Tests in `cad/tests/test_tailgate.py`, including the stone-does-not-pass-the-mouth check.

---

## 3. Immediate Next Steps (For Incoming Agent)
1. Wait for Adib's answers in `design/tailgate/CONCEPTS.md` before cutting metal or changing the burner slot.
2. Do not put the oven on the lowered tailgate. The plan is 675 mm and the tailgate is 517 mm deep, and a flame there has no clearance to the ute.
3. Do not add injector geometry. Do not glue a wood shell over this oven.
4. The Gozney study on `research/argon-anatomy` is still the reference for the insulation network. It is not the oven being built.

---

## 4. Guiding Invariants
- **No Premature Assumptions:** Fuel is gas. Wood fire is out unless Adib reopens it. Dimensions live in `cad/tailgate/spec.py`.
- **Material Safety Invariant:** No galvanised zinc in the hot path. This oven has no wood in the thermal stack. Handles and feet are jarrah, off the shell.
- **OSHWA Compliance:** Hardware CERN-OHL-P v2. These notes CC-BY-4.0.
- **Commit Format:** Conventional commit with agent signature, e.g. `feat(cad): initial floor layout [agent:cursor]`.

---

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `cad/tailgate/`, `design/tailgate/`, `bom/bom.csv`.
- **Mass to believe:** 31.5 kg stone-out, 37.6 kg ready, from the model. Argon's hand total of 27.7 kg was the Ø625 crown-only thickening.
