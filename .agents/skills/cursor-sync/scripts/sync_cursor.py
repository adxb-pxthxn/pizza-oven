#!/usr/bin/env python3
"""
Cursor & Multi-Agent IDE Synchronization Script
Part of the Open-Source Neapolitan Pizza Oven Project (.agents/skills/cursor-sync)

Creates and synchronizes:
1. .cursor/rules/*.mdc (00-universal.mdc, cad.mdc, thermo.mdc, oshwa.mdc)
2. .cursorrules root configuration
3. Symlink/mirror for .cursor/skills/ -> .agents/skills/
4. Symlink for CLAUDE.md -> AGENTS.md
"""

import os
import sys
import argparse
from pathlib import Path


def find_repo_root() -> Path:
    """Find repository root directory."""
    current = Path(__file__).resolve().parent
    for p in [current] + list(current.parents):
        if (p / ".git").is_dir() or (p / ".agents").is_dir():
            return p
    return Path.cwd()


REPO_ROOT = find_repo_root()
CURSOR_DIR = REPO_ROOT / ".cursor"
RULES_DIR = CURSOR_DIR / "rules"
CURSOR_SKILLS_DIR = CURSOR_DIR / "skills"
AGENTS_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
CURSORRULES_FILE = REPO_ROOT / ".cursorrules"
AGENTS_MD_FILE = REPO_ROOT / "AGENTS.md"
CLAUDE_MD_FILE = REPO_ROOT / "CLAUDE.md"


UNIVERSAL_MDC = """---
description: Universal engineering standards, commit conventions, and multi-agent coordination
globs: "*"
alwaysApply: true
---

# Pizza Oven Project: Universal Engineering & Agent Rules

This is an open-source physical engineering development workspace for a pizza oven.

## Core Engineering Principles
1. **No Premature Assumptions:** Do NOT assume dimensions, fuel sources, materials, or manufacturing methods until explicitly specified by the user.
2. **Food Safety & Materials:** When materials are selected, enforce food-grade safety standards (FDA / EU 1935/2004) and avoid toxic coatings or galvanized zinc in heated zones.
3. **Open Hardware:** Adhere to OSHWA principles (CERN-OHL-P v2 hardware license, CC-BY-4.0 docs license).

## Multi-Agent Commit & Handover Protocol
1. Commits MUST use conventional commits with agent signature:
   `<type>(<scope>): <subject> [agent:cursor]` (or `[agent:antigrav]`, `[agent:claude-code]`).
2. Always check `docs/HANDOVER.md` and `.agents/state/TASK_BOARD.md` before starting and after finishing work.
3. Run situational briefing:
   `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --summary`
"""

CAD_MDC = """---
description: Code-CAD modeling, DFM, laser cutting tolerances, and thermal expansion relief
globs: "cad/**/*,*.py,*.scad,*.step,*.dxf,*.svg"
alwaysApply: false
---

# Code-CAD & Design for Manufacturing (DFM)

Guidelines for parametric mechanical design, fabrication, and code-driven CAD.

## Parametric toolchain
- Master dimensions are millimetre fields in `cad/parameters.py`. The checked-in model is a placeholder, not a product specification.
- Export with `python3 -m cad.build` (STEP AP214 + STL) into gitignored `cad/output/`.
- Test with `python3 -m unittest cad.tests.test_placeholder_assembly`.
- Conventions: `.agents/skills/cad/SKILL.md`.

## General Fabrication & DFM Rules
- **Laser / Waterjet:** Maintain hole diameter >= 1.0 * thickness and web distance >= 2.0 * thickness.
- **Press Brake Air Bending:** Select standard V-die openings (typically 6-8 * t) and appropriate bend deductions / K-factors.
- **Thermal Expansion Relief:** High-temperature metal components subject to differential thermal expansion must include slotted clearances or sliding joints.
- **Assembly Joinery:** If using tab-and-slot construction, apply 0.20-0.30mm clearance for clean fit without binding.
"""

