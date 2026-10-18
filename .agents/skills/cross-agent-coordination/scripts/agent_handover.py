#!/usr/bin/env python3
"""
Agent Handover & Coordination CLI Tool
Part of the Open-Source Neapolitan Pizza Oven Project (.agents/skills/cross-agent-coordination)

Provides 10-second situational awareness, git status inspection, task board
management, advisory file locking, and cursor prompt export for multi-agent workflows
(Antigravity, Cursor, Claude Code, Codex).
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def find_repo_root() -> Path:
    """Find the root directory of the git repository."""
    current = Path(__file__).resolve().parent
    for p in [current] + list(current.parents):
        if (p / ".git").is_dir() or (p / ".agents").is_dir():
            return p
    return Path.cwd()


REPO_ROOT = find_repo_root()
HANDOVER_PATH = REPO_ROOT / "docs" / "HANDOVER.md"
TASK_BOARD_PATH = REPO_ROOT / ".agents" / "state" / "TASK_BOARD.md"
LOCKS_DIR = REPO_ROOT / ".agents" / "locks"


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    """Execute a shell command in REPO_ROOT and return (exit_code, stdout, stderr)."""
    try:
        res = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def get_git_state() -> dict:
    """Gather git branch, commit, status, and diff statistics."""
    branch = "unknown"
    commit = "unknown"
    status_lines = []
    diff_stat = ""

    code, out, _ = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code == 0 and out:
        branch = out

    code, out, _ = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    if code == 0 and out:
        commit = out

    code, out, _ = run_cmd(["git", "status", "--porcelain"])
    if code == 0 and out:
        status_lines = [line.strip() for line in out.splitlines() if line.strip()]

    code, out, _ = run_cmd(["git", "diff", "--stat"])
    if code == 0 and out:
        diff_stat = out

    staged_code, staged_diff, _ = run_cmd(["git", "diff", "--cached", "--stat"])
    if staged_code == 0 and staged_diff:
        if diff_stat:
            diff_stat += "\n" + staged_diff
        else:
            diff_stat = staged_diff

    return {
        "branch": branch,
        "commit": commit,
        "status_lines": status_lines,
        "clean": len(status_lines) == 0,
        "diff_stat": diff_stat,
        "modified_count": len(status_lines)
    }


def clean_and_get_locks() -> list[dict]:
    """Inspect and clean expired locks from .agents/locks/."""
    LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    active_locks = []
    now = time.time()

    for lock_file in LOCKS_DIR.glob("*.lock"):
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            expires_at = data.get("expires_timestamp", 0)
            if expires_at > 0 and now > expires_at:
                # Expired lock
                lock_file.unlink(missing_ok=True)
            else:
                data["_file_path"] = str(lock_file)
                active_locks.append(data)
        except Exception:
            continue

    return active_locks


def acquire_lock(target_file: str, agent: str, reason: str, ttl_minutes: int = 15) -> bool:
    """Acquire an advisory lock on target_file for agent."""
    LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = target_file.replace("/", "__").replace("\\", "__") + ".lock"
    lock_file = LOCKS_DIR / safe_name
    active = clean_and_get_locks()

    for item in active:
        if item.get("target_file") == target_file:
            if item.get("agent") == agent:
                # Refresh existing lock
                break
            else:
                print(f"[ERROR] Cannot acquire lock on '{target_file}'. Already locked by '{item.get('agent')}'. Reason: {item.get('reason')}")
                return False

    now = time.time()
    iso_now = datetime.now(timezone.utc).isoformat()
    expires_at = now + (ttl_minutes * 60)
    expires_iso = datetime.fromtimestamp(expires_at, timezone.utc).isoformat()

    lock_data = {
        "target_file": target_file,
        "agent": agent,
        "pid": os.getpid(),
        "created_at": iso_now,
        "expires_timestamp": expires_at,
        "expires_at": expires_iso,
        "reason": reason or "Active edit session"
    }

    with open(lock_file, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)

    print(f"[OK] Advisory lock acquired on '{target_file}' for '{agent}' (TTL: {ttl_minutes}m, expires {expires_iso}).")
    return True


def release_lock(target_file: str, agent: str, force: bool = False) -> bool:
    """Release an advisory lock."""
    safe_name = target_file.replace("/", "__").replace("\\", "__") + ".lock"
    lock_file = LOCKS_DIR / safe_name
    if not lock_file.exists():
        print(f"[INFO] No lock found for '{target_file}'.")
        return True

    try:
        with open(lock_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        locked_by = data.get("agent", "")
        if not force and locked_by and locked_by != agent and agent != "system":
            print(f"[WARNING] Lock on '{target_file}' is held by '{locked_by}', not '{agent}'. Use --force to override.")
            return False
        lock_file.unlink(missing_ok=True)
        print(f"[OK] Lock released on '{target_file}'.")
        return True
    except Exception as e:
        print(f"[ERROR] Could not release lock: {e}")
        return False


def get_handover_summary() -> dict:
    """Read essential sections from docs/HANDOVER.md."""
    if not HANDOVER_PATH.exists():
        return {
            "exists": False,
            "active_agent": "unknown",
            "timestamp": "none",
            "status": "NOT_INITIALIZED",
            "summary": "Handover document does not exist yet.",
            "next_steps": []
        }

    content = HANDOVER_PATH.read_text(encoding="utf-8")
    active_agent = "unknown"
    timestamp = "unknown"
    status = "UNKNOWN"
    summary_lines = []
    next_steps = []

    lines = content.splitlines()
    in_summary = False
    in_next_steps = False

    for line in lines:
        if line.startswith("**Active Agent:**"):
            active_agent = line.replace("**Active Agent:**", "").strip()
        elif line.startswith("**Timestamp:**"):
            timestamp = line.replace("**Timestamp:**", "").strip()
        elif line.startswith("**Overall Status:**"):
            status = line.replace("**Overall Status:**", "").strip()
        elif line.startswith("## 1. Executive Summary"):
            in_summary = True
            in_next_steps = False
            continue
        elif line.startswith("## 2. Completed in This Session"):
            in_summary = False
        elif line.startswith("## 3. Immediate Next Steps"):
            in_summary = False
            in_next_steps = True
            continue
        elif line.startswith("## 4. Invariants"):
            in_next_steps = False

        if in_summary and line.strip() and not line.startswith("#"):
            summary_lines.append(line.strip())
        elif in_next_steps and line.strip() and not line.startswith("#"):
            next_steps.append(line.strip())

    return {
        "exists": True,
        "active_agent": active_agent,
        "timestamp": timestamp,
        "status": status,
        "summary": " ".join(summary_lines) if summary_lines else "No executive summary provided.",
        "next_steps": next_steps[:5]
    }


def parse_task_board() -> dict:
    """Parse .agents/state/TASK_BOARD.md into categories and task items."""
    if not TASK_BOARD_PATH.exists():
        return {"columns": {}}

    content = TASK_BOARD_PATH.read_text(encoding="utf-8")
    columns = {"BACKLOG": [], "READY": [], "IN_PROGRESS": [], "UNDER_REVIEW": [], "DONE": []}
    current_col = None

    for line in content.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("## "):
            col_header = line_clean.replace("## ", "").strip().upper()
            for key in columns:
                if key in col_header:
                    current_col = key
                    break
        elif current_col and (line_clean.startswith("- [ ]") or line_clean.startswith("- [x]")):
            columns[current_col].append(line_clean)

    return {"columns": columns}


def cmd_summary():
    """Print the 10-Second Situational Awareness Summary."""
    git_st = get_git_state()
    handover = get_handover_summary()
    locks = clean_and_get_locks()
    board = parse_task_board()

    print("=" * 76)
    print("  10-SECOND AGENT SITUATIONAL AWARENESS BRIEFING")
    print("  Repository: Open-Source Neapolitan Pizza Oven (Dual CERN / CC-BY)")
    print("=" * 76)
    print(f"Git State:      Branch: {git_st['branch']} | Commit: {git_st['commit']}")
    print(f"Working Tree:   {'CLEAN' if git_st['clean'] else f'{git_st['modified_count']} files modified / untracked'}")
    if git_st["diff_stat"]:
        print("Diff Stats:")
        for l in git_st["diff_stat"].splitlines()[:5]:
            print(f"  {l}")

    print("-" * 76)
    print(f"Last Agent:     {handover.get('active_agent', 'none')} ({handover.get('timestamp', 'unknown')})")
    print(f"Handover State: {handover.get('status', 'NONE')}")
    print(f"Brief Summary:  {handover.get('summary', '')}")

    print("-" * 76)
    print("Active File Locks:")
    if not locks:
        print("  [None] All files unlocked. Safe for editing.")
    else:
        for lock in locks:
            print(f"  * {lock.get('target_file')} - locked by '{lock.get('agent')}' (expires {lock.get('expires_at')})")

    print("-" * 76)
    print("Active Kanban Tasks:")
    in_prog = board.get("columns", {}).get("IN_PROGRESS", [])
    ready = board.get("columns", {}).get("READY", [])
    under_rev = board.get("columns", {}).get("UNDER_REVIEW", [])

    if in_prog:
        print("  IN PROGRESS:")
        for t in in_prog:
            print(f"    {t}")
    if under_rev:
        print("  UNDER REVIEW:")
        for t in under_rev:
            print(f"    {t}")
    if ready:
        print("  READY (Next Up):")
        for t in ready[:3]:
            print(f"    {t}")
    if not (in_prog or under_rev or ready):
        print("  No tasks currently in progress or ready queue.")

    print("-" * 76)
    print("Next Immediate Steps:")
    steps = handover.get("next_steps", [])
    if steps:
        for s in steps:
            print(f"  {s}")
    else:
        print("  1. Consult docs/engineering-specifications.md and bom/bom.csv")
        print("  2. Run python3 .agents/skills/code-cad/scripts/cad_validate.py")
    print("=" * 76)


def cmd_status():
    """Print complete task board, handover state, and lock details."""
    print("=== HANDOVER DOCUMENT STATUS ===")
    if HANDOVER_PATH.exists():
        print(f"Path: {HANDOVER_PATH}")
        print(HANDOVER_PATH.read_text(encoding="utf-8"))
    else:
        print("docs/HANDOVER.md not found.")

    print("\n=== TASK BOARD STATUS ===")
    if TASK_BOARD_PATH.exists():
        print(f"Path: {TASK_BOARD_PATH}")
        print(TASK_BOARD_PATH.read_text(encoding="utf-8"))
    else:
        print(".agents/state/TASK_BOARD.md not found.")

    print("\n=== ACTIVE LOCKS ===")
    locks = clean_and_get_locks()
    if locks:
        print(json.dumps(locks, indent=2))
    else:
        print("No active locks found.")


def cmd_new_task(title: str, agent: str, priority: str, category: str, description: str):
    """Add a new task ticket to .agents/state/TASK_BOARD.md."""
    TASK_BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not TASK_BOARD_PATH.exists():
        init_task_board()

    content = TASK_BOARD_PATH.read_text(encoding="utf-8")
    task_id = f"TASK-{int(time.time()) % 10000:04d}"
    item_str = f"- [ ] **[{task_id}]** `{category.upper()}`: {title} *(Priority: {priority}, Assigned: {agent or 'unassigned'})*\n  - {description}"

    # Insert under ## READY (or BACKLOG)
    target_section = "## READY"
    if target_section in content:
        parts = content.split(target_section, 1)
        new_content = parts[0] + target_section + "\n" + item_str + "\n" + parts[1]
    else:
        new_content = content + f"\n\n{target_section}\n{item_str}\n"

    TASK_BOARD_PATH.write_text(new_content, encoding="utf-8")
    print(f"[OK] Added task [{task_id}] '{title}' to {TASK_BOARD_PATH}")


def cmd_update(task_id: str, new_status: str, agent: str, notes: str):
    """Move a task to a new column and update notes in task board and handover doc."""
    if not TASK_BOARD_PATH.exists():
        print(f"[ERROR] {TASK_BOARD_PATH} does not exist.")
        return

    content = TASK_BOARD_PATH.read_text(encoding="utf-8")
    new_status = new_status.upper()
    valid_cols = ["BACKLOG", "READY", "IN_PROGRESS", "UNDER_REVIEW", "DONE"]
    if new_status not in valid_cols:
        print(f"[ERROR] Invalid status '{new_status}'. Must be one of: {', '.join(valid_cols)}")
        return

    lines = content.splitlines()
    found_line = None
    other_lines = []
    
    # Locate task line
    for line in lines:
        if task_id in line and ("- [ ]" in line or "- [x]" in line):
            found_line = line
        else:
            other_lines.append(line)

    if not found_line:
        print(f"[WARNING] Task '{task_id}' not found in task board. Will create record.")
        found_line = f"- [ ] **[{task_id}]**: Updated task (Owner: {agent})"

    if new_status == "DONE":
        found_line = found_line.replace("- [ ]", "- [x]")
    else:
        found_line = found_line.replace("- [x]", "- [ ]")

    if notes:
        found_line += f" <!-- note: {notes} -->"

    # Re-insert into target column
    new_text = "\n".join(other_lines)
    header_target = f"## {new_status}"
    if header_target in new_text:
        parts = new_text.split(header_target, 1)
        final_content = parts[0] + header_target + "\n" + found_line + "\n" + parts[1]
    else:
        final_content = new_text + f"\n\n{header_target}\n{found_line}\n"

    TASK_BOARD_PATH.write_text(final_content, encoding="utf-8")
    print(f"[OK] Moved task {task_id} to '{new_status}' in TASK_BOARD.md")

    # Update docs/HANDOVER.md if notes provided
    if notes and HANDOVER_PATH.exists():
        update_handover_notes(agent, notes, new_status)


def update_handover_notes(agent: str, notes: str, status: str):
    """Update docs/HANDOVER.md timestamp, agent, and status."""
    content = HANDOVER_PATH.read_text(encoding="utf-8")
    iso_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = content.splitlines()
    out = []
    for line in lines:
        if line.startswith("**Active Agent:**"):
            out.append(f"**Active Agent:** {agent}")
        elif line.startswith("**Timestamp:**"):
            out.append(f"**Timestamp:** {iso_now}")
        elif line.startswith("**Overall Status:**"):
            out.append(f"**Overall Status:** {status}")
        else:
            out.append(line)

    HANDOVER_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[OK] Updated docs/HANDOVER.md metadata for agent '{agent}'.")


def cmd_export_cursor() -> str:
    """Generate a high-density situational markdown snippet for Cursor Composer."""
    git_st = get_git_state()
    handover = get_handover_summary()
    board = parse_task_board()

    snippet = [
        "<!-- CURSOR COMPOSER CONTEXT INJECTION -->",
        f"# Pizza Oven Physical Engineering — Active Session Context",
        f"**Repository Root:** `{REPO_ROOT}`",
        f"**Branch / Commit:** `{git_st['branch']} @ {git_st['commit']}`",
        f"**Handover Status:** `{handover.get('status')}` (Updated by `{handover.get('active_agent')}` at `{handover.get('timestamp')}`)",
        "",
        "## Current Invariants & Engineering Constraints",
        "- **Target Temperature:** 500°C internal dome & floor; outer shell touch temperature <= 60°C.",
        "- **Chamber Mouth Ratio:** Neapolitan 63% mouth opening height / dome apex height.",
        "- **Laser Sheet DFM:** AISI 304 1.5mm inner, 1.2mm outer shroud; tab & slot 0.25mm fit clearance.",
        "- **Thermal Expansion:** 6.5mm expansion slots on hot-to-cold fastener points (min 3.9mm travel).",
        "- **Licenses & OSHWA:** CERN-OHL-P v2 (hardware), CC-BY-4.0 (docs); all parts must be logged in `bom/bom.csv`.",
        "",
        "## Working Tree & Modified Files",
    ]

    if git_st["status_lines"]:
        snippet.append("```")
        for line in git_st["status_lines"]:
            snippet.append(line)
        snippet.append("```")
    else:
        snippet.append("*Working tree is clean.*")

    snippet.append("")
    snippet.append("## Active Tasks in Flight")
    in_prog = board.get("columns", {}).get("IN_PROGRESS", [])
    ready = board.get("columns", {}).get("READY", [])
    if in_prog:
        for t in in_prog:
            snippet.append(f"- {t}")
    elif ready:
        for t in ready[:3]:
            snippet.append(f"- {t}")
    else:
        snippet.append("- No tasks marked IN_PROGRESS.")

    snippet.append("")
    snippet.append("## Immediate Next Instructions")
    for s in handover.get("next_steps", []):
        snippet.append(f"- {s}")

    snippet.append("")
    snippet.append("## Pre-Commit Verification Commands")
    snippet.append("```bash")
    snippet.append("python3 .agents/skills/code-cad/scripts/cad_validate.py")
    snippet.append("python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py")
    snippet.append("python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py")
    snippet.append("git commit -m \"feat(scope): description [agent:cursor]\"")
    snippet.append("```")

    result = "\n".join(snippet)
    print(result)
    return result


def init_task_board():
    """Initialize a default Kanban task board if absent."""
    default_board = """# Project Kanban Task Board

