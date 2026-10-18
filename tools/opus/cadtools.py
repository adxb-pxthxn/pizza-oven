"""Wrappers around the existing CAD scripts, and the measured check().

check() does not trust the model's report. Mass comes from
cad/freecad/masslib.evaluate. Interference comes from a freecadcmd run, or
from an explicit "freecadcmd is missing" result of that same tool. A Blender
render counts only when cad_render itself returned success.
"""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from sandbox import child_env, resolve_in_repo

REPO = Path(__file__).resolve().parents[2]
BURNER_KG = 1.85
VARIANTS = ("morning", "moondancer")
FINISHES = ("jarrah", "gidgee", "brushed-aluminium", "blued-steel")
INTENDED_PAIR = ("ferrule", "dowel")


class Receipts:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, tool: str, payload: dict) -> None:
        self.rows.append({"tool": tool, **payload})

    def find(self, tool: str, **match) -> dict | None:
        found = None
        for row in self.rows:
            if row.get("tool") != tool:
                continue
            if all(row.get(key) == value for key, value in match.items()):
                found = row
        return found


def clip(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    head = limit // 2
    marker = f"\n... [{len(text)} chars, {text.count(chr(10))} lines, middle omitted] ...\n"
    tail = max(0, limit - head - len(marker))
    return text[:head] + marker + text[-tail:]


def freecad_command() -> list[str] | None:
    import os
    import shlex

    configured = os.environ.get("FREECADCMD", "").strip()
    if configured:
        parts = shlex.split(configured)
        if parts and Path(parts[0]).exists():
            return parts
    default = Path("/tmp/freecad-dl/squashfs-root/usr/bin/freecadcmd")
    if default.exists():
        return [str(default)]
    tools = str(REPO / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    from freecad_mcp.headless import detect_freecadcmd

    return detect_freecadcmd()


def freecad_available() -> bool:
    return freecad_command() is not None


def _load_design(root: Path, variant: str):
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {', '.join(VARIANTS)}")
    sys.path.insert(0, str(root))
    from cad.freecad.masslib import Design

    payload = json.loads((root / "design" / "variants" / "optimizer.json").read_text(encoding="utf-8"))
    return Design(**payload[variant]["design"])


def evaluate_variant(root: Path, variant: str) -> dict:
    sys.path.insert(0, str(root))
    from cad.freecad.masslib import evaluate

    design = _load_design(root, variant)
    result = evaluate(design)
    keep = (
        "ready_kg",
        "stone_kg",
        "wall_outer_C",
        "wall_inner_face_C",
        "under_C",
        "grip_C",
        "outer_diameter",
        "body_height",
        "pizza_clearance",
        "mouth_over_apex",
    )
    public = {key: result[key] for key in keep}
    public["stone_d"] = float(design.stone_d)
    public["skin"] = design.skin
    return public


def cad_mass(root: Path, variant: str, mode: str, receipts: Receipts, timeout_s: float = 180) -> dict:
    mode = mode or "evaluate"
    if mode == "evaluate":
        measured = evaluate_variant(root, variant)
        payload = {"ok": True, "mode": "evaluate", "variant": variant, **measured}
        receipts.add("cad_mass", payload)
        return payload
    if mode != "optimize":
        return {"ok": False, "error": "mode must be evaluate or optimize"}
    proc = subprocess.run(
        [sys.executable, str(root / "cad" / "freecad" / "optimize.py")],
        cwd=str(root),
        env=child_env(root=root),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    payload = {
        "ok": proc.returncode == 0,
        "mode": "optimize",
        "variant": variant,
        "code": proc.returncode,
        "log": clip((proc.stdout or "") + (proc.stderr or "")),
        "note": "optimize rewrites design/variants/optimizer.json",
    }
    receipts.add("cad_mass", payload)
    return payload


def cad_build(root: Path, variant: str, receipts: Receipts, timeout_s: float = 180) -> dict:
    if variant not in VARIANTS:
        return {"ok": False, "error": f"variant must be one of {', '.join(VARIANTS)}"}
    proc = subprocess.run(
        [sys.executable, str(root / "cad" / "freecad" / "drive.py"), variant],
        cwd=str(root),
        env=child_env(root=root),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    log = clip((proc.stdout or "") + (proc.stderr or ""))
    payload = {"ok": proc.returncode == 0, "variant": variant, "code": proc.returncode, "log": log}
    receipts.add("cad_build", payload)
    return payload


def cad_thermal(root: Path, receipts: Receipts, timeout_s: float = 600) -> dict:
    proc = subprocess.run(
        [sys.executable, str(root / "cad" / "freecad" / "thermal_fea.py")],
        cwd=str(root),
        env=child_env(root=root),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    payload = {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "log": clip((proc.stdout or "") + (proc.stderr or "")),
        "note": "runs the slab check, then both walls and both grips; writes thermal-fea.json",
    }
    receipts.add("cad_thermal", payload)
    return payload


def cad_interference(root: Path, variant: str, receipts: Receipts, timeout_s: float = 180) -> dict:
    if variant not in VARIANTS:
        return {"ok": False, "error": f"variant must be one of {', '.join(VARIANTS)}"}
    command = freecad_command()
    if not command:
        payload = {
            "ok": False,
            "available": False,
            "variant": variant,
            "error": "freecadcmd is not installed; no overlap volume was computed",
        }
        receipts.add("cad_interference", payload)
        return payload
    fcstd = root / "design" / "variants" / variant / f"{variant}.FCStd"
    if not fcstd.is_file():
        payload = {"ok": False, "available": True, "variant": variant, "error": f"missing {fcstd.name}"}
        receipts.add("cad_interference", payload)
        return payload
    tools = str(root / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    from freecad_mcp.headless import run_headless

    code = _interference_code(fcstd, variant)
    result = run_headless(code, timeout=timeout_s, command=command)
    output = result.get("output") or ""
    parsed = _parse_interference(output)
    payload = {
        "ok": bool(result.get("success")) and parsed is not None and not parsed.get("unintended"),
        "available": True,
        "variant": variant,
        "log": clip(output),
        "error": result.get("error"),
        "report": parsed,
    }
    receipts.add("cad_interference", payload)
    return payload


def _interference_code(fcstd: Path, variant: str) -> str:
    return f"""
import json
import FreeCAD as App
doc = App.openDocument({str(fcstd)!r})
shapes = []
for obj in doc.Objects:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        continue
    try:
        null = shape.isNull()
        volume = float(shape.Volume)
    except Exception:
        continue
    if null or volume <= 1.0:
        continue
    shapes.append((obj.Name, shape))
pairs = []
for i in range(len(shapes)):
    for j in range(i + 1, len(shapes)):
        common = shapes[i][1].common(shapes[j][1])
        try:
            overlap = float(common.Volume) if common and not common.isNull() else 0.0
        except Exception:
            overlap = 0.0
        if overlap >= 1.0:
            pairs.append({{"a": shapes[i][0], "b": shapes[j][0], "overlap_mm3": round(overlap, 4)}})
print("INTERFERENCE_JSON " + json.dumps({{"variant": {variant!r}, "solids": len(shapes), "pairs": pairs}}))
"""


def _parse_interference(output: str) -> dict | None:
    for line in output.splitlines():
        if line.startswith("INTERFERENCE_JSON "):
            report = json.loads(line[len("INTERFERENCE_JSON ") :])
            unintended = []
            intended = []
            for pair in report.get("pairs") or []:
                names = (pair.get("a", "") + " " + pair.get("b", "")).lower()
                if any(token in names for token in INTENDED_PAIR):
                    intended.append(pair)
                else:
                    unintended.append(pair)
            report["intended_press"] = intended
            report["unintended"] = unintended
            return report
    return None


def cad_render(
    root: Path,
    kind: str,
    variant: str,
    finish: str | None,
    script: str | None,
    output: str | None,
    receipts: Receipts,
    timeout_s: float = 300,
) -> dict:
    if kind == "ga":
        return _render_ga(root, variant, receipts)
    if kind == "colored":
        return {"ok": False, "error": "colored STL shading is design/tailgate/drawings/render_colored.py; use kind blender for a textured finish"}
    if kind != "blender":
        return {"ok": False, "error": "kind must be ga or blender"}
    if variant not in VARIANTS:
        return {"ok": False, "error": f"variant must be one of {', '.join(VARIANTS)}"}
    if finish not in FINISHES:
        return {"ok": False, "error": f"finish must be one of {', '.join(FINISHES)}"}
    if not script or not output:
        return {"ok": False, "error": "blender render needs script and output paths inside the repo"}
    if shutil.which("blender") is None:
        payload = {"ok": False, "available": False, "kind": "blender", "error": "blender is not on PATH"}
        receipts.add("cad_render", payload)
        return payload
    try:
        script_path = resolve_in_repo(root, script)
        output_path = resolve_in_repo(root, output)
    except Exception as exc:  # SandboxError
        return {"ok": False, "error": str(exc)}
    if script_path.suffix != ".py" or not script_path.is_file():
        return {"ok": False, "error": "script must be an existing .py file inside the repo"}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["blender", "--background", "--python", str(script_path), "--", str(output_path)],
        cwd=str(root),
        env=child_env(root=root),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    exists = output_path.is_file() and output_path.stat().st_size > 0
    payload = {
        "ok": proc.returncode == 0 and exists,
        "available": True,
        "kind": "blender",
        "variant": variant,
        "finish": finish,
        "output": output,
        "script": script,
        "code": proc.returncode,
        "bytes": output_path.stat().st_size if output_path.is_file() else 0,
        "log": clip((proc.stdout or "") + (proc.stderr or "")),
    }
    receipts.add("cad_render", payload)
    return payload


def _render_ga(root: Path, variant: str, receipts: Receipts) -> dict:
    if variant not in VARIANTS:
        return {"ok": False, "error": f"variant must be one of {', '.join(VARIANTS)}"}
    folder = root / "design" / "variants" / variant
    files = []
    for name in ("front", "side", "top", "section"):
        path = folder / f"{name}.png"
        files.append(
            {
                "name": name,
                "exists": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else 0,
            }
        )
    payload = {
        "ok": all(item["exists"] and item["bytes"] > 0 for item in files),
        "kind": "ga",
        "variant": variant,
        "files": files,
        "note": "These PNGs are written by cad/freecad/build_variant.py during cad_build. This call only reports them.",
    }
    receipts.add("cad_render", payload)
    return payload


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def check(task: dict, root: Path, receipts: Receipts) -> dict:
    """Run the task acceptance block. ok is true only when every predicate passes."""
    acceptance = task["acceptance"]
    failures: list[str] = []
    measured: dict = {}

    if "png" in acceptance:
        failures.extend(_check_png(root, acceptance["png"], measured))
    if "manifest" in acceptance:
        failures.extend(_check_manifest(root, acceptance["manifest"], measured))
    if acceptance.get("render_receipt"):
        failures.extend(_check_render_receipt(acceptance["render_receipt"], receipts, measured))
    if "mass_gate" in acceptance:
        failures.extend(_check_mass(root, acceptance["mass_gate"], receipts, measured))
    if "markdown" in acceptance:
        failures.extend(_check_markdown(root, acceptance["markdown"], receipts, measured))
    if "template" in acceptance:
        failures.extend(_check_template(root, acceptance["template"], measured))
    if acceptance.get("unittest"):
        unit = _run_unittest(root, str(acceptance["unittest"]))
        measured["unittest"] = unit
        if unit["status"] == "fail":
            failures.append("unittest failed: " + unit.get("output", "")[:300])
    if acceptance.get("interference"):
        failures.extend(_check_interference(root, acceptance["interference"], receipts, measured))

    return {"ok": not failures, "failures": failures, "measured": measured}


def _check_png(root: Path, spec: dict, measured: dict) -> list[str]:
    relative = spec["path"]
    path = root / relative
    if not path.is_file():
        return [f"png missing: {relative}"]
    size = png_size(path)
    bytes_on_disk = path.stat().st_size
    measured["png"] = {"path": relative, "bytes": bytes_on_disk, "size": size}
    failures = []
    if size is None:
        failures.append(f"png header is not a PNG: {relative}")
        return failures
    if size[0] < int(spec["min_width"]) or size[1] < int(spec["min_height"]):
        failures.append(f"png is {size[0]}x{size[1]}, need {spec['min_width']}x{spec['min_height']}")
    if bytes_on_disk < int(spec["min_bytes"]):
        failures.append(f"png is {bytes_on_disk} bytes, need {spec['min_bytes']}")
    return failures


def _check_manifest(root: Path, spec: dict, measured: dict) -> list[str]:
    relative = spec["path"]
    path = root / relative
    if not path.is_file():
        return [f"manifest missing: {relative}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [f"manifest is not JSON: {relative}"]
    failures = []
    for key, expected in (spec.get("equals") or {}).items():
        if payload.get(key) != expected:
            failures.append(f"manifest {key} is {payload.get(key)!r}, need {expected!r}")
    for key in spec.get("path_keys") or []:
        target = payload.get(key)
        if not isinstance(target, str) or not (root / target).is_file():
            failures.append(f"manifest {key} is not an existing repo file")
    for key in spec.get("path_map_keys") or []:
        mapping = payload.get(key)
        if not isinstance(mapping, dict) or not mapping:
            failures.append(f"manifest {key} must be a non-empty map of files")
            continue
        for name, target in mapping.items():
            if not isinstance(target, str) or not (root / target).is_file():
                failures.append(f"manifest {key}.{name} is not an existing repo file")
    measured["manifest"] = {"path": relative, "keys": sorted(payload.keys())}
    return failures


def _check_render_receipt(spec: dict, receipts: Receipts, measured: dict) -> list[str]:
    receipt = receipts.find(
        "cad_render",
        ok=True,
        kind="blender",
        variant=spec["variant"],
        finish=spec["finish"],
        output=spec["output"],
    )
    measured["render_receipt"] = bool(receipt)
    if receipt is None:
        return ["no successful cad_render blender receipt for this output in this session"]
    return []


def _check_mass(root: Path, spec: dict, receipts: Receipts, measured: dict) -> list[str]:
    failures = []
    results = {}
    for variant in spec["variants"]:
        try:
            measured_variant = evaluate_variant(root, variant)
        except Exception as exc:
            failures.append(f"{variant} evaluate failed: {exc}")
            continue
        results[variant] = {key: measured_variant[key] for key in ("ready_kg", "wall_outer_C", "grip_C", "under_C")}
        ready = float(measured_variant["ready_kg"])
        if ready > float(spec["max_ready_kg"]) or ready < float(spec["min_ready_kg"]):
            failures.append(f"{variant} ready_kg {ready:.3f} is outside {spec['min_ready_kg']}..{spec['max_ready_kg']}")
        if float(measured_variant["under_C"]) > float(spec["max_under_C"]):
            failures.append(f"{variant} under_C {measured_variant['under_C']}")
        if float(measured_variant["grip_C"]) > float(spec["max_grip_C"]):
            failures.append(f"{variant} grip_C {measured_variant['grip_C']}")
        if measured_variant["skin"] == "blackwood":
            if float(measured_variant["wall_outer_C"]) > float(spec["max_wood_outer_C"]):
                failures.append(f"{variant} wood skin {measured_variant['wall_outer_C']}")
            if float(measured_variant["wall_inner_face_C"]) > float(spec["max_wood_inner_C"]):
                failures.append(f"{variant} wood inner face {measured_variant['wall_inner_face_C']}")
        elif float(measured_variant["wall_outer_C"]) > float(spec["max_metal_outer_C"]):
            failures.append(f"{variant} metal skin {measured_variant['wall_outer_C']}")
        if float(measured_variant["pizza_clearance"]) < float(spec["min_pizza_clearance"]):
            failures.append(f"{variant} pizza clearance {measured_variant['pizza_clearance']}")
        outer = float(measured_variant["outer_diameter"])
        if outer < float(spec["min_outer_diameter"]) or outer > float(spec["max_outer_diameter"]):
            failures.append(f"{variant} outer diameter {outer}")
        if float(measured_variant["body_height"]) > float(spec["max_body_height"]):
            failures.append(f"{variant} body height {measured_variant['body_height']}")
        solid = root / "design" / "variants" / variant / "freecad-mass.json"
        if not solid.is_file():
            failures.append(f"missing FreeCAD mass report for {variant}")
        else:
            report = json.loads(solid.read_text(encoding="utf-8"))
            analytical = ready - BURNER_KG
            if abs(float(report["freecad_kg"]) - analytical) > float(spec["freecad_tolerance_kg"]):
                failures.append(
                    f"{variant} FreeCAD {report['freecad_kg']} kg is more than "
                    f"{spec['freecad_tolerance_kg']} kg from analytical {analytical:.3f} kg"
                )
            if float(report["ready_with_burner_kg"]) > float(spec["max_ready_kg"]):
                failures.append(f"{variant} FreeCAD ready mass {report['ready_with_burner_kg']}")
    measured["mass"] = results
    record_path = root / spec["record"]
    variant = spec["record_variant"]
    if not record_path.is_file():
        failures.append(f"iteration record missing: {spec['record']}")
    else:
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            failures.append("iteration record is not JSON")
            record = {}
        if record.get("variant") != variant:
            failures.append(f"iteration record variant is {record.get('variant')!r}")
        if not str(record.get("parameter") or "").strip():
            failures.append("iteration record needs a parameter name")
        if record.get("decision") not in ("kept", "changed", "rejected"):
            failures.append("iteration record decision must be kept, changed, or rejected")
        expected = results.get(variant, {}).get("ready_kg")
        if expected is not None and abs(float(record.get("ready_kg", -1)) - float(expected)) > float(spec["record_tolerance_kg"]):
            failures.append(
                f"iteration ready_kg {record.get('ready_kg')} does not match evaluate() {expected}"
            )
    if receipts.find("cad_mass", ok=True, mode="evaluate", variant=variant) is None:
        failures.append(f"cad_mass evaluate was not run for {variant} in this session")
    return failures


def _check_markdown(root: Path, spec: dict, receipts: Receipts, measured: dict) -> list[str]:
    path = root / spec["path"]
    if not path.is_file():
        return [f"missing {spec['path']}"]
    text = path.read_text(encoding="utf-8")
    failures = []
    for heading in spec.get("headings") or []:
        if not _has_heading(text, heading):
            failures.append(f"BUILD doc is missing a heading {heading}")
    variant = spec["contains_mass_of"]
    measured_variant = evaluate_variant(root, variant)
    mass_text = f"{measured_variant['ready_kg']:.2f}"
    stone_text = str(int(round(measured_variant["stone_d"])))
    measured["markdown"] = {"mass_text": mass_text, "stone_d": stone_text}
    if mass_text not in text:
        failures.append(f"{spec['path']} must contain the measured ready mass {mass_text}")
    if stone_text not in text:
        failures.append(f"{spec['path']} must contain the stone diameter {stone_text}")
    if spec.get("require_cad_mass") and receipts.find("cad_mass", ok=True, mode="evaluate", variant=variant) is None:
        failures.append(f"cad_mass evaluate was not run for {variant} in this session")
    return failures


def _has_heading(text: str, heading: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            words = stripped.lstrip("#").strip()
            if words.lower() == heading.lower():
                return True
    return False


def _check_template(root: Path, spec: dict, measured: dict) -> list[str]:
    folder = root / spec["dir"]
    suffixes = tuple(spec.get("suffixes") or [".svg", ".dxf"])
    found = []
    if folder.is_dir():
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() in suffixes and path.stat().st_size >= int(spec["min_bytes"]):
                text = path.read_text(encoding="utf-8", errors="replace")
                if "CUT" in text and str(spec.get("must_contain", "420")) in text:
                    found.append(path.name)
    measured["templates"] = found
    if not found:
        return [
            f"no {suffixes} template under {spec['dir']} with CUT, "
            f"{spec.get('must_contain', '420')}, and at least {spec['min_bytes']} bytes"
        ]
    return []


def _check_interference(root: Path, spec: dict, receipts: Receipts, measured: dict) -> list[str]:
    variant = spec["variant"]
    if freecad_available():
        live = cad_interference(root, variant, receipts)
        report = (live.get("report") or {})
        measured["interference"] = {"available": True, "unintended": len(report.get("unintended") or [])}
        if report.get("unintended"):
            return [f"unintended interference pairs: {report['unintended'][:5]}"]
        if not live.get("ok"):
            return [f"interference gate did not pass: {live.get('error') or 'no report'}"]
        return []
    receipt = receipts.find("cad_interference", variant=variant, available=False)
    measured["interference"] = {"available": False, "called": receipt is not None}
    if receipt is None:
        return ["cad_interference was not called, and freecadcmd is not installed"]
    return []


def _run_unittest(root: Path, module: str) -> dict:
    try:
        import scipy  # noqa: F401
    except ImportError:
        return {"status": "skipped", "reason": "scipy is not installed"}
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", module],
        cwd=str(root),
        env=child_env(root=root),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    output = clip((proc.stdout or "") + (proc.stderr or ""), 2000)
    return {"status": "pass" if proc.returncode == 0 else "fail", "output": output}

