---
name: cross-agent-coordination
description: Multi-agent and cross-agent collaboration framework between Antigravity, Cursor, Claude Code, and Codex. Defines the Handover Protocol (docs/HANDOVER.md and .agents/state/TASK_BOARD.md), Atomic Git Commits with agent signatures, and File Locking / collision avoidance (.agents/locks/).
license: CERN-OHL-P v2 / MIT
compatibility: Python 3.10+, Git, POSIX shells
metadata:
  opencode/slash: "true"
---

# Cross-Agent & Multi-Agent Coordination Skill

This skill defines the operational protocols, shared state mechanisms, commit conventions, and file-locking disciplines that allow heterogeneous AI agent systems—including **Antigravity**, **Cursor Composer / Agent**, **Claude Code CLI**, and **Codex / Copilot**—to collaborate seamlessly on this physical engineering repository without overwriting work, introducing CAD regressions, or desynchronizing project state.

---

## 1. Agent Archetypes & Division of Responsibility

In this repository, each AI tool is matched to its architectural strengths:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AI AGENT COLLABORATIVE TOPOLOGY                      │
└────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  ANTIGRAVITY         │ │  CURSOR COMPOSER     │ │  CLAUDE CODE CLI     │
│  - Architecture      │ │  - Rapid local edits │ │  - Long-running CLI  │
│  - Parametric CAD    │ │  - Inline file diffs │ │  - Refactoring loops │
│  - Deep validation   │ │  - Interactive code  │ │  - Test execution    │
│  - Critic / Reviewer │ │  - Fast iteration    │ │  - Batch operations  │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    ▼
                ┌───────────────────────────────────────┐
                │        SHARED REPOSITORY STATE        │
                │  - docs/HANDOVER.md                   │
                │  - .agents/state/TASK_BOARD.md        │
                │  - .agents/locks/*.lock               │
                │  - Git commits with [agent:<id>] tags │
                └───────────────────────────────────────┘
```

| Agent Archetype | Primary Role | Best Tasks | Operating Rules |
|---|---|---|---|
| **Antigravity** | Chief Architect & Critic | Parametric CAD modeling, thermodynamic verification, system-level architecture, formal code reviews | Always runs validation scripts before handoff; executes `multi-agent-review` protocol. |
| **Cursor (Composer / Agent)** | Rapid Prototyper / Maker | Focused file edits, sheet-metal parameter adjustments, script polishing, documentation markdown | Works within scoped file contexts; checks `docs/HANDOVER.md` upon entering; updates task state on commit. |
| **Claude Code** | Terminal Operator & Auditor | Large batch transformations, repetitive file refactoring, test harness execution | Runs from shell; commits with atomic agent trailers. |
| **Codex / Copilot** | Inline Autocompleter | Line-level snippet completion, docstring filling | Subservient to active prompt; bound by `.cursorrules` and MDC files. |

---

## 2. The Handover Protocol

When one agent finishes a session or yields context to another agent, it **must** perform a structured handover to grant the incoming agent immediate 10-second situational awareness.

### 2.1 Handover File: `docs/HANDOVER.md`
The file `docs/HANDOVER.md` acts as the repository's persistent relay baton. Every agent finishing a task or session must update it using `agent_handover.py` or by directly following this template:

```markdown
# Agent Handover Protocol & Session Status

**Active Agent:** [antigrav | cursor | claude-code | codex | human]
**Timestamp:** YYYY-MM-DDTHH:MM:SSZ
**Current Branch / Commit:** main @ <short-sha>
**Overall Status:** [READY_FOR_NEXT_AGENT | BLOCKED | UNDER_REVIEW | IN_PROGRESS]

---

## 1. Executive Summary (10-Second Briefing)
[Concise 2-3 sentence overview of what was accomplished and the current state of the repo.]

## 2. Completed in This Session
- [x] Feature/Fix item 1
- [x] Feature/Fix item 2

## 3. Immediate Next Steps (For Incoming Agent)
1. Step 1 (e.g., Run `python3 cad/model_generator.py`)
2. Step 2 (e.g., Verify outer shroud clearance in `cad/assemblies/`)

## 4. Invariants & Physical Gotchas
- **Thermal:** Chamber must sustain 500°C; outer shell must remain <= 60°C touch temperature.
- **DFM:** Tab & slot tolerance is strictly 0.25 mm. Sheet thickness 1.5 mm (inner) / 1.2 mm (outer).
- **Mouth Ratio:** Neapolitan mouth height ratio must be maintained at 63% ± 1% of dome apex.
- **OSHWA:** Every new mechanical component requires a row in `bom/bom.csv`.

## 5. Active Locks & Touched Files
- None (or list active locks in `.agents/locks/`)
```

### 2.2 Task Board: `.agents/state/TASK_BOARD.md`
The Kanban board records project-level deliverables across five standard columns:
1. `BACKLOG`: Unprioritized future work items.
2. `READY`: Prioritized, scoped items ready to be picked up.
3. `IN_PROGRESS`: Actively owned by an agent with an active lock.
4. `UNDER_REVIEW`: Maker agent completed changes; awaiting Critic review.
5. `DONE`: Validated, audited, and committed to trunk.

---

## 3. Atomic Git Commits & Agent Signatures

To maintain clear auditability and bisectability across autonomous agents, all git commits must follow conventional commits extended with an agent signature bracket.

### 3.1 Commit Format Specification
```text
<type>(<scope>): <subject> [agent:<agent-name>]

[optional body: explanation of rationale, physical equations, DFM choices]

[optional footer: References: #issue, Validations: pass]
```

### 3.2 Recognized Agent Identifiers
- `[agent:antigrav]` - Antigravity (Google DeepMind)
- `[agent:cursor]` - Cursor Composer / Agent
- `[agent:claude-code]` - Anthropic Claude Code CLI
- `[agent:codex]` - OpenAI Codex / GitHub Copilot
- `[agent:human]` - Human engineer manual commit
- `[agent:multi]` - Co-authored or reviewed commit

### 3.3 Commit Message Examples
```bash
# Correct examples:
feat(cad): generate parametric outer shroud panels [agent:antigrav]
fix(bom): update M5 PEM nut part numbers to McMaster [agent:cursor]
test(thermo): add transient heat loss simulation [agent:claude-code]
docs(handover): update next steps for stone support brackets [agent:cursor]
refactor(mesh): optimize SVG export resolution for laser DFM [agent:antigrav]
```

### 3.4 Pre-Commit Agent Verification Rule
Before executing any commit:
1. Run repository audits:
   ```bash
   python3 .agents/skills/code-cad/scripts/cad_validate.py
   python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py
   python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py
   ```
2. Check for active collision locks:
   ```bash
   python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --status
   ```
3. Update `docs/HANDOVER.md` and `.agents/state/TASK_BOARD.md`.

---

## 4. File Locking & Collision Avoidance

When multiple agents run in parallel (for instance, Antigravity running an architectural audit in the background while Cursor Composer edits a CAD script in the foreground), concurrent file edits can lead to corrupted models or lost work.

### 4.1 Locking Mechanics
- Locks live in `.agents/locks/<safe-filename>.lock`.
- Each lock file contains a JSON payload:
  ```json
  {
    "file": "cad/model_generator.py",
    "locked_by": "cursor",
    "pid": 58210,
    "created_at": "2026-10-18T20:00:00Z",
    "expires_at": "2026-10-18T20:15:00Z",
    "reason": "Refactoring dome slot geometry"
  }
  ```
- **TTL Expiration:** All locks automatically expire after 15 minutes to prevent abandoned locks from permanently blocking development.
- **Acquire Lock:**
  ```bash
  python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --lock cad/model_generator.py --agent cursor --reason "Refactoring slots"
  ```
- **Release Lock:**
  ```bash
  python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --unlock cad/model_generator.py --agent cursor
  ```

---

## 5. Tooling & Automation

Use `.agents/skills/cross-agent-coordination/scripts/agent_handover.py`:
- `--summary`: Output a 10-second situational awareness card.
- `--status`: Display task board and active locks.
- `--new-task`: Add a ticket to the Kanban board.
- `--update`: Update task ticket status and handover notes.
- `--export-cursor`: Print a compact prompt context snippet ready for Cursor Composer.
- `--lock / --unlock`: Manage advisory file locks.
