"""STL and glTF binary meshes for a web viewer.

STL stays in millimetres, Z up, the same frame as the STEP file.
glTF is metres and Y up, which is what a browser viewer expects.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

# base color, metallic, roughness
COLORS = {
    "ss": ((0.72, 0.74, 0.76), 0.9, 0.35),
    "al": ((0.78, 0.80, 0.82), 0.85, 0.40),
    "brass": ((0.74, 0.57, 0.27), 0.85, 0.32),
    "jarrah": ((0.45, 0.24, 0.14), 0.0, 0.72),
    "blackwood": ((0.25, 0.16, 0.10), 0.0, 0.68),
    "cordierite": ((0.86, 0.80, 0.68), 0.0, 0.85),
    "micro": ((0.91, 0.86, 0.68), 0.0, 0.92),
    "ptfe": ((0.93, 0.93, 0.90), 0.0, 0.42),
    "rubber": ((0.10, 0.10, 0.10), 0.0, 0.82),
}
_GRAY = ((0.6, 0.6, 0.6), 0.1, 0.6)


def _gltf_vertex(x: float, y: float, z: float, scale: float) -> tuple[float, float, float]:
    """FreeCAD millimetres, Z up, to glTF metres, Y up."""
    return (x * scale, z * scale, -y * scale)


def write_stl(path: Path, meshes: list[dict], *, z_lift: float = 0.0) -> int:
    """Binary STL in millimetres. Crown parts rise by z_lift when it is set."""
    triangles = 0
    body = bytearray()
    for mesh in meshes:
        lift = z_lift if mesh.get("crown") and z_lift else 0.0
        vertices = mesh["vertices"]
        for i0, i1, i2 in mesh["triangles"]:
            p0 = vertices[i0]
            p1 = vertices[i1]
            p2 = vertices[i2]
            body += struct.pack(
                "<12fH",
                0.0, 0.0, 0.0,
                p0[0], p0[1], p0[2] + lift,
                p1[0], p1[1], p1[2] + lift,
                p2[0], p2[1], p2[2] + lift,
                0,
            )
            triangles += 1
    header = b"Angas variant mesh, millimetres, Z up".ljust(80, b"\0")
    path.write_bytes(header + struct.pack("<I", triangles) + body)
    return triangles


def write_glb(path: Path, meshes: list[dict], *, scale: float = 0.001, z_lift: float = 0.0) -> int:
    """One glTF binary. Each part is its own node so a viewer can show it."""
    kinds = []
    for mesh in meshes:
        if mesh["kind"] not in kinds:
            kinds.append(mesh["kind"])
    materials = []
    for kind in kinds:
        color, metallic, roughness = COLORS.get(kind, _GRAY)
        materials.append({
            "name": kind,
            "pbrMetallicRoughness": {
                "baseColorFactor": [color[0], color[1], color[2], 1.0],
                "metallicFactor": metallic,
                "roughnessFactor": roughness,
            },
        })

    blob = bytearray()
    buffer_views = []
    accessors = []
    gltf_meshes = []
    nodes = []
    triangles = 0

    def _view(data: bytes, target: int) -> int:
        while len(blob) % 4:
            blob.append(0)
        start = len(blob)
        blob.extend(data)
        buffer_views.append({"buffer": 0, "byteOffset": start, "byteLength": len(data), "target": target})
        return len(buffer_views) - 1

    for mesh in meshes:
        lift = z_lift if mesh.get("crown") and z_lift else 0.0
        raw_vertices = mesh["vertices"]
        raw_triangles = mesh["triangles"]
        if not raw_vertices or not raw_triangles:
            continue
        positions = []
        for x, y, z in raw_vertices:
            positions.extend(_gltf_vertex(x, y, z + lift, scale))
        indices = [index for tri in raw_triangles for index in tri]
        pos_bytes = struct.pack(f"<{len(positions)}f", *positions)
        idx_bytes = struct.pack(f"<{len(indices)}I", *indices)
        pos_view = _view(pos_bytes, 34962)
        idx_view = _view(idx_bytes, 34963)
        xs = positions[0::3]
        ys = positions[1::3]
        zs = positions[2::3]
        pos_accessor = len(accessors)
        accessors.append({
            "bufferView": pos_view,
            "componentType": 5126,
            "count": len(raw_vertices),
            "type": "VEC3",
            "min": [min(xs), min(ys), min(zs)],
            "max": [max(xs), max(ys), max(zs)],
        })
        idx_accessor = len(accessors)
        accessors.append({
            "bufferView": idx_view,
            "componentType": 5125,
            "count": len(indices),
            "type": "SCALAR",
        })
        mesh_index = len(gltf_meshes)
        gltf_meshes.append({
            "name": mesh["name"],
            "primitives": [{
                "attributes": {"POSITION": pos_accessor},
                "indices": idx_accessor,
                "material": kinds.index(mesh["kind"]),
            }],
        })
        nodes.append({"name": mesh["name"], "mesh": mesh_index})
        triangles += len(raw_triangles)

    if not nodes:
        raise ValueError("no triangles to write")
    root = {"name": path.stem, "children": list(range(len(nodes)))}
    document = {
        "asset": {"version": "2.0", "generator": "cad.freecad.web_mesh"},
        "scene": 0,
        "scenes": [{"nodes": [len(nodes)]}],
        "nodes": nodes + [root],
        "meshes": gltf_meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(blob)}],
    }
    payload = json.dumps(document, separators=(",", ":")).encode("utf-8")
    while len(payload) % 4:
        payload += b" "
    while len(blob) % 4:
        blob.append(0)
    header = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(payload) + 8 + len(blob))
    json_chunk = struct.pack("<II", len(payload), 0x4E4F534A) + payload
    bin_chunk = struct.pack("<II", len(blob), 0x004E4942) + blob
    path.write_bytes(header + json_chunk + bin_chunk)
    return triangles


def collect_triangles(parts: list[tuple], deflection: float = 0.8) -> list[dict]:
    """Tessellate FreeCAD shapes. parts are (name, kind, crown, shape)."""
    collected = []
    for name, kind, crown, shape in parts:
        points, facets = shape.tessellate(deflection)
        collected.append({
            "name": name,
            "kind": kind,
            "crown": crown,
            "vertices": [(point.x, point.y, point.z) for point in points],
            "triangles": [tuple(facet) for facet in facets],
        })
    return collected


def export_view_meshes(out_dir: Path, stem: str, parts: list[tuple], explode_lift: float) -> None:
    """Write stem.stl, stem.glb, and stem-exploded.glb beside the STEP files."""
    meshes = collect_triangles(parts)
    stl_path = out_dir / f"{stem}.stl"
    glb_path = out_dir / f"{stem}.glb"
    exploded_path = out_dir / f"{stem}-exploded.glb"
    write_stl(stl_path, meshes)
    write_glb(glb_path, meshes)
    write_glb(exploded_path, meshes, z_lift=explode_lift)
    print("MESH", stl_path, glb_path, exploded_path)
