---
name: cursor-sync
description: Cross-platform synchronization between Antigravity, Cursor, and Claude Code environments. Generates and synchronizes scoped Cursor MDC rules (.cursor/rules/*.mdc), legacy .cursorrules, skill symlinks (.cursor/skills/), and CLAUDE.md pointers.
license: CERN-OHL-P v2 / MIT
compatibility: Python 3.10+, Cursor 0.40+, POSIX filesystems
metadata:
  opencode/slash: "true"
---

# Cursor & Multi-Agent IDE Synchronization Skill

This skill governs the integration between Google Antigravity, Cursor IDE (Composer & Chat), and Claude Code. It establishes a unified source of truth for repository engineering instructions, prevents context fragmentation, and automatically projects agent skills into Cursor's native rule system (`.cursor/rules/*.mdc`) and skill directory (`.cursor/skills/`).

---

## 1. Unified Agent Knowledge Architecture

Different AI environments consume project context through distinct discovery paths. Rather than maintaining redundant configuration files that drift out of sync, this repository uses `.agents/` as the canonical store and synchronizes downstream formats:

```
                      Canonical Source of Truth
                      ┌───────────────────────┐
                      │    AGENTS.md          │
                      │  .agents/skills/      │
                      └───────────┬───────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   ANTIGRAVITY    │    │      CURSOR      │    │   CLAUDE CODE    │
│  Native Skill    │    │  .cursorrules    │    │  CLAUDE.md       │
│  Loader          │    │  .cursor/rules/  │    │  (symlink to     │
│  (.agents/       │    │  .cursor/skills/ │    │   AGENTS.md)     │
│   skills/*)      │    │  (symlink mirror)│    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 2. Cursor Configuration: `.cursorrules` vs `.cursor/rules/*.mdc`

Cursor supports two distinct rule mechanisms:

### 2.1 Legacy `.cursorrules` (Root File)
- **Scope:** Injected unconditionally into every Cursor Composer and Chat interaction.
- **Best Practice:** Keep it compact, high-density, and focused on universal project invariants (open hardware licensing, 500°C thermal constraints, tab-and-slot tolerances, agent commit conventions). Do not pack entire skill manuals into this file; delegate specialized topics to MDC files.

### 2.2 Modern Scoped Rules: `.cursor/rules/*.mdc` (Cursor 0.40+)
Modern Cursor rules use Markdown with frontmatter (`.mdc`), providing fine-grained file-glob matching. This prevents wasting LLM context window tokens on irrelevant instructions.

#### Frontmatter Specification:
```markdown
---
description: Brief sentence describing when this rule activates
globs: "glob/pattern/**/*,another/pattern/*.py"
alwaysApply: false
---

# Rule Content...
```

#### Rule Hierarchy in This Repository:

| Rule File | Scoped Globs | `alwaysApply` | Focus Area |
|---|---|---|---|
| `00-universal.mdc` | `*` | `true` | Physical engineering rules, commit signatures, handover discipline, safe-touch specs |
| `cad.mdc` | `cad/**/*`, `*.py`, `*.scad`, `*.step`, `*.dxf` | `false` | Code-CAD DFM, sheet metal K-factors, 0.25mm tab/slot fit clearance, thermal slots |
| `thermo.mdc` | `*thermo*`, `docs/thermal*`, `cad/parts/insulation*` | `false` | 500°C chamber, 63% Neapolitan mouth ratio, refractory stone, Kaowool insulation sizing |
| `oshwa.mdc` | `bom/**/*`, `OSHWA.md`, `LICENSE*`, `README.md` | `false` | CERN-OHL-P v2, CC-BY-4.0, BOM 7-column schema, open-source hardware reproducibility |

---

## 3. Skill Bridging: `.agents/skills/` ↔ `.cursor/skills/` & `.claude/`

To allow Cursor Agent and Claude Code to access the rich engineering skills created for Antigravity (such as `code-cad`, `oven-thermodynamics`, `mechanical-engineering`, and `oshwa-hardware`), the sync script builds transparent filesystem links:

1. **Cursor Skills:** Symlinks `.cursor/skills/` directly to `.agents/skills/`. Cursor agents can directly load and reference specialized skill folders.
2. **Claude Code Bridge:** Creates a root symlink `CLAUDE.md -> AGENTS.md`. Claude Code automatically loads `CLAUDE.md` on startup, gaining immediate awareness of the repository rules and available skills.

---

## 4. Synchronization Automation

The synchronization tool `.agents/skills/cursor-sync/scripts/sync_cursor.py` automates this pipeline.

### Command-Line Usage:

```bash
# Perform full synchronization (MDC rules, .cursorrules, symlinks, CLAUDE.md)
python3 .agents/skills/cursor-sync/scripts/sync_cursor.py

# Check current synchronization status without writing (dry-run)
python3 .agents/skills/cursor-sync/scripts/sync_cursor.py --check

# Force rewrite and overwrite existing rules
python3 .agents/skills/cursor-sync/scripts/sync_cursor.py --force
```

### Generated File Manifest:
- `.cursorrules`
- `.cursor/rules/00-universal.mdc`
- `.cursor/rules/cad.mdc`
- `.cursor/rules/thermo.mdc`
- `.cursor/rules/oshwa.mdc`
- `.cursor/skills/` (Symlink or mirrored directory)
- `CLAUDE.md` (Symlink to `AGENTS.md`)

---

## 5. Working in Cursor: Practical Guide

When developing in Cursor:
1. **Starting a Task:**
   - In Cursor Chat or Composer, type: `@docs/HANDOVER.md` to load the latest handover context.
   - Run in the Cursor terminal: `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --summary`.
2. **Locking Files:**
   - Before large refactors, lock target files:
     `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --lock cad/model_generator.py --agent cursor`
3. **Committing Changes:**
   - Run audit commands before saving:
     `python3 .agents/skills/code-cad/scripts/cad_validate.py`
   - Use the agent commit signature:
     `git commit -m "feat(cad): refine chimney flue mounting tabs [agent:cursor]"`
4. **Handoff:**
   - Release locks and update handover notes:
     `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --unlock cad/model_generator.py --agent cursor`
   - Update `docs/HANDOVER.md`.
