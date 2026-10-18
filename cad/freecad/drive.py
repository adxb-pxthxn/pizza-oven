"""Drive FreeCAD through the freecad-mcp headless runner or directly via freecadcmd.

The runner is ``tools/freecad_mcp/headless.py`` when present, or a direct
subprocess call to ``freecadcmd`` so a native crash stays in the helper process.
Set ``FREECADCMD`` to the FreeCAD command on a Mac (``FreeCADCmd`` from the
application bundle). The default below is the Linux build used to generate
the files in this checkout.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

try:
    from freecad_mcp.headless import run_headless  # type: ignore[import-not-found]
except ImportError:
    run_headless = None

DEFAULT_CMD = "/tmp/freecad-dl/squashfs-root/usr/bin/freecadcmd"


def _fallback_headless(code: str, timeout: float, command: list[str]) -> dict:
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    proc = subprocess.run(
        [*command, "-c", code],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return {
        "success": proc.returncode == 0,
        "output": output,
        "error": None if proc.returncode == 0 else f"freecadcmd exited with {proc.returncode}: {output}",
    }


def run_variant(name: str, timeout: float = 180.0) -> dict:
    command = [os.environ.get("FREECADCMD", DEFAULT_CMD)]
    code = (
        "import sys\n"
        "sys.path = [p for p in sys.path if 'dist-packages' not in p] + [" + repr(str(ROOT)) + "]\n"
        "from cad.freecad.build_variant import build\n"
        f"build({name!r})\n"
    )
    runner = run_headless if run_headless is not None else _fallback_headless
    result = runner(code, timeout=timeout, command=command)
    print(result.get("output", ""))
    if not result.get("success"):
        raise RuntimeError(result.get("error") or "freecad-mcp headless run failed")
    return result


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "morning"
    run_variant(target)