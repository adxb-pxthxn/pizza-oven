# Agent Handover Protocol & Session Status

**Active Agent:** antigrav
**Current Branch / Commit:** main
**Overall Status:** READY_FOR_USER_INPUT

---

## 1. Executive Summary (10-Second Briefing)
The repository has been thoroughly cleansed of all premature design assumptions and hardcoded specifications. The foundational open-source engineering stack is fully prepared:
- Upstream Anatomy visual explanation skill
- Mechanical engineering DFM, bend allowance, and thermal expansion calculators
- Parametric code-CAD workflows and interchange pipelines
- High-temperature thermodynamics modeling
- OSHWA compliance auditor and CERN-OHL / CC-BY licensing
- Multi-agent coordination (Antigravity, Cursor, Claude Code) and synchronization
- Material sourcing & classifieds scraping pipeline

The repository is a clean slate awaiting the user's initial design criteria and requirements.

---

## 2. Completed in This Session
- [x] Cleansed all hardcoded CAD models, exports, and generator scripts from `cad/`.
- [x] Cleansed `bom/bom.csv` into a clean, un-opinionated OSHWA-compliant template.
- [x] Removed assumed engineering specification, assembly guide, and thermal calculation docs.
- [x] Cleansed `AGENTS.md`, `GEMINI.md`, `README.md`, and `OSHWA.md` of any assumed dimensions, fuel types, or materials.
- [x] Kept all general engineering calculation tools, DFM helpers, multi-agent frameworks, and scraping tools intact.

---

## 3. Immediate Next Steps (For Incoming Agent)
1. **Wait for User Direction:** Do NOT implement CAD models, select materials, or fix dimensions until the user explicitly defines the project requirements (e.g. fuel type, capacity, portability, target temperature, budget, or preferred manufacturing method).
2. **Consult Available Skills:** Use `.agents/skills/` once design criteria are given.

---

## 4. Guiding Invariants
- **No Premature Assumptions:** Never assume specific dimensions, fuel source, sheet metal thickness, stone type, or assembly method without user input.
- **Material Safety Invariant:** When materials are chosen, always verify food safety (FDA/EU 1935/2004) and avoid toxic materials (e.g. galvanized zinc in high-temp zones).
- **OSHWA Compliance:** Any future physical parts must be added to `bom/bom.csv` with editable CAD and open interchange exports.
- **Commit Format:** Conventional commit with agent signature, e.g. `feat(cad): initial floor layout [agent:antigrav]`.

---

## 5. Active Locks & Touched Files
- **Active Locks:** None. All resources unlocked in `.agents/locks/`.
