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
description: Universal engineering standards, commit conventions, safety limits, and multi-agent coordination
globs: "*"
alwaysApply: true
---

# Pizza Oven Project: Universal Engineering & Agent Rules

This is an open-source, certified-grade physical engineering project for a high-performance portable Neapolitan pizza oven (500°C chamber, sub-90s bake).

## Core Physical Constraints
1. **Operating Temperatures:** Sustained 450°C–500°C floor & dome.
2. **Exterior Safe Touch:** Outer shell, handles, and control points must remain <= 60°C under steady state (EN 60335-2-6 / ASTM C1055).
3. **Materials:** AISI 304 food-grade stainless steel for inner hot zone; AISI 304/430 or powder-coated steel for outer shroud.
4. **Fasteners:** Metric ISO A2/A4 stainless steel (M4/M5/M6). No carbon steel in thermal zones.

## Multi-Agent Commit & Handover Protocol
1. Commits MUST use conventional commits with agent signature:
   `<type>(<scope>): <subject> [agent:cursor]` (or `[agent:antigrav]`, `[agent:claude-code]`).
2. Before committing, run repository validation scripts:
   - `python3 .agents/skills/code-cad/scripts/cad_validate.py`
   - `python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py`
   - `python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py`
3. Always check `docs/HANDOVER.md` and `.agents/state/TASK_BOARD.md` before starting and after finishing work.
4. Run situational briefing:
   `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --summary`
"""

CAD_MDC = """---
description: Code-CAD modeling, sheet metal DFM, laser cutting tolerances, and thermal expansion relief
globs: "cad/**/*,*.py,*.scad,*.step,*.dxf,*.svg"
alwaysApply: false
---

# Code-CAD & Sheet Metal Design for Manufacturing (DFM)

Guidelines for parametric mechanical design, laser cutting, and press brake bending.

## Sheet Metal & Laser Tolerances
- **Inner Shell:** 1.5 mm AISI 304 stainless steel.
- **Outer Shell:** 1.2 mm cold-rolled steel or AISI 430.
- **K-Factor:** 0.42 for air bending stainless steel on standard V-die (bend allowance formula: BA = pi * (R + K * t) * (A / 180)).
- **Minimum Flange Length:** >= 4 * t (6.0 mm for 1.5 mm sheet).
- **Minimum Hole Diameter:** >= 1.0 * t (laser pierce rule; prefer >= 1.5 * t for fiber laser life).
- **Minimum Web Distance:** Distance between cutouts or edges >= 2.0 * t.

## Tab-and-Slot Joinery & Thermal Relief
- **Fit Clearance:** Tab-and-slot mortise/tenon joints have exactly 0.25 mm clearance per side (tab width W - 0.25 mm, slot width W + 0.25 mm) for clean self-alignment without weld fixtures.
- **Thermal Expansion Slots:** Inner dome sheet experiences thermal expansion (delta L approx 3.9 mm at 500°C).
- Hot-to-cold interface mounting slots must have >= 6.5 mm slotted travel along the expansion axis.

## Verification
Always test CAD output:
`python3 .agents/skills/code-cad/scripts/cad_validate.py`
"""

THERMO_MDC = """---
description: Thermodynamics, refractory stone, heat retention, and insulation cavity engineering
globs: "*thermo*,docs/thermal*,cad/parts/insulation*,cad/parts/stone*"
alwaysApply: false
---

# High-Temperature Thermodynamics & Insulation Sizing

Specifications for heat retention, combustion air, radiant transfer, and insulation.

## Thermal Invariants
1. **Target Temperatures:**
   - Baking Stone (Floor): 430°C–480°C.
   - Hot Gas / Apex Dome: 480°C–520°C.
   - Outer Shroud Safe Touch: <= 60°C.

2. **The 63% Neapolitan Mouth Ratio:**
   - Mouth Opening Height H_m approx 0.63 * H_apex (Dome Apex Interior Height).
   - This ratio optimizes radiant heat reflection back onto the pizza surface while maintaining laminar intake air draft.

3. **Insulation Barrier:**
   - Minimum 25 mm bio-soluble ceramic fiber blanket (128 kg/m³ density, thermal conductivity k approx 0.09 W/m·K at 500°C).
   - Total wall thermal resistance R >= 0.42 m²·K/W.
   - Insulation must be fully encapsulated by sheet metal baffles to ensure zero airborne fiber migration into the cooking chamber.

4. **Baking Stone (Thermal Mass):**
   - High-density cordierite or Biscotto di Sorrento stone >= 15 mm thickness.

## Verification
Run thermodynamic solver:
`python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py`
"""

OSHWA_MDC = """---
description: OSHWA open-source hardware compliance, dual-licensing, and Bill of Materials schema
globs: "bom/**/*,OSHWA.md,LICENSE*,README.md,docs/assembly*"
alwaysApply: false
---

# OSHWA Open-Source Hardware Compliance & Licensing

Rules for maintaining open-source hardware certification standards.

## Dual Licensing
- **Hardware & CAD Designs:** CERN-OHL-P v2 (Permissive Open Hardware License) in `LICENSE-HARDWARE`.
- **Documentation & Media:** Creative Commons Attribution 4.0 International (CC-BY-4.0) in `LICENSE-DOCS`.

## Bill of Materials (BOM) Requirements
Every physical part, fastener, and raw material must be cataloged in `bom/bom.csv`.
Strict 7-column CSV schema:
1. `Item`: Numeric index (e.g. 1, 2, 3...)
2. `Part Number`: Formatted part code (e.g. `PO-001-DOME`, `FAST-M5-12`)
3. `Description`: Component title and engineering role
4. `Qty`: Numeric quantity required per oven
5. `Material`: Specified alloy or material (e.g. `AISI 304 Stainless Steel`, `Cordierite`)
6. `Supplier / Source`: Vendor, standard part reference, or `Laser Cut Service`
7. `Estimated Cost (USD)`: Currency formatted estimated unit cost

## Verification
Run OSHWA compliance audit:
`python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py`
"""

CURSORRULES_CONTENT = """# Pizza Oven Physical Engineering — Root Cursor Instructions
# Generated by .agents/skills/cursor-sync/scripts/sync_cursor.py

## 1. Project Invariants
- High-performance portable Neapolitan pizza oven (500°C chamber, 60s-90s bake time).
- Open Hardware certified: Dual CERN-OHL-P v2 (hardware) + CC-BY-4.0 (documentation).
- All components tracked in `bom/bom.csv` with standard 7-column schema.

## 2. Mechanical DFM & Thermal Rules
- Inner shell: 1.5mm AISI 304 Stainless Steel; Outer shroud: 1.2mm steel.
- K-Factor: 0.42. Minimum flange >= 4*t. Minimum hole >= 1.0*t.
- Tab-and-slot fit clearance: exactly 0.25mm per side.
- Thermal expansion slotted holes: >= 6.5mm travel for 500°C differential.
- Safe touch outer temperature: <= 60°C.
- Neapolitan mouth height ratio: 63% ± 1% of dome apex height.

## 3. Multi-Agent & Git Commit Discipline
- Commits must follow: `<type>(<scope>): <subject> [agent:cursor]`
- Always run pre-commit checks:
  * `python3 .agents/skills/code-cad/scripts/cad_validate.py`
  * `python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py`
  * `python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py`
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
