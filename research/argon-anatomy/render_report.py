"""Turn REPORT.md into a print HTML file. Stdlib only."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "REPORT.md"
DST = ROOT / "report.html"


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def render(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            out.append(f"<h{level}>{inline(line[level:].strip())}</h{level}>")
            i += 1
            continue
        if line.startswith("|"):
            rows: list[str] = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            cells = [[part.strip() for part in row.strip("|").split("|")] for row in rows]
            body_rows = [row for row in cells if not all(set(cell) <= set("-: ") for cell in row)]
            out.append("<table>")
            for index, row in enumerate(body_rows):
                tag = "th" if index == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in row) + "</tr>")
            out.append("</table>")
            continue
        if line.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith("- "):
                out.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("</ul>")
            continue
        if line.startswith("```"):
            i += 1
            buff: list[str] = []
            while i < len(lines) and not lines[i].startswith("```"):
                buff.append(lines[i])
                i += 1
            i += 1
            out.append("<pre>" + html.escape("\n".join(buff)) + "</pre>")
            continue
        buff = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "- ", "```")):
            buff.append(lines[i])
            i += 1
        out.append("<p>" + inline(" ".join(buff)) + "</p>")
    return "\n".join(out)


def main() -> None:
    body = render(SRC.read_text())
    figures = """
<h2>Figures</h2>
<figure><img src="drawings/dome-xl-section.svg" alt="Dome XL section"/><figcaption>Dome XL section. Body 520 mm, hearth 187 mm, flue to 997 mm.</figcaption></figure>
<figure><img src="drawings/dome-xl.png" alt="Dome XL shaded solid"/><figcaption>Shaded solid of the Dome XL reconstruction.</figcaption></figure>
<figure><img src="drawings/dome-xl-cutaway.png" alt="Dome XL cutaway render"/><figcaption>Cutaway of the same solid. The section sheet is the dimensioned view.</figcaption></figure>
<figure><img src="drawings/arc-lite.png" alt="Arc Lite shaded solid"/><figcaption>Arc Lite reconstructed envelope.</figcaption></figure>
<figure><img src="drawings/tread.png" alt="Tread shaded solid"/><figcaption>Tread reconstructed envelope.</figcaption></figure>
"""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Gozney reconstruction for an Adelaide build</title>
<style>
  body {{ font: 14px/1.45 "Iowan Old Style", Palatino, Georgia, serif; color: #1c1a17; margin: 28px auto; max-width: 860px; }}
  h1 {{ font-size: 26px; line-height: 1.2; }}
  h2 {{ font-size: 18px; margin-top: 1.6em; border-top: 1px solid #d9d3c8; padding-top: 0.6em; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12px; margin: 0.6em 0 1em; }}
  th, td {{ border: 1px solid #d0c9bc; padding: 4px 6px; text-align: left; vertical-align: top; }}
  th {{ background: #f3efe6; }}
  code, pre {{ font-family: ui-monospace, Menlo, monospace; font-size: 12px; }}
  pre {{ background: #f6f3ec; padding: 10px; white-space: pre-wrap; }}
  img {{ width: 100%; height: auto; }}
  figcaption {{ font-size: 12px; color: #3c3832; margin-bottom: 1em; }}
</style>
</head>
<body>
{body}
{figures}
</body>
</html>
"""
    DST.write_text(page)
    print(DST)


if __name__ == "__main__":
    main()
