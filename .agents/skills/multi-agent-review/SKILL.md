---
name: multi-agent-review
description: Dual-agent 'Maker / Critic' review protocol and automated validation pipeline. When one agent (e.g. Cursor Composer or Claude Code) drafts changes, a critic agent (e.g. Antigravity) runs this protocol across DFM sanity, thermal safety, OSHWA compliance, unit tests, and multi-agent etiquette.
license: CERN-OHL-P v2 / MIT
compatibility: Python 3.10+, Git, POSIX shells
metadata:
  opencode/slash: "true"
---

# Multi-Agent Review & Verification Skill

This skill defines the formal **Maker / Critic** dual-agent review protocol for this physical engineering codebase. Autonomous AI agents can write syntactically correct code that nonetheless violates physical manufacturing tolerances, dangerous thermal thresholds, or open-hardware licensing mandates. This protocol guarantees that every change is independently audited before merging or handover.

---

## 1. The Maker / Critic Paradigm

```
┌────────────────────────────────┐       Git Diff / Staged Edits
│   MAKER AGENT                  │ ─────────────────────────────────┐
│   (e.g., Cursor Composer,      │                                  │
│    Claude Code, or Antigrav)   │                                  ▼
└────────────────────────────────┘                       ┌──────────────────────┐
                ▲                                        │   CRITIC AGENT       │
                │        CHANGES_REQUESTED               │   (e.g., Antigrav)   │
                └─────────────────────────────────────── │                      │
                                                         │ - Runs Audit Suite   │
                                                         │ - Inspects Physics   │
                                                         │ - Evaluates DFM      │
                                                         │ - Verifies OSHWA     │
                                                         └──────────┬───────────┘
                                                                    │
                                                          APPROVED  ▼
                                                         ┌──────────────────────┐
                                                         │ Commit to Trunk      │
                                                         │ [agent:maker]        │
                                                         │ Reviewed: [critic]   │
                                                         └──────────────────────┘
```

| Role | Typical Agent | Core Responsibilities |
|---|---|---|
| **Maker** | Cursor Composer, Claude Code, Human | Implements features, refactors CAD scripts, updates documentation, proposes dimensional changes. Must request review upon completion. |
| **Critic** | Antigravity (Chief Architect) | Operates independently; runs automated validation harness; rigorously audits git diff against physical invariants; renders a structured Review Card. |

---

## 2. Review Checklist: The 5 Pillars

Every multi-agent review evaluates the codebase across five non-negotiable pillars:

### Pillar 1: Design For Manufacturing (DFM) Sanity
- [ ] **Sheet Thickness:** Inner hot dome $\ge 1.5$ mm (AISI 304); outer casing $\ge 1.2$ mm.
- [ ] **Laser Pierce Rule:** Minimum hole diameter $\ge 1.0 \times t$ (sheet thickness) to prevent laser optic damage and burred edges.
- [ ] **Web / Bridge Clearance:** Distance between adjacent cutouts or holes $\ge 2.0 \times t$.
- [ ] **Tab-and-Slot Tolerance:** Fit clearance must be exactly $0.25$ mm per side ($0.50$ mm total clearance) for clean self-aligning tab-and-slot joinery.
- [ ] **Flange Length & Relief:** Minimum bend flange $\ge 4.0 \times t$; bend reliefs present at notch corners.

### Pillar 2: High-Temperature Thermal Safety & Physics
- [ ] **Internal Operating Temperature:** Structural integrity maintained at $500^\circ$C continuous operation.
- [ ] **Exterior Safe Touch:** Outer shell and touch points must remain $\le 60^\circ$C steady state (EN 60335-2-6 / ASTM C1055 standard).
- [ ] **Thermal Expansion Travel:** Inner sheet thermal expansion ($\Delta L \approx 3.9$ mm at $500^\circ$C) must have slotted relief holes with $\ge 6.5$ mm total travel.
- [ ] **Neapolitan 63% Mouth Ratio:** Mouth opening height must remain within $63\% \pm 1\%$ of interior dome apex height ($H_m / H_{apex} \approx 0.63$).
- [ ] **Refractory Mass:** Cordierite or Biscotto stone thickness $\ge 15$ mm.

### Pillar 3: OSHWA Open Hardware Compliance
- [ ] **Dual Licensing:** CERN-OHL-P v2 for hardware (`LICENSE-HARDWARE`) and CC-BY-4.0 for docs (`LICENSE-DOCS`).
- [ ] **BOM Integrity:** Every new physical item is logged in `bom/bom.csv` with standard 7-column schema.
- [ ] **Source CAD Formats:** Editable parametric code or native CAD source files accompany any export (STEP/DXF/STL).

### Pillar 4: Software & Automated Validation Suite
- [ ] **Execution Purity:** All Python audit tools run with standard library Python 3.10+ without unhandled exceptions.
- [ ] **Passing Audits:**
  * `python3 .agents/skills/code-cad/scripts/cad_validate.py` passes with 0 failures.
  * `python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py` passes with 0 failures.
  * `python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py` executes and thermal margins are analyzed.

### Pillar 5: Multi-Agent Etiquette & Hygiene
- [ ] **Commit Conventional Signature:** Commit messages follow `<type>(<scope>): <subject> [agent:<id>]`.
- [ ] **Locking Discipline:** All locks in `.agents/locks/` have been released.
- [ ] **Handover State:** `docs/HANDOVER.md` and `.agents/state/TASK_BOARD.md` updated with accurate current state.

---

## 3. Automated Review CLI: `agent_review.py`

The critic agent runs the unified audit harness:

```bash
# Run comprehensive audit and output Markdown Review Card
python3 .agents/skills/multi-agent-review/scripts/agent_review.py

# Specify Maker agent identity
python3 .agents/skills/multi-agent-review/scripts/agent_review.py --maker cursor

# Strict mode: treat warnings as failures
python3 .agents/skills/multi-agent-review/scripts/agent_review.py --strict

# Export review card to file
python3 .agents/skills/multi-agent-review/scripts/agent_review.py --output docs/REVIEWS/latest-review.md
```

---

## 4. Review Card Format Specification

The tool outputs a standardized review verdict:

```markdown
# Multi-Agent Maker/Critic Review Card

**Reviewer (Critic):** `antigrav`
**Maker Agent:** `cursor`
**Date / Time:** 2026-10-18T20:15:00Z
**Git Target:** `main @ a1b2c3d`
**Final Verdict:** `APPROVED` | `APPROVED_WITH_WARNINGS` | `CHANGES_REQUESTED`

## Subsystem Audit Results
| Subsystem | Validator Script | Status | Key Metrics |
|---|---|---|---|
| Code-CAD DFM | `cad_validate.py` | PASS | 10/10 checks passed, 0.25mm tab/slot |
| OSHWA Standards | `validate_oshwa.py` | PASS | 20 parts, dual licenses CERN/CC-BY |
| Thermodynamics | `thermal_model.py` | WARN | Outer temp 102°C requires standoff check |

## Verification Checklist
- [x] Laser DFM tolerances confirmed
- [x] 63% mouth opening ratio preserved
- [x] CERN-OHL-P v2 & CC-BY-4.0 maintained
- [x] No active file locks left in .agents/locks/
- [x] Commit signature format verified

## Verdict & Actionable Remediation
[Detailed instructions for Maker agent or approval sign-off]
```
