"""Drive FreeCAD through the freecad-mcp headless runner.

The runner is ``tools/freecad_mcp/headless.py``, the ``execute_code_headless``
path from https://github.com/neka-nat/freecad-mcp. It shells out to
``freecadcmd`` so a native crash stays in the helper process. Set
``FREECADCMD`` to the FreeCAD command on a Mac (``FreeCADCmd`` from the
application bundle). The default below is the Linux build used to generate
the files in this checkout.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from freecad_mcp.headless import run_headless  # noqa: E402

DEFAULT_CMD = "/tmp/freecad-dl/squashfs-root/usr/bin/freecadcmd"


def run_variant(name: str, timeout: float = 180.0) -> dict:
    command = [os.environ.get("FREECADCMD", DEFAULT_CMD)]
    code = (
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from cad.freecad.build_variant import build\n"
        f"build({name!r})\n"
    )
    result = run_headless(code, timeout=timeout, command=command)
    print(result.get("output", ""))
    if not result.get("success"):
        raise RuntimeError(result.get("error") or "freecad-mcp headless run failed")
    return result


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "morning"
    run_variant(target)
