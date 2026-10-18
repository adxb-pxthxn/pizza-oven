#!/usr/bin/env python3
"""Agent loop for Claude Opus 5.5 on this oven repository.

The model id is whatever GET /v1/models lists for Opus 5.5. The key is read
from ANTHROPIC_API_KEY and is never printed. done means the model called
declare_done. verified means check() passed. A run can be done and still
unverified.

Examples
--------
python3 tools/opus/opus.py estimate
python3 tools/opus/opus.py dry-run --task tools/opus/tasks/render-textured.yaml
python3 tools/opus/opus.py mock --task tools/opus/tasks/mass-under-20kg.yaml
python3 tools/opus/opus.py ping
python3 tools/opus/opus.py probe
python3 tools/opus/opus.py run --task tools/opus/tasks/build-doc.yaml
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

from budget import BudgetError, Ledger, global_cap, load_prices, parse_usage
from cadtools import (
    FINISHES,
    VARIANTS,
    Receipts,
    cad_build,
    cad_interference,
    cad_mass,
    cad_render,
    cad_thermal,
    check,
    clip,
)
from sandbox import SandboxError, read_file, run_bash, write_file
from tasks import TaskError, load_task

REPO = Path(__file__).resolve().parents[2]
MESSAGES_URL = "https://api.anthropic.com/v1/messages"
MODELS_URL = "https://api.anthropic.com/v1/models"
API_VERSION = "2023-06-01"
RETRYABLE = {408, 409, 429, 500, 502, 503, 529}
OUTPUT_TOKENS_ASSUMED = 2000
TOOL_RESULT_TOKENS_ASSUMED = 1500
PROBE_INPUT_TOKENS_ASSUMED = 2000
HARD_TURN_CAP = 25
STALL_TURN = 15

SYSTEM_PROMPT = """You execute one pizza-oven task in this repository. The harness measures the result. You do not.

States. declare_done records that you believe the acceptance gate is already met. That state is done. verified becomes true only when check() passes on measured files and tool receipts. A summary, a render you only imagined, a mass you remember, or a clearance you did not compute is not a measurement. Quote kilograms, temperatures, and overlap volumes only from a tool result in this session.

How to work. Read the task. Use the tools. Rebuild from the parametric scripts under cad/freecad/. Do not hand-edit an FCStd. Do not select geometry by EdgeN identifiers; those names move. If the same tool error or the same failing check appears twice, change the construction instead of repeating the edit. A reply with no tool call ends the turn and the work pauses. While the gate is unmet, make the next tool call in the same turn as any status note. Stop when check() passes, when a tool result says the budget has stopped the session, or when you are blocked on something only the operator can provide.

Scope. The cooking geometry and the numbers already in design/variants/ are the source. Do not invent a fuel, an overall size, or a material stack the task did not name. No galvanised zinc in the hot path. The burner, valve, regulator, and hose stay bought and certified. New fabricated parts get a row in bom/bom.csv. Hardware designs are CERN-OHL-P v2. Notes are CC-BY-4.0. Write files only inside the repository. The tools/opus harness is not editable.