THERMO_MDC = """---
description: Thermodynamics, heat transfer, insulation sizing, and airflow modeling
globs: "*thermo*,docs/thermal*"
alwaysApply: false
---

# High-Temperature Thermodynamics & Heat Transfer

Principles for oven heat transfer, insulation sizing, and combustion aerodynamics.

## General Thermal Engineering Principles
1. **Heat Transfer Modes:** Balance floor conduction (thermal mass), dome radiant flux (Stefan-Boltzmann), and hot gas convection.
2. **Insulation:** Size multi-layer insulation walls to prevent excessive thermal losses and maintain safe exterior touch temperatures.
3. **Thermal Shock:** Select refractory materials with appropriate thermal shock resistance and thermal effusivity.

## Verification
Run thermodynamic solver:
`python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py --help`
"""

OSHWA_MDC = """---
description: OSHWA open-source hardware compliance, dual-licensing, and Bill of Materials schema
globs: "bom/**/*,OSHWA.md,LICENSE*,README.md"
alwaysApply: false
---

# OSHWA Open-Source Hardware Compliance & Licensing

Rules for maintaining open-source hardware certification standards.

## Dual Licensing
- **Hardware & CAD Designs:** CERN-OHL-P v2 (Permissive Open Hardware License) in `LICENSE-HARDWARE`.
- **Documentation & Media:** Creative Commons Attribution 4.0 International (CC-BY-4.0) in `LICENSE-DOCS`.

## Bill of Materials (BOM) Requirements
Every physical part, fastener, and raw material must be cataloged in `bom/bom.csv`.
Strict schema:
`Part Number,Component Name,Material / Spec,Qty,Category,Vendor / Reference,Estimated Unit Cost (USD),Sourcing Notes`

## Verification
Run OSHWA compliance audit:
`python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py`
"""

CURSORRULES_CONTENT = """# Pizza Oven Physical Engineering — Root Cursor Instructions
# Generated by .agents/skills/cursor-sync/scripts/sync_cursor.py

## 1. Project Invariants
- Open Hardware certified: Dual CERN-OHL-P v2 (hardware) + CC-BY-4.0 (documentation).
- No premature design assumptions: await explicit user guidance on fuel, form, and dimensions.
- All components tracked in `bom/bom.csv` once designed.

## 2. Multi-Agent & Git Commit Discipline
- Commits must follow: `<type>(<scope>): <subject> [agent:cursor]`
- Situational briefing CLI:
  * `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --summary`
- Task state tracked in `.agents/state/TASK_BOARD.md` and `docs/HANDOVER.md`.
- Scoped MDC rules live in `.cursor/rules/` (00-universal, cad, thermo, oshwa).
- Specialized engineering skills accessible in `.cursor/skills/` -> `.agents/skills/`.
"""


def ensure_symlink(source: Path, target: Path, check_only: bool = False) -> bool:
    """Ensure target symlinks to source. If not or if target is directory/file, handle cleanly."""
    if target.is_symlink():
        try:
            curr_dest = target.resolve()
            src_dest = source.resolve()
            if curr_dest == src_dest:
                return True
        except Exception:
            pass

    if check_only:
        return False

    # If target exists and is an empty directory or wrong symlink, remove it
    if target.is_symlink():
        target.unlink()
    elif target.is_dir():
        # Check if empty
        if not any(target.iterdir()):
            target.rmdir()
        else:
            # Non-empty directory: backup or do not clobber
            backup = target.with_name(target.name + ".bak")
            print(f"[INFO] Backing up existing directory {target} -> {backup}")
            target.rename(backup)
    elif target.is_file():
        target.unlink()

    # Create relative symlink
    try:
        rel_src = os.path.relpath(source, target.parent)
        os.symlink(rel_src, target)
        print(f"[OK] Created symlink: {target} -> {rel_src}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed creating symlink {target} -> {source}: {e}")
        return False


