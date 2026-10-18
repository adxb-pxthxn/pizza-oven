"""The web mesh writer packs a triangle a browser can open."""

from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

from cad.freecad.web_mesh import write_glb, write_stl


def _triangle() -> list[dict]:
    return [{
        "name": "pad",
        "kind": "ss",
        "crown": False,
        "vertices": [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 0.0, 5.0)],
        "triangles": [(0, 1, 2)],
    }]


class WebMeshTest(unittest.TestCase):
    def test_glb_is_y_up_metres_and_stl_stays_in_millimetres(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            glb = root / "pad.glb"
            stl = root / "pad.stl"
            self.assertEqual(write_glb(glb, _triangle()), 1)
            self.assertEqual(write_stl(stl, _triangle()), 1)
            data = glb.read_bytes()
            self.assertEqual(data[:4], b"glTF")
            length = struct.unpack_from("<I", data, 8)[0]
            self.assertEqual(length, len(data))
            json_len = struct.unpack_from("<I", data, 12)[0]
            document = json.loads(data[20:20 + json_len])
            accessor = document["accessors"][0]
            # FreeCAD (0, 0, 5 mm) becomes glTF (0, 0.005 m, 0).
            self.assertAlmostEqual(accessor["max"][1], 0.005)
            self.assertEqual(document["meshes"][0]["name"], "pad")
            self.assertEqual(struct.unpack_from("<I", stl.read_bytes(), 80)[0], 1)


if __name__ == "__main__":
    unittest.main()
