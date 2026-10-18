"""Repository jail for the bash, read_file, and write_file tools.

The child environment drops every variable whose name looks like a credential.
Commands may not leave the repository, dump the environment, or touch the
harness ledger. This is a workspace boundary for an agent that is supposed to
edit the oven, not a sandbox against a hostile process.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
from pathlib import Path


class SandboxError(RuntimeError):
    """The command or path is outside the repository jail."""


SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
DENY_PATTERNS = (
    re.compile(r"(^|[;&|`\n])\s*printenv\b"),
    re.compile(r"(^|[;&|`\n])\s*env\b"),
    re.compile(r"(^|[;&|`\n])\s*export\b"),
    re.compile(r"declare\s+-p"),
    re.compile(r"/proc/"),
    re.compile(r"\.\."),
    re.compile(r"ANTHROPIC_API_KEY"),
    re.compile(r"GEMINI_API_KEY"),
    re.compile(r"tools/opus"),
    re.compile(r"ledger\.jsonl"),
)
# Executables and system data a CAD or Blender run may touch.
ALLOW_ABSOLUTE = (
    "/usr",
    "/bin",
    "/lib",
    "/lib64",
    "/opt",
    "/tmp",
    "/dev/null",
    "/etc/ssl",
    "/etc/ca-certificates",
    "/etc/alternatives",
)
ABSOLUTE_PATH = re.compile(r"(?<![\w.-])(/[\w./+-]+)")
PROTECTED_PREFIXES = ("tools/opus/", ".git/")


def child_env(base: dict[str, str] | None = None, root: Path | None = None) -> dict[str, str]:
    source = base if base is not None else os.environ
    env: dict[str, str] = {}
    for name, value in source.items():
        upper = name.upper()
        if any(marker in upper for marker in SECRET_MARKERS):
            continue
        env[name] = value
    if root is not None:
        previous = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(root) if not previous else str(root) + os.pathsep + previous
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def resolve_in_repo(root: Path, relative: str) -> Path:
    if not relative or relative.startswith(("/", "~")):
        raise SandboxError("path must be relative to the repository")
    if "\x00" in relative:
        raise SandboxError("path contains a null")
    root_real = root.resolve()
    path = (root_real / relative).resolve()
    if path != root_real and root_real not in path.parents:
        raise SandboxError("path escapes the repository")
    return path


def is_protected(root: Path, path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return True
    return any(relative == prefix.rstrip("/") or relative.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def check_command(command: str, root: Path) -> None:
    if not command.strip():
        raise SandboxError("empty command")
    if "\x00" in command:
        raise SandboxError("command contains a null")
    for pattern in DENY_PATTERNS:
        if pattern.search(command):
            raise SandboxError("command is outside the repository jail")
    root_real = root.resolve().as_posix()
    for match in ABSOLUTE_PATH.finditer(command):
        absolute = match.group(1)
        if absolute.startswith(root_real):
            continue
        if absolute.startswith(ALLOW_ABSOLUTE):
            continue
        raise SandboxError(f"absolute path is outside the repository jail: {absolute}")


def run_bash(root: Path, command: str, timeout_s: float = 60) -> dict:
    try:
        check_command(command, root)
    except SandboxError as exc:
        return {"ok": False, "timed_out": False, "code": None, "output": "", "error": str(exc)}
    timeout_s = max(1.0, min(float(timeout_s), 300.0))
    # cd is inside the shell so a relative command stays in the repo even if
    # the model tries to change directory first. `..` is already rejected.
    wrapped = f"cd {sh_quote(str(root.resolve()))} && {command}"
    proc = subprocess.Popen(
        ["bash", "-c", wrapped],
        cwd=str(root.resolve()),
        env=child_env(root=root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
        return {
            "ok": False,
            "timed_out": True,
            "code": None,
            "output": _clip((stdout or "") + (stderr or "")),
            "error": f"command exceeded {timeout_s:g}s",
        }
    output = _clip((stdout or "") + (stderr or ""))
    return {
        "ok": proc.returncode == 0,
        "timed_out": False,
        "code": proc.returncode,
        "output": output,
        "error": None if proc.returncode == 0 else f"exit {proc.returncode}",
    }


def _clip(text: str, limit: int = 8000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [{len(text)} chars truncated]\n"


def sh_quote(text: str) -> str:
    return "'" + text.replace("'", "'\"'\"'") + "'"


def read_file(root: Path, relative: str, limit: int = 20_000) -> dict:
    try:
        path = resolve_in_repo(root, relative)
    except SandboxError as exc:
        return {"ok": False, "error": str(exc)}
    if not path.is_file():
        return {"ok": False, "error": f"not a file: {relative}"}
    data = path.read_bytes()
    if b"\x00" in data[:1024]:
        return {"ok": True, "path": relative, "bytes": len(data), "binary": True, "text": ""}
    text = data.decode("utf-8", errors="replace")
    clipped = len(text) > limit
    body = text if not clipped else text[:limit]
    return {
        "ok": True,
        "path": relative,
        "bytes": len(data),
        "binary": False,
        "clipped": clipped,
        "text": body,
    }


def write_file(root: Path, relative: str, content: str, limit: int = 200_000) -> dict:
    if len(content) > limit:
        return {"ok": False, "error": f"content exceeds {limit} characters"}
    try:
        path = resolve_in_repo(root, relative)
    except SandboxError as exc:
        return {"ok": False, "error": str(exc)}
    if is_protected(root, path):
        return {"ok": False, "error": "the harness directory and .git are not writable from a tool"}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "path": relative, "bytes": path.stat().st_size}