State tracking for autonomous agents (Antigravity, Cursor, Claude Code, Codex).

## IN_PROGRESS
- [ ] **[TASK-001]** `COORDINATION`: Cross-agent integration & cursor MDC sync *(Priority: HIGH, Assigned: antigrav)*

## READY
- [ ] **[TASK-002]** `CAD`: Parametric outer shroud sheet metal unfolding *(Priority: HIGH, Assigned: unassigned)*
- [ ] **[TASK-003]** `THERMO`: Outer touch temperature mitigation (<60°C standoff audit) *(Priority: HIGH, Assigned: unassigned)*
- [ ] **[TASK-004]** `BOM`: Supplier cross-references for refractory cordierite tiles *(Priority: MEDIUM, Assigned: unassigned)*

## UNDER_REVIEW

## DONE
- [x] **[TASK-000]** `SETUP`: Initial repository structure, OSHWA documentation, and base thermal model *(Priority: HIGH, Assigned: antigrav)*

## BACKLOG
- [ ] **[TASK-005]** `DOCS`: Multi-language laser cutting fabrication checklist *(Priority: LOW, Assigned: unassigned)*
- [ ] **[TASK-006]** `CAD`: Integrated digital pyrometer probe mount *(Priority: LOW, Assigned: unassigned)*
"""
    TASK_BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASK_BOARD_PATH.write_text(default_board, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Agent Handover & Situational Awareness CLI"
    )
    parser.add_argument("--summary", action="store_true", help="Print 10-second situational awareness briefing")
    parser.add_argument("--status", action="store_true", help="Display full task board, handover state, and locks")
    parser.add_argument("--new-task", action="store_true", help="Add a new task to TASK_BOARD.md")
    parser.add_argument("--update", action="store_true", help="Update task state in TASK_BOARD.md")
    parser.add_argument("--export-cursor", action="store_true", help="Export Cursor Composer context injection prompt")

    # Options for new-task / update
    parser.add_argument("--title", type=str, default="", help="Task title")
    parser.add_argument("--agent", type=str, default="antigrav", help="Agent identifier (antigrav, cursor, claude-code)")
    parser.add_argument("--priority", type=str, default="MEDIUM", help="Priority (HIGH, MEDIUM, LOW)")
    parser.add_argument("--category", type=str, default="CAD", help="Category (CAD, THERMO, BOM, DOCS, DFM)")
    parser.add_argument("--description", type=str, default="", help="Detailed task description")
    parser.add_argument("--id", type=str, default="", help="Task ID (e.g. TASK-001)")
    parser.add_argument("--task-status", type=str, default="", help="New task column: READY, IN_PROGRESS, UNDER_REVIEW, DONE")
    parser.add_argument("--notes", type=str, default="", help="Status update or handover notes")

    # Locking options
    parser.add_argument("--lock", type=str, default="", help="Target file path to lock")
    parser.add_argument("--unlock", type=str, default="", help="Target file path to unlock")
    parser.add_argument("--reason", type=str, default="", help="Reason for file lock")
    parser.add_argument("--ttl", type=int, default=15, help="Lock TTL in minutes (default 15)")
    parser.add_argument("--force", action="store_true", help="Force lock release")

    args = parser.parse_args()

    if args.lock:
        acquire_lock(args.lock, args.agent, args.reason, args.ttl)
        return

    if args.unlock:
        release_lock(args.unlock, args.agent, args.force)
        return

    if args.new_task:
        if not args.title:
            print("[ERROR] --title is required for --new-task")
            sys.exit(1)
        cmd_new_task(args.title, args.agent, args.priority, args.category, args.description)
        return

    if args.update:
        if not args.id or not args.task_status:
            print("[ERROR] Both --id and --task-status are required for --update")
            sys.exit(1)
        cmd_update(args.id, args.task_status, args.agent, args.notes)
        return

    if args.status:
        cmd_status()
        return

    if args.export_cursor:
        cmd_export_cursor()
        return

    # Default action is --summary
    cmd_summary()


if __name__ == "__main__":
    main()
