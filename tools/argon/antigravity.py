#!/usr/bin/env python3
"""Reusable wrapper for Google's managed Antigravity agent.

This is the modelling harness. It does not call generateContent and it does
not fall back to tools/argon/argon.py.

POST https://generativelanguage.googleapis.com/v1beta/interactions
Header x-goog-api-key from GEMINI_API_KEY. The key is never printed.

The live Interactions schema for this agent accepts agent_config fields
type, model, and max_total_tokens. On 2026-10-18 the same endpoint rejected
the highest-thinking controls with these exact bodies:

- HTTP 400 {"error":{"message":"Unknown parameter 'thinking_level' at 'agent_config'.","code":"invalid_request"}}
- HTTP 400 {"error":{"message":"Unknown parameter 'generation_config'.","code":"invalid_request"}}
- HTTP 400 {"error":{"message":"Unknown parameter 'thinking_level'.","code":"invalid_request"}}
- HTTP 400 {"error":{"message":"Unknown parameter 'effort' at 'agent_config'.","code":"invalid_request"}}

gemini-4-argon is the highest model the agent accepts. A caller who passes
thinking_level or effort still sends that field. A 400 is raised with the
redacted body. The wrapper does not drop the field and retry.

Examples
--------
python3 tools/argon/antigravity.py ping
python3 tools/argon/antigravity.py run --prompt-file brief.md --source local.py:/workspace/local.py --text-out out.md
python3 tools/argon/antigravity.py continue --id INTERACTION_ID --environment ENV_ID --prompt-file next.md
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
API_REVISION = "2026-05-20"
AGENT = "antigravity-preview-09-2026"
MODEL = "gemini-4-argon"
# Highest named thinking level on the direct gemini-4-argon model.
# The managed-agent endpoint does not accept it. See the module docstring.
HIGHEST_THINKING_LEVEL = "high"
DEFAULT_TIMEOUT_S = 120
TERMINAL_STATUSES = {
    "completed",
    "failed",
    "incomplete",
    "cancelled",
    "canceled",
    "requires_action",
}
FILE_RE = re.compile(
    r"===== FILE (?P<path>[^\n=]+) =====\n(?P<body>.*?)\n===== END FILE =====",
    re.DOTALL,
)
B64_RE = re.compile(
    r"===== B64 (?P<path>[^\n=]+) =====\n(?P<body>.*?)\n===== END B64 =====",
    re.DOTALL,
)


class AntigravityError(RuntimeError):
    """Failure safe to show. The API key has already been redacted."""


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise AntigravityError(
            "GEMINI_API_KEY is missing. Export it in the environment. "
            "This script will not read the key from a file."
        )
    return key


def redact(text: str, key: str | None = None) -> str:
    secret = key if key is not None else os.environ.get("GEMINI_API_KEY", "")
    cleaned = text
    if secret:
        cleaned = cleaned.replace(secret, "[REDACTED]")
    return cleaned


def agent_config(
    *,
    model: str = MODEL,
    max_total_tokens: int | None = None,
    thinking_level: str | None = None,
    effort: str | None = None,
) -> dict:
    """Build the agent_config object.

    thinking_level and effort are included only when the caller sets them.
    They are not stripped. The endpoint currently rejects both.
    """
    config: dict = {"type": "antigravity", "model": model}
    if max_total_tokens is not None:
        config["max_total_tokens"] = int(max_total_tokens)
    if thinking_level:
        config["thinking_level"] = thinking_level
    if effort:
        config["effort"] = effort
    return config


def inline_source(local: Path, target: str) -> dict:
    data = local.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = None
    if text is not None and "\x00" not in text:
        return {"type": "inline", "target": target, "content": text}
    return {
        "type": "inline",
        "target": target,
        "content": base64.b64encode(data).decode("ascii"),
        "encoding": "base64",
    }


def parse_source_spec(spec: str) -> dict:
    if ":" not in spec:
        raise AntigravityError(
            "A source must be local-path:remote-target, for example "
            "cad/freecad/build_variant.py:/workspace/cad/freecad/build_variant.py"
        )
    local_text, target = spec.split(":", 1)
    local = Path(local_text)
    if not local.is_file():
        raise AntigravityError(f"source file does not exist: {local_text}")
    if not target.startswith("/"):
        raise AntigravityError(f"remote target must be an absolute path: {target}")
    return inline_source(local, target)


def build_body(
    prompt: str,
    *,
    sources: list[dict] | None = None,
    background: bool = True,
    model: str = MODEL,
    max_total_tokens: int | None = None,
    thinking_level: str | None = None,
    effort: str | None = None,
    previous_interaction_id: str | None = None,
    environment_id: str | None = None,
) -> dict:
    if sources:
        environment: dict | str = {"type": "remote", "sources": sources}
    elif environment_id:
        environment = environment_id
    else:
        environment = "remote"
    body: dict = {
        "agent": AGENT,
        "input": prompt,
        "environment": environment,
        "background": background,
        "store": True,
        "agent_config": agent_config(
            model=model,
            max_total_tokens=max_total_tokens,
            thinking_level=thinking_level,
            effort=effort,
        ),
    }
    if previous_interaction_id:
        body["previous_interaction_id"] = previous_interaction_id
    if environment_id and sources:
        body["environment"]["environment_id"] = environment_id
    return body


def _http_request(method: str, url: str, body: dict | None, timeout_s: int, key: str) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
            "Api-Revision": API_REVISION,
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AntigravityError(redact(f"HTTP {exc.code}: {detail}", key)) from None
    except AntigravityError:
        raise
    except Exception as exc:  # noqa: BLE001 — network and TLS failures
        raise AntigravityError(redact(f"{type(exc).__name__}: {exc}", key)) from None


def _decode_payload(raw: str, key: str) -> dict:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AntigravityError(redact(f"response was not JSON: {raw[:500]}", key)) from exc
    if not isinstance(payload, dict):
        raise AntigravityError("response JSON was not an object")
    return payload


def create(
    prompt: str,
    *,
    sources: list[dict] | None = None,
    background: bool = True,
    model: str = MODEL,
    max_total_tokens: int | None = None,
    thinking_level: str | None = None,
    effort: str | None = None,
    previous_interaction_id: str | None = None,
    environment_id: str | None = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    transport=None,
) -> dict:
    """Start one interaction. Raises AntigravityError on HTTP or network failure.

    There is no retry for 400, 401, 403, or 404. Those mean the request or
    the key is rejected. The caller must not substitute another client.
    """
    key = api_key()
    body = build_body(
        prompt,
        sources=sources,
        background=background,
        model=model,
        max_total_tokens=max_total_tokens,
        thinking_level=thinking_level,
        effort=effort,
        previous_interaction_id=previous_interaction_id,
        environment_id=environment_id,
    )
    sender = transport or _http_request
    try:
        status, raw = sender("POST", API_URL, body, timeout_s, key)
    except AntigravityError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AntigravityError(redact(f"{type(exc).__name__}: {exc}", key)) from None
    if status >= 400:
        raise AntigravityError(redact(f"HTTP {status}: {raw}", key))
    payload = _decode_payload(raw, key)
    if not payload.get("id"):
        raise AntigravityError(redact(f"interaction response had no id: {raw[:500]}", key))
    return payload


def get_interaction(interaction_id: str, *, timeout_s: int = DEFAULT_TIMEOUT_S, transport=None) -> dict:
    key = api_key()
    url = f"{API_URL}/{interaction_id}"
    sender = transport or _http_request
    try:
        status, raw = sender("GET", url, None, timeout_s, key)
    except AntigravityError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AntigravityError(redact(f"{type(exc).__name__}: {exc}", key)) from None
    if status >= 400:
        raise AntigravityError(redact(f"HTTP {status}: {raw}", key))
    return _decode_payload(raw, key)


def output_text(payload: dict) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    chunks: list[str] = []
    for step in payload.get("steps") or []:
        if step.get("type") not in (None, "model_output"):
            continue
        content = step.get("content")
        if isinstance(content, str):
            chunks.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type", "text") == "text" and part.get("text"):
                    chunks.append(part["text"])
                elif isinstance(part, str):
                    chunks.append(part)
    return "\n".join(chunks).strip()


def _decode_b64(body: str) -> bytes | None:
    """Decode one base64 block. A truncated block is skipped, not raised."""
    if "===== FILE " in body or "===== B64 " in body:
        return None
    blob = re.sub(r"[^A-Za-z0-9+/=]", "", body)
    if not blob:
        return None
    try:
        return base64.b64decode(blob, validate=False)
    except Exception:
        return None


def extract_files(text: str) -> list[tuple[str, bytes]]:
    """Pull files the agent emitted between FILE and B64 markers.

    A long answer can contain two copies when the model continues after a
    truncated block. The later complete copy wins. A base64 span that runs
    into the next marker is dropped instead of raising.
    """
    found: dict[str, bytes] = {}
    order: list[str] = []
    for match in FILE_RE.finditer(text):
        path = match.group("path").strip()
        body = match.group("body")
        if "===== FILE " in body or "===== B64 " in body:
            continue
        if path not in found:
            order.append(path)
        found[path] = body.encode("utf-8")
    for match in B64_RE.finditer(text):
        path = match.group("path").strip()
        data = _decode_b64(match.group("body"))
        if data is None:
            continue
        if path not in found:
            order.append(path)
        found[path] = data
    return [(path, found[path]) for path in order]


def write_files(files: list[tuple[str, bytes]], root: Path) -> list[Path]:
    written: list[Path] = []
    for relative, data in files:
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise AntigravityError(f"refusing to write an unsafe path: {relative}")
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        written.append(destination)
    return written


def poll(
    interaction_id: str,
    *,
    timeout_s: int,
    interval_s: float = 15.0,
    request_timeout_s: int = DEFAULT_TIMEOUT_S,
    transport=None,
    on_status=None,
) -> dict:
    """Poll until the interaction leaves in_progress, or the deadline passes."""
    deadline = time.monotonic() + timeout_s
    last = None
    while True:
        last = get_interaction(interaction_id, timeout_s=request_timeout_s, transport=transport)
        status = str(last.get("status") or "")
        if on_status:
            on_status(status, last)
        if status in TERMINAL_STATUSES:
            return last
        if status not in {"in_progress", "queued", "running"}:
            raise AntigravityError(f"unexpected interaction status: {status}")
        if time.monotonic() >= deadline:
            raise AntigravityError(
                f"timed out after {timeout_s}s while interaction {interaction_id} was {status}"
            )
        time.sleep(interval_s)


def public_summary(payload: dict, text: str) -> dict:
    usage = payload.get("usage") or {}
    keep_usage = {
        key: usage.get(key)
        for key in (
            "total_tokens",
            "total_input_tokens",
            "total_output_tokens",
            "total_thought_tokens",
            "total_tool_use_tokens",
            "total_cached_tokens",
        )
    }
    return {
        "id": payload.get("id"),
        "status": payload.get("status"),
        "agent": payload.get("agent", AGENT),
        "environment_id": payload.get("environment_id"),
        "model_requested": MODEL,
        "usage": keep_usage,
        "chars": len(text),
    }


def _read_prompt(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def cmd_ping(args: argparse.Namespace) -> int:
    created = create(
        "Reply with exactly ANTIGRAVITY_OK and nothing else. Do not use tools.",
        model=args.model,
        thinking_level=args.thinking_level,
        effort=args.effort,
        timeout_s=args.request_timeout,
    )
    print(f"id={created.get('id')} status={created.get('status')}")
    finished = poll(
        created["id"],
        timeout_s=args.timeout,
        interval_s=args.interval,
        on_status=lambda status, _payload: print(f"status={status}", flush=True),
    )
    text = redact(output_text(finished))
    print(text)
    print(json.dumps(public_summary(finished, text)))
    return 0 if text.strip() == "ANTIGRAVITY_OK" else 2


def cmd_pull(args: argparse.Namespace) -> int:
    text = Path(args.text).read_text(encoding="utf-8")
    written = write_files(extract_files(text), Path(args.pull_root))
    for path in written:
        print(f"pulled {path}")
    return 0 if written else 2


def cmd_run(args: argparse.Namespace) -> int:
    sources = [parse_source_spec(spec) for spec in args.source]
    prompt = _read_prompt(args.prompt_file)
    created = create(
        prompt,
        sources=sources or None,
        model=args.model,
        max_total_tokens=args.max_total_tokens,
        thinking_level=args.thinking_level,
        effort=args.effort,
        previous_interaction_id=args.previous,
        environment_id=args.environment,
        timeout_s=args.request_timeout,
    )
    interaction_id = created["id"]
    print(
        json.dumps(
            {
                "id": interaction_id,
                "status": created.get("status"),
                "environment_id": created.get("environment_id"),
                "agent": AGENT,
                "model": args.model,
            }
        ),
        flush=True,
    )
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(
            json.dumps({"created": public_summary(created, ""), "id": interaction_id}, indent=2) + "\n",
            encoding="utf-8",
        )
    finished = poll(
        interaction_id,
        timeout_s=args.timeout,
        interval_s=args.interval,
        on_status=lambda status, _payload: print(f"status={status}", flush=True),
    )
    text = redact(output_text(finished))
    summary = public_summary(finished, text)
    print(json.dumps(summary), flush=True)
    if args.text_out:
        destination = Path(args.text_out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text + ("\n" if text and not text.endswith("\n") else ""), encoding="utf-8")
    if args.out:
        Path(args.out).write_text(json.dumps({"summary": summary, "text_file": args.text_out}, indent=2) + "\n", encoding="utf-8")
    if args.pull_root and text:
        written = write_files(extract_files(text), Path(args.pull_root))
        for path in written:
            print(f"pulled {path}", flush=True)
    if finished.get("status") != "completed":
        raise AntigravityError(
            f"interaction {interaction_id} finished with status {finished.get('status')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--model", default=MODEL)
    common.add_argument("--thinking-level", default=None, help="Sent as agent_config.thinking_level. The endpoint rejects this.")
    common.add_argument("--effort", default=None, help="Sent as agent_config.effort. The endpoint rejects this.")
    common.add_argument("--max-total-tokens", type=int, default=None)
    common.add_argument("--timeout", type=int, default=3600, help="Seconds to poll.")
    common.add_argument("--request-timeout", type=int, default=DEFAULT_TIMEOUT_S)
    common.add_argument("--interval", type=float, default=15.0)

    parser = argparse.ArgumentParser(description="Call the managed Antigravity agent on the Gemini API.")
    sub = parser.add_subparsers(dest="command", required=True)

    ping = sub.add_parser("ping", parents=[common], help="Check that the agent endpoint accepts this key.")
    ping.set_defaults(func=cmd_ping)

    run = sub.add_parser("run", parents=[common], help="Start an interaction, poll, and optionally pull marked files.")
    run.add_argument("--prompt-file")
    run.add_argument("--source", action="append", default=[], help="local-path:remote-absolute-target. Repeatable.")
    run.add_argument("--previous", help="previous_interaction_id, to continue a sandbox.")
    run.add_argument("--environment", help="environment_id from an earlier interaction.")
    run.add_argument("--out", help="Write a short JSON summary here.")
    run.add_argument("--text-out", help="Write the agent's text answer here.")
    run.add_argument("--pull-root", help="Write FILE and B64 markers under this directory.")
    run.set_defaults(func=cmd_run)

    pull = sub.add_parser("pull", help="Write FILE and B64 markers from a saved answer.")
    pull.add_argument("--text", required=True, help="Saved agent answer.")
    pull.add_argument("--pull-root", required=True)
    pull.set_defaults(func=cmd_pull)

    follow = sub.add_parser("continue", parents=[common], help="Continue an existing sandbox.")
    follow.add_argument("--id", required=True)
    follow.add_argument("--environment", required=True)
    follow.add_argument("--prompt-file")
    follow.add_argument("--source", action="append", default=[])
    follow.add_argument("--out")
    follow.add_argument("--text-out")
    follow.add_argument("--pull-root")
    follow.set_defaults(func=cmd_run, previous=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "continue":
        args.previous = args.id
    try:
        return args.func(args)
    except AntigravityError as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