def sync_all(check_only: bool = False, force: bool = False):
    """Perform the full synchronization."""
    status = {"created": 0, "verified": 0, "errors": 0}

    print("=" * 70)
    print("  CURSOR & MULTI-AGENT SYNC ENGINE")
    print(f"  Target: {REPO_ROOT}")
    print(f"  Mode:   {'CHECK ONLY (Dry Run)' if check_only else 'SYNC & GENERATE'}")
    print("=" * 70)

    # 1. Ensure .cursor/rules directory
    if not check_only:
        RULES_DIR.mkdir(parents=True, exist_ok=True)

    mdc_files = {
        RULES_DIR / "00-universal.mdc": UNIVERSAL_MDC,
        RULES_DIR / "cad.mdc": CAD_MDC,
        RULES_DIR / "thermo.mdc": THERMO_MDC,
        RULES_DIR / "oshwa.mdc": OSHWA_MDC,
    }

    # 2. Write / verify .cursor/rules/*.mdc
    for mdc_path, content in mdc_files.items():
        if mdc_path.exists() and not force:
            existing = mdc_path.read_text(encoding="utf-8")
            if existing.strip() == content.strip():
                print(f"[PASS] Rule verified: {mdc_path.relative_to(REPO_ROOT)}")
                status["verified"] += 1
                continue

        if check_only:
            print(f"[FAIL] Rule needs update: {mdc_path.relative_to(REPO_ROOT)}")
            status["errors"] += 1
        else:
            mdc_path.write_text(content.strip() + "\n", encoding="utf-8")
            print(f"[OK] Generated rule: {mdc_path.relative_to(REPO_ROOT)}")
            status["created"] += 1

    # 3. Write / verify .cursorrules
    if CURSORRULES_FILE.exists() and not force:
        existing = CURSORRULES_FILE.read_text(encoding="utf-8")
        if existing.strip() == CURSORRULES_CONTENT.strip():
            print(f"[PASS] File verified: .cursorrules")
            status["verified"] += 1
        elif check_only:
            print(f"[FAIL] .cursorrules needs update")
            status["errors"] += 1
        else:
            CURSORRULES_FILE.write_text(CURSORRULES_CONTENT.strip() + "\n", encoding="utf-8")
            print(f"[OK] Updated: .cursorrules")
            status["created"] += 1
    else:
        if check_only:
            print(f"[FAIL] .cursorrules does not exist")
            status["errors"] += 1
        else:
            CURSORRULES_FILE.write_text(CURSORRULES_CONTENT.strip() + "\n", encoding="utf-8")
            print(f"[OK] Created: .cursorrules")
            status["created"] += 1

    # 4. Link .cursor/skills -> .agents/skills
    if AGENTS_SKILLS_DIR.exists():
        if check_only:
            if CURSOR_SKILLS_DIR.is_symlink() and CURSOR_SKILLS_DIR.resolve() == AGENTS_SKILLS_DIR.resolve():
                print(f"[PASS] Symlink verified: .cursor/skills -> .agents/skills")
                status["verified"] += 1
            else:
                print(f"[FAIL] Symlink missing or invalid: .cursor/skills")
                status["errors"] += 1
        else:
            ok = ensure_symlink(AGENTS_SKILLS_DIR, CURSOR_SKILLS_DIR)
            if ok:
                status["created"] += 1
            else:
                status["errors"] += 1
    else:
        print(f"[WARNING] .agents/skills directory not found at {AGENTS_SKILLS_DIR}")

    # 5. Link CLAUDE.md -> AGENTS.md
    if AGENTS_MD_FILE.exists():
        if check_only:
            if CLAUDE_MD_FILE.is_symlink() and CLAUDE_MD_FILE.resolve() == AGENTS_MD_FILE.resolve():
                print(f"[PASS] Symlink verified: CLAUDE.md -> AGENTS.md")
                status["verified"] += 1
            else:
                print(f"[FAIL] Symlink missing or invalid: CLAUDE.md")
                status["errors"] += 1
        else:
            ok = ensure_symlink(AGENTS_MD_FILE, CLAUDE_MD_FILE)
            if ok:
                status["created"] += 1
            else:
                status["errors"] += 1
    else:
        print(f"[WARNING] AGENTS.md file not found at {AGENTS_MD_FILE}")

    print("-" * 70)
    print(f"Sync Results: Verified: {status['verified']} | Updated/Created: {status['created']} | Issues: {status['errors']}")
    print("=" * 70)

    if check_only and status["errors"] > 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Synchronize Cursor MDC rules, .cursorrules, and agent links.")
    parser.add_argument("--check", action="store_true", help="Perform dry run check without modifying files")
    parser.add_argument("--force", action="store_true", help="Force overwrite all rules and configurations")
    args = parser.parse_args()

    sync_all(check_only=args.check, force=args.force)


if __name__ == "__main__":
    main()
