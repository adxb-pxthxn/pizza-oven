"""Task files for the Opus harness.

The loader accepts a small YAML subset: maps, lists, scalars, and `|` / `>`
blocks. Task files stay inside that subset so the harness has no PyYAML
dependency. A corrupt task raises TaskError before any model call.
"""

from __future__ import annotations

import re
from pathlib import Path


class TaskError(ValueError):
    """The task file is missing a field the loop relies on."""


_INT = re.compile(r"-?\d+")
_FLOAT = re.compile(r"-?\d+\.\d+")


def load_task(path: Path) -> dict:
    payload = parse_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TaskError(f"{path} did not parse as a mapping")
    for key in ("id", "title", "goal", "max_budget_usd", "acceptance"):
        if key not in payload or payload[key] in ("", None):
            raise TaskError(f"{path} is missing {key}")
    if not isinstance(payload["acceptance"], dict):
        raise TaskError(f"{path} acceptance must be a mapping")
    payload["max_budget_usd"] = float(payload["max_budget_usd"])
    payload.setdefault("max_turns", 25)
    payload["max_turns"] = int(payload["max_turns"])
    payload.setdefault("expected_turns", min(8, payload["max_turns"]))
    payload["expected_turns"] = int(payload["expected_turns"])
    payload["_path"] = str(path)
    return payload


def parse_yaml(text: str):
    lines = text.splitlines()
    value, index = _parse_map(lines, 0, 0)
    trailing = _next_content(lines, index)
    if trailing < len(lines):
        raise TaskError(f"trailing content at line {trailing + 1}")
    return value


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _next_content(lines: list[str], index: int) -> int:
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return index
        index += 1
    return index


def _coerce(value: str):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in ("null", "~"):
        return None
    if _INT.fullmatch(value):
        return int(value)
    if _FLOAT.fullmatch(value):
        return float(value)
    return value


def _parse_block(lines: list[str], index: int, parent: int, folded: bool):
    collected: list[str] = []
    block_indent = None
    while index < len(lines):
        line = lines[index]
        if line.strip() == "":
            if block_indent is None:
                index += 1
                continue
            collected.append("")
            index += 1
            continue
        indent = _indent(line)
        if block_indent is None:
            if indent <= parent:
                return "", index
            block_indent = indent
        if indent < block_indent:
            break
        collected.append(line[block_indent:])
        index += 1
    text = "\n".join(collected).strip("\n")
    if folded:
        paragraphs = text.split("\n\n")
        text = "\n\n".join(" ".join(part.split()) for part in paragraphs)
    return text, index


def _parse_map(lines: list[str], index: int, indent: int):
    result: dict = {}
    while True:
        index = _next_content(lines, index)
        if index >= len(lines) or _indent(lines[index]) < indent:
            break
        if _indent(lines[index]) > indent:
            raise TaskError(f"unexpected indent at line {index + 1}")
        stripped = lines[index].strip()
        if stripped.startswith("- "):
            raise TaskError(f"list item where a key was expected at line {index + 1}")
        if ":" not in stripped:
            raise TaskError(f"expected a key at line {index + 1}")
        key, rest = stripped.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        if rest in ("|", ">"):
            value, index = _parse_block(lines, index + 1, indent, rest == ">")
        elif rest == "":
            nxt = _next_content(lines, index + 1)
            if nxt >= len(lines) or _indent(lines[nxt]) <= indent:
                value = None
                index += 1
            else:
                child = _indent(lines[nxt])
                if lines[nxt].lstrip().startswith("- "):
                    value, index = _parse_list(lines, nxt, child)
                else:
                    value, index = _parse_map(lines, nxt, child)
        else:
            value = _coerce(rest)
            index += 1
        result[key] = value
    return result, index


def _parse_list(lines: list[str], index: int, indent: int):
    items = []
    while True:
        index = _next_content(lines, index)
        if index >= len(lines) or _indent(lines[index]) < indent:
            break
        stripped = lines[index].lstrip()
        if not stripped.startswith("- "):
            break
        if _indent(lines[index]) > indent:
            raise TaskError(f"unexpected indent at line {index + 1}")
        rest = stripped[2:].strip()
        dash_indent = _indent(lines[index])
        if rest == "":
            nxt = _next_content(lines, index + 1)
            if nxt < len(lines) and _indent(lines[nxt]) > dash_indent:
                child = _indent(lines[nxt])
                if lines[nxt].lstrip().startswith("- "):
                    value, index = _parse_list(lines, nxt, child)
                else:
                    value, index = _parse_map(lines, nxt, child)
            else:
                value = None
                index += 1
        elif ":" in rest and not rest.startswith(("'", '"')):
            key, after = rest.split(":", 1)
            item: dict = {}
            after = after.strip()
            if after in ("|", ">"):
                item[key.strip()], index = _parse_block(lines, index + 1, dash_indent, after == ">")
            elif after == "":
                nxt = _next_content(lines, index + 1)
                if nxt < len(lines) and _indent(lines[nxt]) > dash_indent:
                    child = _indent(lines[nxt])
                    if lines[nxt].lstrip().startswith("- "):
                        item[key.strip()], index = _parse_list(lines, nxt, child)
                    else:
                        item[key.strip()], index = _parse_map(lines, nxt, child)
                else:
                    item[key.strip()] = None
                    index += 1
            else:
                item[key.strip()] = _coerce(after)
                index += 1
            nxt = _next_content(lines, index)
            if nxt < len(lines) and _indent(lines[nxt]) > dash_indent:
                extra, index = _parse_map(lines, nxt, _indent(lines[nxt]))
                item.update(extra)
            value = item
        else:
            value = _coerce(rest)
            index += 1
        items.append(value)
    return items, index
