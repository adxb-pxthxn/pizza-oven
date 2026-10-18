#!/usr/bin/env python3
"""Mac-friendly Gemini orchestrator for this repository.

Reads GEMINI_API_KEY from the environment. The key is never printed, logged,
or written to disk. Stdlib only, so it runs on Apple Silicon with the system
python3 and no virtualenv.

Heavy reasoning uses gemini-4-argon at thinking level HIGH, the highest
named level. A call can instead set a thinking budget up to 65535; the
API accepts only one of the two. Summaries and formatting use a cheap
model (default gemini-2.5-flash-lite) with thinking left off.

Examples
--------
python3 tools/argon/argon.py ping
python3 tools/argon/argon.py call --prompt-file brief.md --out out.md
python3 tools/argon/argon.py batch --jobs jobs.json --workers 4
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_MODEL = "gemini-4-argon"
CHEAP_MODEL = "gemini-2.5-flash-lite"
API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_TIMEOUT_S = 600
DEFAULT_MAX_OUTPUT_TOKENS = 32768
# Highest named level. MEDIUM and LOW are lower. The API rejects a level
# and a budget in the same request, so the default uses the level.
THINKING_LEVEL_HIGH = "HIGH"
# Documented range is [-1, 65535]. -1 is dynamic. 65535 is the maximum
# budget, and it shares the output-token window with the answer.
MAX_THINKING_BUDGET = 65535


class ArgonError(RuntimeError):
    """Failure that is safe to show: the API key has already been redacted."""


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise ArgonError(
            "GEMINI_API_KEY is missing. Export it in the environment. "
            "This script will not read the key from a file."
        )
    return key


def redact(text: str, key: str | None = None) -> str:
    """Remove the API key and any URL that still carries it."""
    secret = key if key is not None else os.environ.get("GEMINI_API_KEY", "")
    cleaned = text
    if secret:
        cleaned = cleaned.replace(secret, "[REDACTED]")
    cleaned = cleaned.replace("key=[REDACTED]", "key=[REDACTED]")
    return cleaned


def _endpoint(model: str, key: str) -> str:
    return f"{API_ROOT}/{model}:generateContent?key={key}"


def is_reasoning_model(model: str) -> bool:
    """Models that should think hard unless a call opts out."""
    name = model.split("/")[-1]
    return name == DEFAULT_MODEL or name.startswith("gemini-4-argon")


def resolve_thinking(
    model: str,
    thinking_level: str | None = None,
    thinking_budget: int | None = None,
    *,
    enabled: bool | None = None,
) -> dict | None:
    """Return a thinkingConfig, or None to leave thinking off.

    The generateContent API accepts only one of thinkingLevel and
    thinkingBudget. Reasoning models default to thinkingLevel HIGH.
    Cheap models default to off. ``enabled=False`` forces that off
    unless a level or budget is passed explicitly.
    """
    if thinking_level and thinking_budget is not None:
        raise ArgonError(
            "Set only one of thinking_level and thinking_budget. "
            "The API rejects a request that contains both."
        )
    if thinking_level:
        return {"thinkingLevel": thinking_level.strip().upper()}
    if thinking_budget is not None:
        if thinking_budget < -1 or thinking_budget > MAX_THINKING_BUDGET:
            raise ArgonError(
                f"thinking_budget must be in [-1, {MAX_THINKING_BUDGET}], got {thinking_budget}"
            )
        return {"thinkingBudget": int(thinking_budget)}
    if enabled is False:
        return None
    if enabled is True or is_reasoning_model(model):
        return {"thinkingLevel": THINKING_LEVEL_HIGH}
    return None


def _extract_text(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        prompt_feedback = payload.get("promptFeedback")
        raise ArgonError(f"no candidates in response: {json.dumps(prompt_feedback)[:500]}")
    parts = ((candidates[0].get("content") or {}).get("parts")) or []
    chunks: list[str] = []
    for part in parts:
        if part.get("thought"):
            continue
        text = part.get("text")
        if text:
            chunks.append(text)
    if not chunks:
        # Some responses put the answer in a thought-only part when the
        # output budget is exhausted. Surface that as an error, not silence.
        finish = candidates[0].get("finishReason", "unknown")
        raise ArgonError(f"empty text parts (finishReason={finish})")
    return "".join(chunks).strip()


def generate(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    temperature: float = 0.4,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    json_mode: bool = False,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    retries: int = 3,
    thinking_level: str | None = None,
    thinking_budget: int | None = None,
    thinking: bool | None = None,
) -> dict:
    """Call generateContent. Returns text, model version, and usage metadata.

    ``thinking`` is the on/off default. None uses HIGH for gemini-4-argon
    and off for other models. A level or a budget overrides that default.
    """
    key = api_key()
    thinking_config = resolve_thinking(
        model,
        thinking_level,
        thinking_budget,
        enabled=thinking,
    )
    body: dict = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }
    if thinking_config:
        body["generationConfig"]["thinkingConfig"] = thinking_config
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"

    data = json.dumps(body).encode("utf-8")
    url = _endpoint(model, key)
    last_error = "unknown error"
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_s) as response:
                raw = response.read().decode("utf-8")
            payload = json.loads(raw)
            text = _extract_text(payload)
            usage = payload.get("usageMetadata") or {}
            return {
                "text": redact(text, key),
                "model": payload.get("modelVersion", model),
                "usage": usage,
                "attempts": attempt + 1,
                "thinking": thinking_config,
            }
        except ArgonError as exc:
            last_error = redact(str(exc), key)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            last_error = redact(f"HTTP {exc.code}: {detail}", key)
            # Auth failures will not improve on retry.
            if exc.code in {400, 401, 403}:
                break
        except Exception as exc:  # noqa: BLE001 — network and JSON errors
            last_error = redact(f"{type(exc).__name__}: {exc}", key)
        if attempt + 1 < retries:
            time.sleep(min(8, 2 ** attempt))
    raise ArgonError(last_error)


def _read_prompt(job: dict, root: Path) -> str:
    if "prompt" in job and job["prompt"]:
        return str(job["prompt"])
    prompt_file = job.get("prompt_file")
    if not prompt_file:
        raise ArgonError("job needs 'prompt' or 'prompt_file'")
    path = Path(prompt_file)
    if not path.is_absolute():
        path = root / path
    return path.read_text(encoding="utf-8")


def run_job(job: dict, root: Path) -> dict:
    started = time.time()
    job_id = str(job.get("id") or "job")
    model = str(job.get("model") or DEFAULT_MODEL)
    result = generate(
        _read_prompt(job, root),
        model=model,
        system=job.get("system"),
        temperature=float(job.get("temperature", 0.4)),
        max_output_tokens=int(job.get("max_output_tokens", DEFAULT_MAX_OUTPUT_TOKENS)),
        json_mode=bool(job.get("json", False)),
        timeout_s=int(job.get("timeout_s", DEFAULT_TIMEOUT_S)),
        retries=int(job.get("retries", 3)),
        thinking_level=job.get("thinking_level"),
        thinking_budget=job.get("thinking_budget"),
        thinking=job.get("thinking"),
    )
    out_path = None
    if job.get("out"):
        out_path = Path(job["out"])
        if not out_path.is_absolute():
            out_path = root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result["text"] + "\n", encoding="utf-8")
    usage = result["usage"]
    return {
        "id": job_id,
        "model": result["model"],
        "requested_model": model,
        "out": str(out_path) if out_path else None,
        "seconds": round(time.time() - started, 2),
        "attempts": result["attempts"],
        "prompt_tokens": usage.get("promptTokenCount"),
        "output_tokens": usage.get("candidatesTokenCount"),
        "thought_tokens": usage.get("thoughtsTokenCount"),
        "thinking": result.get("thinking"),
        "chars": len(result["text"]),
    }


def run_batch(jobs: list[dict], *, workers: int, root: Path) -> list[dict]:
    if workers < 1:
        raise ArgonError("workers must be >= 1")
    summaries: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_job, job, root): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            job_id = str(job.get("id") or "job")
            try:
                summary = future.result()
            except Exception as exc:  # noqa: BLE001
                summary = {
                    "id": job_id,
                    "error": redact(str(exc)),
                    "requested_model": job.get("model", DEFAULT_MODEL),
                }
                traceback.print_exc(file=sys.stderr)
            summaries.append(summary)
            status = "ERROR" if "error" in summary else "OK"
            print(f"[{status}] {job_id} {json.dumps({k: v for k, v in summary.items() if k != 'id'})}", flush=True)
    order = {str(job.get("id") or "job"): index for index, job in enumerate(jobs)}
    summaries.sort(key=lambda item: order.get(item["id"], 0))
    return summaries


def _load_jobs(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        jobs = payload.get("jobs")
    else:
        jobs = payload
    if not isinstance(jobs, list) or not jobs:
        raise ArgonError("jobs file must be a non-empty list, or an object with a 'jobs' list")
    return jobs


def cmd_ping(args: argparse.Namespace) -> int:
    result = generate(
        "Reply with exactly: ARGON_OK",
        model=args.model,
        temperature=0,
        max_output_tokens=64,
        timeout_s=90,
        retries=2,
        thinking=False,
    )
    print(result["text"])
    print(f"model={result['model']} attempts={result['attempts']} thinking=off")
    return 0 if result["text"].strip() == "ARGON_OK" else 2


def cmd_call(args: argparse.Namespace) -> int:
    prompt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else sys.stdin.read()
    system = Path(args.system_file).read_text(encoding="utf-8") if args.system_file else None
    result = generate(
        prompt,
        model=args.model,
        system=system,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        json_mode=args.json,
        timeout_s=args.timeout,
        thinking_level=args.thinking_level,
        thinking_budget=args.thinking_budget,
        thinking=False if args.no_thinking else None,
    )
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(result["text"] + "\n", encoding="utf-8")
    else:
        print(result["text"])
    usage = result["usage"]
    print(
        f"# model={result['model']} prompt_tokens={usage.get('promptTokenCount')} "
        f"output_tokens={usage.get('candidatesTokenCount')} "
        f"thought_tokens={usage.get('thoughtsTokenCount')} thinking={result.get('thinking')}",
        file=sys.stderr,
    )
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    jobs = _load_jobs(Path(args.jobs))
    summaries = run_batch(jobs, workers=args.workers, root=root)
    if args.summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary).write_text(json.dumps(summaries, indent=2) + "\n", encoding="utf-8")
    failed = [item for item in summaries if "error" in item]
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gemini Argon orchestrator. Never prints GEMINI_API_KEY.")
    sub = parser.add_subparsers(dest="command", required=True)

    ping = sub.add_parser("ping", help="Tiny live call. Prints ARGON_OK on success.")
    ping.add_argument("--model", default=DEFAULT_MODEL)
    ping.set_defaults(func=cmd_ping)

    call = sub.add_parser("call", help="One prompt, from a file or stdin.")
    call.add_argument("--model", default=DEFAULT_MODEL)
    call.add_argument("--prompt-file")
    call.add_argument("--system-file")
    call.add_argument("--out")
    call.add_argument("--json", action="store_true")
    call.add_argument("--temperature", type=float, default=0.4)
    call.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    call.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    call.add_argument(
        "--thinking-level",
        help="Named level (HIGH, MEDIUM, LOW). Default for gemini-4-argon is HIGH. Cannot be combined with --thinking-budget.",
    )
    call.add_argument(
        "--thinking-budget",
        type=int,
        help=f"Token budget from -1 (dynamic) to {MAX_THINKING_BUDGET}. Replaces the thinking level.",
    )
    call.add_argument(
        "--no-thinking",
        action="store_true",
        help="Leave thinking off. Use for grunt calls on a reasoning model.",
    )
    call.set_defaults(func=cmd_call)

    batch = sub.add_parser("batch", help="Run a jobs JSON file in parallel.")
    batch.add_argument("--jobs", required=True)
    batch.add_argument("--workers", type=int, default=4)
    batch.add_argument("--root", default=".")
    batch.add_argument("--summary")
    batch.set_defaults(func=cmd_batch)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ArgonError as exc:
        print(f"error: {redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