Budget. Input, output, and cache tokens are billed, and a hard cap ends the session. Prefer the smallest read that answers the question. Do not re-read a file you already have. Do not paste a long log back into the reply; the harness already truncated it.
"""


def redact(text: str, key: str | None = None) -> str:
    secret = key if key is not None else os.environ.get("ANTHROPIC_API_KEY", "")
    if secret:
        text = text.replace(secret, "[REDACTED]")
    return text


def api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is missing. Export it in the environment. "
            "This script will not read the key from a file."
        )
    return key


def cache_control(ttl: str) -> dict:
    if ttl == "5m":
        return {"type": "ephemeral"}
    if ttl == "1h":
        return {"type": "ephemeral", "ttl": "1h"}
    raise ValueError("cache ttl must be 5m or 1h")


def tool_defs(ttl: str) -> list[dict]:
    """Stable tool list. The last definition carries the cache breakpoint."""
    variant = {"type": "string", "enum": list(VARIANTS)}
    finish = {"type": "string", "enum": list(FINISHES)}
    tools = [
        {
            "name": "bash",
            "description": "Run a shell command with the working directory locked to the repository. Credentials are not in the environment. Paths outside the repo, environment dumps, and the harness directory are rejected. Use this for downloads and for inspecting command output.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "command": {"type": "string"},
                    "timeout_s": {"type": "integer"},
                },
                "required": ["command"],
            },
        },
        {
            "name": "read_file",
            "description": "Read a UTF-8 text file inside the repository. Long files are truncated. Binary files return a size only.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "write_file",
            "description": "Write a UTF-8 text file inside the repository. Refuses tools/opus and .git. Use this for the Blender script, the iteration record, BUILD.md, and templates.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
        {
            "name": "cad_build",
            "description": "Rebuild one variant by running cad/freecad/drive.py, which calls freecadcmd through tools/freecad_mcp. Writes FCStd, STEP, mass JSON, and the GA PNGs. Fails clearly when freecadcmd is missing. Do not invent a build result.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"variant": variant},
                "required": ["variant"],
            },
        },
        {
            "name": "cad_interference",
            "description": "Pairwise common-volume gate on the variant FCStd. Pairs of at least 1 mm^3 are returned. Names containing ferrule or dowel are the intended press fits. When freecadcmd is missing the tool records that and does not invent a volume.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"variant": variant},
                "required": ["variant"],
            },
        },
        {
            "name": "cad_thermal",
            "description": "Run cad/freecad/thermal_fea.py. Slab check, then both walls and both grips, via Gmsh and CalculiX. Rewrites design/variants/thermal-fea.json. Needs gmsh and ccx. Do not invent a temperature.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
        },
        {
            "name": "cad_mass",
            "description": "Measure ready mass and skin temperatures. mode evaluate reads design/variants/optimizer.json and calls cad/freecad/masslib.evaluate. It does not need FreeCAD or scipy. mode optimize runs cad/freecad/optimize.py and rewrites optimizer.json. Quote the returned ready_kg.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "variant": variant,
                    "mode": {"type": "string", "enum": ["evaluate", "optimize"]},
                },
                "required": ["variant"],
            },
        },
        {
            "name": "cad_render",
            "description": "kind ga reports the front, side, top, and section PNGs that cad_build wrote. kind blender runs blender --background --python on a script inside the repo and records a receipt. A PNG written any other way does not satisfy a render task. Finishes: jarrah, gidgee, brushed-aluminium, blued-steel.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "kind": {"type": "string", "enum": ["ga", "blender"]},
                    "variant": variant,
                    "finish": finish,
                    "script": {"type": "string"},
                    "output": {"type": "string"},
                },
                "required": ["kind", "variant"],
            },
        },
        {
            "name": "check",
            "description": "Run this task's measured acceptance gate. Returns pass or fail with the measurements. This is the only way verified becomes true. Calling it does not by itself mark done.",
            "input_schema": {"type": "object", "additionalProperties": False, "properties": {}},
        },
        {
            "name": "declare_done",
            "description": "Call only when you believe every acceptance predicate is already true. The harness runs check() immediately. If check fails you are done and not verified, and you should keep working. If check passes the session stops.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
            },
        },
    ]
    tools[-1]["cache_control"] = cache_control(ttl)
    return tools


def build_request(
    *,
    model: str,
    messages: list,
    max_tokens: int,
    effort: str,
    ttl: str,
) -> dict:
    """Messages request. No temperature, no forced tool_choice, no disabled thinking."""
    return {
        "model": model,
        "max_tokens": max_tokens,
        "system": [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": cache_control(ttl),
            }
        ],
        "tools": tool_defs(ttl),
        "messages": messages,
        "cache_control": cache_control(ttl),
        "output_config": {"effort": effort},
    }


def select_opus_55(models: list) -> str:
    ids = []
    for item in models:
        ids.append(item["id"] if isinstance(item, dict) else str(item))
    if "claude-opus-5-5" in ids:
        return "claude-opus-5-5"
    dated = sorted(model_id for model_id in ids if model_id.startswith("claude-opus-5-5"))
    if dated:
        return dated[-1]
    opus = [model_id for model_id in ids if "opus" in model_id]
    raise RuntimeError("no Opus 5.5 model in /v1/models. Opus ids seen: " + ", ".join(opus))


def list_models(transport, key: str, timeout_s: int = 30) -> list:
    collected = []
    after = None
    for _ in range(10):
        url = MODELS_URL + "?limit=1000"
        if after:
            url += "&after_id=" + urllib.request.quote(after)
        status, text = transport("GET", url, None, timeout_s, key)
        if status != 200:
            raise RuntimeError(redact(f"GET /v1/models HTTP {status}: {text[:400]}", key))
        payload = json.loads(text)
        page = payload.get("data") or []
        collected.extend(page)
        if not payload.get("has_more"):
            break
        after = payload.get("last_id") or (page[-1].get("id") if page else None)
        if not after:
            break
    return collected


def http_transport(method: str, url: str, body: dict | None, timeout_s: int, key: str) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": API_VERSION,
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return exc.code, detail
    except urllib.error.URLError as exc:
        return 0, redact(str(exc.reason), key)


def post_message(transport, body: dict, key: str, timeout_s: int, attempts: int, sleep) -> dict:
    delay = 1.0
    last = ""
    for attempt in range(attempts):
        status, text = transport("POST", MESSAGES_URL, body, timeout_s, key)
        if status == 200:
            return json.loads(text)
        last = redact(f"HTTP {status}: {text[:500]}", key)
        if status not in RETRYABLE or attempt + 1 == attempts:
            raise RuntimeError(last)
        sleep(delay)
        delay *= 2
    raise RuntimeError(last)


def probe_cost_usd(prices, max_tokens: int) -> float:
    """Conservative upper bound used to refuse a probe that could exceed $0.05."""
    return prices.cost(
        input_tokens=PROBE_INPUT_TOKENS_ASSUMED,
        output_tokens=max_tokens,
        cache_write_5m_tokens=0,
        cache_write_1h_tokens=0,
        cache_read_tokens=0,
    )


def estimate_task(prices, task: dict, prefix_tokens: int, task_tokens: int) -> dict:
    turns = int(task["expected_turns"])
    uncached = task_tokens + TOOL_RESULT_TOKENS_ASSUMED
    first = prices.cost(
        input_tokens=uncached,
        output_tokens=OUTPUT_TOKENS_ASSUMED,
        cache_write_5m_tokens=prefix_tokens,
        cache_write_1h_tokens=0,
        cache_read_tokens=0,
    )
    later = prices.cost(
        input_tokens=uncached,
        output_tokens=OUTPUT_TOKENS_ASSUMED,
        cache_write_5m_tokens=0,
        cache_write_1h_tokens=0,
        cache_read_tokens=prefix_tokens,
    )
    expected = first if turns < 1 else first + later * (turns - 1)
    return {
        "id": task["id"],
        "expected_turns": turns,
        "max_turns": int(task["max_turns"]),
        "max_budget_usd": float(task["max_budget_usd"]),
        "prefix_tokens_est": prefix_tokens,
        "expected_usd": round(expected, 4),
    }


def prefix_token_estimate(ttl: str) -> int:
    encoded = json.dumps({"system": SYSTEM_PROMPT, "tools": tool_defs(ttl)}, ensure_ascii=False)
    return max(1, len(encoded) // 4)


def task_token_estimate(task: dict) -> int:
    return max(1, len(json.dumps(task_message(task, 21.0, float(task["max_budget_usd"])))) // 4)


def task_message(task: dict, remaining_usd: float, task_cap: float) -> str:
    acceptance = json.dumps(task["acceptance"], indent=2)
    inputs = task.get("inputs") or []
    input_lines = "\n".join(f"- {item}" for item in inputs) or "- (none listed)"
    return (
        f"Task {task['id']}: {task['title']}\n\n"
        f"Goal:\n{task['goal'].strip()}\n\n"
        f"Inputs:\n{input_lines}\n\n"
        f"Acceptance gate, measured by check():\n{acceptance}\n\n"
        f"Task cap ${task_cap:.2f}. Session remaining ${remaining_usd:.2f}. "
        "A hard stop ends the session.\n"
        "Call the tools the gate names. When you believe the gate is met, call declare_done. "
        "verified is not yours to set.\n"
    )


def compact_messages(messages: list, max_chars: int = 60_000, keep_recent: int = 4) -> list:
    """Shrink old tool results once the transcript outgrows the budget.

    Assistant turns, including thinking blocks, are left untouched. The API
    rejects a tool loop that drops or rewrites them.
    """
    if len(json.dumps(messages)) <= max_chars:
        return messages
    locations = []
    for message_index, message in enumerate(messages):
        content = message.get("content")
        if message.get("role") != "user" or not isinstance(content, list):
            continue
        for block_index, block in enumerate(content):
            if isinstance(block, dict) and block.get("type") == "tool_result":
                locations.append((message_index, block_index))
    for message_index, block_index in locations[:-keep_recent]:
        block = messages[message_index]["content"][block_index]
        content = block.get("content")
        if isinstance(content, str) and len(content) > 240:
            block["content"] = content[:160] + " … [earlier tool result summarised]"
    return messages


def dispatch(name: str, payload: dict, root: Path, task: dict, receipts: Receipts) -> dict:
    try:
        if name == "bash":
            return run_bash(root, str(payload.get("command") or ""), float(payload.get("timeout_s") or 60))
        if name == "read_file":
            return read_file(root, str(payload.get("path") or ""))
        if name == "write_file":
            return write_file(root, str(payload.get("path") or ""), str(payload.get("content") or ""))
        if name == "cad_build":
            return cad_build(root, str(payload.get("variant") or ""), receipts)
        if name == "cad_interference":
            return cad_interference(root, str(payload.get("variant") or ""), receipts)
        if name == "cad_thermal":
            return cad_thermal(root, receipts)
        if name == "cad_mass":
            return cad_mass(root, str(payload.get("variant") or ""), str(payload.get("mode") or "evaluate"), receipts)
        if name == "cad_render":
            return cad_render(
                root,
                str(payload.get("kind") or ""),
                str(payload.get("variant") or ""),
                payload.get("finish"),
                payload.get("script"),
                payload.get("output"),
                receipts,
            )
        if name == "check":
            return check(task, root, receipts)
        if name == "declare_done":
            return {"ok": True, "summary": str(payload.get("summary") or "")}
    except (SandboxError, TimeoutError, subprocess_timeout(), OSError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": f"unknown tool {name}"}


def subprocess_timeout():
    import subprocess

    return subprocess.TimeoutExpired


def failure_signature(name: str, result: dict) -> str:
    if result.get("ok"):
        return ""
    if name == "check" or (name == "declare_done" and "check" in result):
        failures = result.get("failures") or result.get("check", {}).get("failures") or []
        return name + ":" + "|".join(failures[:6])
    text = str(result.get("error") or result.get("output") or "")
    first = text.strip().splitlines()[0][:180] if text.strip() else "failed"
    return f"{name}:{first}"


def run_session(
    task: dict,
    *,
    transport,
    key: str,
    ledger: Ledger | None,
    prices,
    model: str,
    effort: str,
    max_tokens: int,
    ttl: str,
    timeout_s: int,
    attempts: int,
    sleep,
    root: Path,
    task_cap: float,
    echo,
) -> dict:
    receipts = Receipts()
    done = False
    verified = False
    status = "incomplete"
    nudges = 0
    stalled = False
    repeats: dict[str, int] = {}
    run_spent = 0.0
    turns = 0
    max_turns = min(HARD_TURN_CAP, int(task["max_turns"]))
    remaining = ledger.remaining() if ledger is not None else task_cap
    messages = [{"role": "user", "content": task_message(task, remaining, task_cap)}]

    while turns < max_turns:
        if ledger is not None and (ledger.spent() >= ledger.cap_usd or run_spent >= task_cap):
            status = "budget_stop"
            break
        turns += 1
        messages = compact_messages(messages)
        body = build_request(model=model, messages=messages, max_tokens=max_tokens, effort=effort, ttl=ttl)
        response = post_message(transport, body, key, timeout_s, attempts, sleep)
        usage = parse_usage(response.get("usage"))
        cost = prices.cost(**usage)
        run_spent += cost
        remaining_after = None
        if ledger is not None:
            recorded = ledger.charge(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "task": task["id"],
                    "turn": turns,
                    "model": model,
                    "cost_usd": round(cost, 8),
                    "task_cap_usd": task_cap,
                    "task_spent_usd": round(run_spent, 8),
                    "stop_reason": response.get("stop_reason"),
                    **usage,
                }
            )
            remaining_after = recorded["remaining_usd"]
        else:
            remaining_after = task_cap - run_spent
        echo(
            f"turn {turns} cost ${cost:.4f} task ${run_spent:.4f} / ${task_cap:.2f} "
            f"remaining ${remaining_after:.4f} / ${ledger.cap_usd if ledger is not None else task_cap:.2f}"
        )
        content = response.get("content") or []
        messages.append({"role": "assistant", "content": content})
        tool_uses = [block for block in content if isinstance(block, dict) and block.get("type") == "tool_use"]
        if not tool_uses:
            if verified:
                status = "verified"
                break
            if nudges >= 2:
                status = "done_unverified" if done else "incomplete"
                break
            nudges += 1
            messages.append({"role": "user", "content": _nudge(task, done, verified)})
            continue

        results = []
        notes = []
        if turns >= STALL_TURN and not verified and not stalled:
            stalled = True
            notes.append(
                "Fifteen turns have not verified the gate. Do not repeat the same construction. Change approach."
            )
        for block in tool_uses:
            name = block.get("name") or ""
            payload = block.get("input") or {}
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = {}
            result = dispatch(name, payload, root, task, receipts)
            if name == "declare_done":
                done = True
                gate = check(task, root, receipts)
                verified = bool(gate["ok"])
                result = {"ok": True, "declared": True, "check": gate}
            elif name == "check":
                verified = bool(result.get("ok"))
            watched = result.get("check") if name == "declare_done" else result
            signature = failure_signature("check" if name == "declare_done" else name, watched or {})
            if signature:
                repeats[signature] = repeats.get(signature, 0) + 1
                if repeats[signature] == 2:
                    notes.append(
                        "The same failure has now happened twice. Do not repeat this construction. Change the approach."
                    )
            rendered = clip(json.dumps(result))
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id") or name,
                    "content": rendered,
                }
            )
            if verified:
                break
        if notes:
            results.append({"type": "text", "text": " ".join(notes)})
        messages.append({"role": "user", "content": results})
        if verified:
            status = "verified"
            break
        if ledger is not None and (ledger.spent() >= ledger.cap_usd or run_spent >= task_cap):
            status = "budget_stop"
            break
    else:
        status = "turn_cap" if not verified else "verified"

    if status == "incomplete" and done and not verified:
        status = "done_unverified"
    summary = {
        "status": status,
        "done": done,
        "verified": verified,
        "turns": turns,
        "model": model,
        "task": task["id"],
        "task_spent_usd": round(run_spent, 8),
        "remaining_usd": None if ledger is None else round(ledger.remaining(), 8),
    }
    echo(f"status {status} done {str(done).lower()} verified {str(verified).lower()} model {model} spent ${run_spent:.4f}")
    return summary


def _nudge(task: dict, done: bool, verified: bool) -> str:
    if done and not verified:
        return (
            "declare_done ran and check() did not pass. "
            "Read the failing measurements and continue with tools. Do not declare the task verified."
        )
    return (
        f"The task {task['id']} is not verified. Continue with the remaining work. "
        "If you are blocked, say what is blocking you."
    )


def _echo(text: str, key: str) -> None:
    print(redact(text, key), flush=True)


def cmd_estimate(prices) -> int:
    ttl = "5m"
    prefix = prefix_token_estimate(ttl)
    print(f"prefix_tokens_est {prefix} (characters/4 of the cached system prompt and tools)")
    print(f"assumed output tokens/turn {OUTPUT_TOKENS_ASSUMED}; assumed tool-result tokens/turn {TOOL_RESULT_TOKENS_ASSUMED}")
    print(f"prices USD/MTok input {prices.input} output {prices.output} cache_write_5m {prices.cache_write_5m} cache_read {prices.cache_read}")
    total = 0.0
    for path in sorted((REPO / "tools" / "opus" / "tasks").glob("*.yaml")):
        task = load_task(path)
        row = estimate_task(prices, task, prefix, task_token_estimate(task))
        total += row["expected_usd"]
        print(
            f"{row['id']}: expected ${row['expected_usd']:.4f} over {row['expected_turns']} turns, "
            f"cap ${row['max_budget_usd']:.2f}, max_turns {row['max_turns']}"
        )
    print(f"starter_tasks_expected_usd {total:.4f}")
    return 0


def cmd_dry_run(task: dict, prices, effort: str, max_tokens: int, ttl: str) -> int:
    body = build_request(
        model="(resolved at run time from GET /v1/models)",
        messages=[{"role": "user", "content": task_message(task, global_cap(None), float(task["max_budget_usd"]))}],
        max_tokens=max_tokens,
        effort=effort,
        ttl=ttl,
    )
    prefix = prefix_token_estimate(ttl)
    row = estimate_task(prices, task, prefix, task_token_estimate(task))
    gate = check(task, REPO, Receipts())
    print(f"dry_run task {task['id']} cap ${task['max_budget_usd']:.2f} expected ${row['expected_usd']:.4f}")
    print(f"request tools {len(body['tools'])} cache_control {body['cache_control']['type']} effort {body['output_config']['effort']}")
    print(f"tool_choice_omitted {('tool_choice' not in body)} temperature_omitted {('temperature' not in body)}")
    preview = {"ok": gate["ok"], "failures": gate["failures"][:8]}
    if "unittest" in gate["measured"]:
        preview["unittest"] = gate["measured"]["unittest"].get("status")
    print("gate_preview " + json.dumps(preview))
    print("status dry_run done false verified false")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Claude Opus 5.5 harness for this oven repository")
    parser.add_argument("command", choices=("run", "dry-run", "mock", "ping", "probe", "estimate", "ledger"))
    parser.add_argument("--task", type=Path)
    parser.add_argument("--budget", type=float, default=None, help="global cap in USD (default 21, or OPUS_BUDGET_USD)")
    parser.add_argument("--effort", default="medium", choices=("low", "medium", "high", "xhigh", "max"))
    parser.add_argument("--max-tokens", type=int, default=8000)
    parser.add_argument("--cache-ttl", default="5m", choices=("5m", "1h"))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--ledger", type=Path, default=REPO / "tools" / "opus" / "ledger.jsonl")
    parser.add_argument("--probe-max-tokens", type=int, default=16)
    args = parser.parse_args(argv)

    key_for_redaction = os.environ.get("ANTHROPIC_API_KEY", "")
    try:
        return _main(args, key_for_redaction)
    except (BudgetError, TaskError, RuntimeError) as exc:
        print(redact(str(exc), key_for_redaction), file=sys.stderr)
        return 1
    except Exception:
        print(redact(traceback.format_exc(), key_for_redaction), file=sys.stderr)
        return 1


def _main(args, key_for_redaction: str) -> int:
    prices = load_prices()
    if args.command == "estimate":
        return cmd_estimate(prices)
    cap = global_cap(args.budget)
    ledger = Ledger(args.ledger, cap)
    if args.command == "ledger":
        print(f"spent ${ledger.spent():.4f} remaining ${ledger.remaining():.4f} cap ${cap:.2f} file {args.ledger}")
        return 0
    if args.command in ("ping", "probe"):
        key = api_key()
        models = list_models(http_transport, key, args.timeout)
        model_id = select_opus_55(models)
        opus_ids = sorted(
            (item["id"] if isinstance(item, dict) else str(item)) for item in models if "opus" in (item["id"] if isinstance(item, dict) else str(item))
        )
        print(f"model_id {model_id}")
        print("opus_ids " + ",".join(opus_ids))
        if args.command == "ping":
            return 0
        bound = probe_cost_usd(prices, args.probe_max_tokens)
        if bound > 0.05:
            print(f"probe refused: worst-case ${bound:.4f} exceeds $0.05")
            return 2
        body = {
            "model": model_id,
            "max_tokens": args.probe_max_tokens,
            "output_config": {"effort": "low"},
            "messages": [{"role": "user", "content": "Reply with the single word ok."}],
        }
        response = post_message(http_transport, body, key, args.timeout, 1, time.sleep)
        usage = parse_usage(response.get("usage"))
        cost = prices.cost(**usage)
        recorded = ledger.charge(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "task": "probe",
                "turn": 1,
                "model": model_id,
                "cost_usd": round(cost, 8),
                "task_cap_usd": 0.05,
                "task_spent_usd": round(cost, 8),
                "stop_reason": response.get("stop_reason"),
                **usage,
            }
        )
        print("usage " + json.dumps(usage))
        print(f"probe_cost ${cost:.4f} remaining ${recorded['remaining_usd']:.4f}")
        return 0

    if args.task is None:
        raise RuntimeError("--task is required")
    task = load_task(args.task if args.task.is_absolute() else REPO / args.task)
    if args.command == "dry-run":
        return cmd_dry_run(task, prices, args.effort, args.max_tokens, args.cache_ttl)

    task_cap = min(float(task["max_budget_usd"]), ledger.remaining())
    if task_cap <= 0 and args.command == "run":
        print(f"budget remaining ${ledger.remaining():.4f} cap ${ledger.cap_usd:.2f}")
        print("status budget_stop done false verified false")
        return 2

    if args.command == "mock":
        summary = run_session(
            task,
            transport=_mock_transport(task),
            key="",
            ledger=None,
            prices=prices,
            model="mock-opus-5-5",
            effort=args.effort,
            max_tokens=args.max_tokens,
            ttl=args.cache_ttl,
            timeout_s=args.timeout,
            attempts=1,
            sleep=lambda _seconds: None,
            root=REPO,
            task_cap=float(task["max_budget_usd"]),
            echo=lambda text: _echo(text, ""),
        )
        return 0 if summary["status"] in ("verified", "done_unverified", "incomplete", "turn_cap") else 2

    key = api_key()
    models = list_models(http_transport, key, args.timeout)
    model_id = select_opus_55(models)
    print(f"model_id {model_id}")
    summary = run_session(
        task,
        transport=http_transport,
        key=key,
        ledger=ledger,
        prices=prices,
        model=model_id,
        effort=args.effort,
        max_tokens=args.max_tokens,
        ttl=args.cache_ttl,
        timeout_s=args.timeout,
        attempts=max(1, args.retries),
        sleep=time.sleep,
        root=REPO,
        task_cap=task_cap,
        echo=lambda text: _echo(text, key),
    )
    _write_status(summary)
    return 0 if summary["verified"] else 2


def _write_status(summary: dict) -> None:
    path = REPO / "tools" / "opus" / "last-run.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def _mock_transport(task: dict):
    """One declare_done, then text-only turns. No network and no ledger charge."""
    state = {"n": 0}

    def transport(method, url, body, timeout_s, key):
        if method == "GET":
            return 200, json.dumps({"data": [{"id": "claude-opus-5-5", "type": "model"}], "has_more": False})
        state["n"] += 1
        if state["n"] == 1:
            content = [
                {
                    "type": "thinking",
                    "thinking": "",
                    "signature": "mock-signature",
                },
                {
                    "type": "tool_use",
                    "id": "toolu_mock",
                    "name": "declare_done",
                    "input": {"summary": f"mock declare for {task['id']}"},
                },
            ]
        else:
            content = [{"type": "text", "text": "mock stop"}]
        payload = {
            "id": "msg_mock",
            "type": "message",
            "role": "assistant",
            "model": "mock-opus-5-5",
            "stop_reason": "tool_use" if state["n"] == 1 else "end_turn",
            "content": content,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        }
        return 200, json.dumps(payload)

    return transport


if __name__ == "__main__":
    sys.exit(main())
