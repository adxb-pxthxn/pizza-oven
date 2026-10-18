# Pizza Oven Project Kanban Task Board

Multi-agent state tracking for Antigravity, Cursor, Claude Code, and Codex.

---

## IN_PROGRESS

---

## READY
- [ ] **[TASK-002]** `CAD`: Parametric outer shroud sheet metal unfolding and DXF export *(Priority: HIGH, Assigned: unassigned)*
  - Create flat patterns with K=0.42 bend deductions for outer 1.2mm powder-coated steel shroud.
- [ ] **[TASK-003]** `THERMO`: Outer touch temperature mitigation (<60°C standoff audit) *(Priority: HIGH, Assigned: unassigned)*
  - Incorporate 5mm ceramic washer standoff locations to decouple inner hot shell from outer casing.

---

## UNDER_REVIEW

---

## DONE
- [x] **[TASK-004]** `SOURCING`: Material sourcing, classifieds scraping (Gumtree/Facebook/Google), and automated price watcher *(Priority: HIGH, Assigned: antigrav)* <!-- note: Built material-sourcing skill, scraper adapters, safety filters, CLI, automation watcher, and test suite -->
- [x] **[TASK-001]** `COORDINATION`: Multi-agent orchestration, Cursor sync, and automated review pipeline *(Priority: HIGH, Assigned: antigrav)* <!-- note: Completed coordination, cursor-sync, and review scripts -->

- [x] **[TASK-000]** `SETUP`: Repository initialization, CERN-OHL-P v2 & CC-BY licenses, and baseline CAD/BOM *(Priority: HIGH, Assigned: antigrav)*
  - Core pizza oven specifications, initial tab-and-slot inner dome CAD, and thermodynamic model established.

---

## BACKLOG
- [ ] **[TASK-005]** `DOCS`: Multi-language laser cutting fabrication checklist *(Priority: LOW, Assigned: unassigned)*
  - Produce maker-ready PDF/markdown checklist for ordering from SendCutSend / Fractory.
- [ ] **[TASK-006]** `CAD`: Integrated digital pyrometer probe mount *(Priority: LOW, Assigned: unassigned)*
  - Design thermocouple bracket positioned 10mm above refractory stone floor.
- [ ] **[TASK-007]** `THERMO`: Transient heat-up time simulation for 0 to 500°C *(Priority: MEDIUM, Assigned: unassigned)*
  - Calculate warm-up duration as a function of burner BTU rating (30,000 BTU/hr propane burner).