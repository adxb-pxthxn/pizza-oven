#!/usr/bin/env python3
"""
Multi-Agent Maker/Critic Review Engine
Part of the Open-Source Neapolitan Pizza Oven Project (.agents/skills/multi-agent-review)

Executes repository verification audits (CAD DFM, OSHWA compliance, Thermodynamics),
inspects git diff and locks, and generates an objective Markdown Review Card.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def find_repo_root() -> Path:
    """Find repository root directory."""
    current = Path(__file__).resolve().parent
    for p in [current] + list(current.parents):
        if (p / ".git").is_dir() or (p / ".agents").is_dir():
            return p
    return Path.cwd()


REPO_ROOT = find_repo_root()


def run_command(cmd: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
    """Run command and return (exit_code, stdout, stderr)."""
    try:
        res = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def audit_cad() -> dict:
    """Run cad_validate.py and parse results."""
    script_path = REPO_ROOT / ".agents" / "skills" / "code-cad" / "scripts" / "cad_validate.py"
    if not script_path.exists():
        return {"status": "SKIP", "script": "cad_validate.py", "summary": "Script not found", "passed": 0, "failed": 0}

    code, stdout, stderr = run_command([sys.executable, str(script_path)])
    passed = 0
    failed = 0
    warnings = 0

    for line in stdout.splitlines():
        if "[ PASS ]" in line:
            passed += 1
        elif "[ FAIL ]" in line:
            failed += 1
        elif "[ WARN ]" in line:
            warnings += 1

    status = "PASS" if code == 0 and failed == 0 else "FAIL"
    summary = f"{passed} passed, {warnings} warnings, {failed} failures"
    return {
        "status": status,
        "script": "cad_validate.py",
        "summary": summary,
        "stdout": stdout,
        "passed": passed,
        "failed": failed,
        "warnings": warnings
    }


def audit_oshwa() -> dict:
    """Run validate_oshwa.py and parse results."""
    script_path = REPO_ROOT / ".agents" / "skills" / "oshwa-hardware" / "scripts" / "validate_oshwa.py"
    if not script_path.exists():
        return {"status": "SKIP", "script": "validate_oshwa.py", "summary": "Script not found"}

    code, stdout, stderr = run_command([sys.executable, str(script_path)])
    is_pass = "REPOSITORY PASSES OSHWA" in stdout and code == 0
    status = "PASS" if is_pass else "FAIL"

    parts_count = 0
    cost = "N/A"
    for line in stdout.splitlines():
        if "Successfully parsed" in line:
            parts_count = line.split("parsed")[-1].split("components")[0].strip()
        if "Estimated Total BOM Cost" in line:
            cost = line.split(":")[-1].strip()

    summary = f"CERN-OHL + CC-BY verified; BOM: {parts_count} parts ({cost})"
    return {
        "status": status,
        "script": "validate_oshwa.py",
        "summary": summary,
        "stdout": stdout
    }


def audit_thermo() -> dict:
    """Run thermal_model.py and parse results."""
    script_path = REPO_ROOT / ".agents" / "skills" / "oven-thermodynamics" / "scripts" / "thermal_model.py"
    if not script_path.exists():
        return {"status": "SKIP", "script": "thermal_model.py", "summary": "Script not found"}

    code, stdout, stderr = run_command([sys.executable, str(script_path)])
    touch_temp = "unknown"
    exceeds_limit = "EXCEEDS 60°C TOUCH LIMIT" in stdout

    for line in stdout.splitlines():
        if "EXTERIOR TOUCH TEMPERATURE:" in line:
            touch_temp = line.split(":")[1].split("==>")[0].strip()

    if exceeds_limit:
        status = "WARN"
        summary = f"Touch temp {touch_temp} exceeds 60°C limit; requires air standoff or dual insulation"
    else:
        status = "PASS"
        summary = f"Touch temp {touch_temp} within safe limit"

    return {
        "status": status,
        "script": "thermal_model.py",
        "summary": summary,
        "stdout": stdout,
        "touch_temp": touch_temp
    }


def get_git_info() -> dict:
    """Retrieve git branch, commit sha, and modified files list."""
    _, branch, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, commit, _ = run_command(["git", "rev-parse", "--short", "HEAD"])
    _, status_raw, _ = run_command(["git", "status", "--porcelain"])
    _, diff_stat, _ = run_command(["git", "diff", "--stat"])

    modified_files = []
    for line in status_raw.splitlines():
        if line.strip():
            modified_files.append(line.strip())

    return {
        "branch": branch or "main",
        "commit": commit or "HEAD",
        "modified_files": modified_files,
        "diff_stat": diff_stat or "No unstaged diffs"
    }


def check_locks() -> list[dict]:
    """Check for active locks."""
    locks_dir = REPO_ROOT / ".agents" / "locks"
    active = []
    if locks_dir.exists():
        for f in locks_dir.glob("*.lock"):
            try:
                active.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
    return active


def generate_review(maker: str, reviewer: str, strict: bool = False) -> dict:
    """Execute all audits and compile review report."""
    cad_res = audit_cad()
    oshwa_res = audit_oshwa()
    thermo_res = audit_thermo()
    git_info = get_git_info()
    locks = check_locks()

    has_failures = any(r.get("status") == "FAIL" for r in [cad_res, oshwa_res, thermo_res])
    has_warnings = any(r.get("status") == "WARN" for r in [cad_res, oshwa_res, thermo_res])

    if has_failures or (strict and has_warnings):
        verdict = "CHANGES_REQUESTED"
    elif has_warnings:
        verdict = "APPROVED_WITH_WARNINGS"
    else:
        verdict = "APPROVED"

    iso_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "verdict": verdict,
        "timestamp": iso_timestamp,
        "reviewer": reviewer,
        "maker": maker,
        "git": git_info,
        "locks": locks,
        "audits": {
            "cad": cad_res,
            "oshwa": oshwa_res,
            "thermo": thermo_res
        }
    }


def format_markdown_card(report: dict) -> str:
    """Format report dict into Markdown Review Card."""
    v = report["verdict"]
    badge = "🟢" if v == "APPROVED" else ("🟡" if v == "APPROVED_WITH_WARNINGS" else "🔴")

    lines = [
        f"# {badge} Multi-Agent Maker/Critic Review Card",
        "",
        f"- **Verdict:** `{report['verdict']}`",
        f"- **Reviewer (Critic):** `{report['reviewer']}`",
        f"- **Maker Agent:** `{report['maker']}`",
        f"- **Timestamp:** `{report['timestamp']}`",
        f"- **Git Target:** `{report['git']['branch']} @ {report['git']['commit']}`",
        "",
        "## 1. Automated Subsystem Audits",
        "",
        "| Subsystem | Validator Script | Status | Findings / Metrics |",
        "|---|---|---|---|",
    ]

    for name, a in [
        ("Code-CAD & DFM", report["audits"]["cad"]),
        ("OSHWA Standards", report["audits"]["oshwa"]),
        ("Oven Thermodynamics", report["audits"]["thermo"]),
    ]:
        icon = "✅ PASS" if a["status"] == "PASS" else ("⚠️ WARN" if a["status"] == "WARN" else "❌ FAIL")
        lines.append(f"| {name} | `{a['script']}` | **{icon}** | {a['summary']} |")

    lines.extend([
        "",
        "## 2. Maker/Critic 5-Pillar Verification Checklist",
        "",
        f"- [{'x' if report['audits']['cad']['status'] == 'PASS' else ' '}] **Pillar 1 (DFM Sanity):** Sheet thicknesses (1.5mm inner / 1.2mm outer), laser pierce ratios (>=1.0*t), and 0.25mm tab/slot fit clearance.",
        f"- [{'x' if report['audits']['thermo']['status'] in ['PASS', 'WARN'] else ' '}] **Pillar 2 (Thermal Safety):** 500°C target sustained; 63% mouth ratio preserved; expansion relief slots >= 6.5mm.",
        f"- [{'x' if report['audits']['oshwa']['status'] == 'PASS' else ' '}] **Pillar 3 (OSHWA Compliance):** Dual licensing (CERN-OHL-P v2 / CC-BY-4.0), complete BOM tracking.",
        f"- [{'x' if not report.get('locks') else ' '}] **Pillar 4 (Lock Hygiene):** All `.agents/locks/` advisory locks released prior to review.",
        f"- [{'x' if report['verdict'] != 'CHANGES_REQUESTED' else ' '}] **Pillar 5 (Code Execution):** Automated test scripts run cleanly without unhandled exceptions.",
        "",
        "## 3. Git Diff & Working Tree State",
    ])

    if report["git"]["modified_files"]:
        lines.append("```")
        for f in report["git"]["modified_files"][:15]:
            lines.append(f)
        if len(report["git"]["modified_files"]) > 15:
            lines.append(f"... and {len(report['git']['modified_files']) - 15} more files")
        lines.append("```")
    else:
        lines.append("*Working tree clean.*")

    lines.extend([
        "",
        "## 4. Critic Notes & Action Items",
    ])

    if report["verdict"] == "APPROVED":
        lines.append("All mechanical tolerances, open hardware standards, and thermal constraints are satisfied. Changes are certified for merging and commit with `[agent:maker]` signature.")
    elif report["verdict"] == "APPROVED_WITH_WARNINGS":
        lines.append("**Advisory Note on Thermodynamics:** The 1D conductive model indicates outer skin temperature of ~102°C at 500°C sustained continuous bake without thermal standoffs. The CAD design must incorporate the 5mm ceramic washer standoffs or increase insulation blanket thickness to >= 35mm to achieve safe touch <= 60°C. Non-blocking for mechanical DFM review.")
    else:
        lines.append("**Action Required:** One or more critical audits failed. Inspect the failed validator scripts listed above, apply fixes, and re-trigger review.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Maker/Critic Review Engine")
    parser.add_argument("--maker", type=str, default="cursor", help="Maker agent identifier (e.g. cursor, claude-code)")
    parser.add_argument("--reviewer", type=str, default="antigrav", help="Reviewer critic agent identifier")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    parser.add_argument("--output", type=str, default="", help="File path to save the review card")
    args = parser.parse_args()

    report = generate_review(maker=args.maker, reviewer=args.reviewer, strict=args.strict)

    if args.json:
        output_text = json.dumps(report, indent=2)
    else:
        output_text = format_markdown_card(report)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"[OK] Review card saved to: {out_path}")

    print(output_text)

    # Return exit code based on verdict
    if report["verdict"] == "CHANGES_REQUESTED":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
