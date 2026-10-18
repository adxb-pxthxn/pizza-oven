"""Steady conduction check: Gmsh mesh, CalculiX solve.

A homogeneous slab is solved first and compared with the 1D resistance sum.
Each variant then gets the same treatment on its wall stack, and a separate
handle model with the posts rooted at the skin temperature the wall solve
just produced. Geometry is in metres. Films use h = 25 on the gas side and
h = 10 on the air side, the same pair as the mass model.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import gmsh

from cad.freecad.masslib import T_AMB, T_GAS, Design, evaluate

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str) -> Design:
    payload = json.loads((ROOT / "design" / "variants" / "optimizer.json").read_text(encoding="utf-8"))
    raw = payload[name]["design"]
    raw["ins_t"] = math.ceil(raw["ins_t"] * 10.0 - 1e-9) / 10.0
    raw["floor_ins"] = math.ceil(raw["floor_ins"] * 10.0 - 1e-9) / 10.0
    for key in ("liner_t", "skin_t", "base_t", "pan_t", "stone_t", "stone_d", "band_t", "band_w", "standoff"):
        raw[key] = round(float(raw[key]), 2)
    return Design(**raw)
CCX = Path("/tmp/freecad-dl/squashfs-root/usr/bin/ccx")
# CalculiX tet faces, 0-based indices into the four nodes. Same order as C3D4.
TET_FACES = ((0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0))
FACE_LABEL = {0: "F1", 1: "F2", 2: "F3", 3: "F4"}


def _resistance_slab(thickness: float, k: float) -> float:
    total = 1.0 / 25.0 + thickness / k + 1.0 / 10.0
    flux = (T_GAS - T_AMB) / total
    return T_AMB + flux / 10.0


def _mesh_layers(layers: list[tuple[str, float, float]], size: dict[str, float]) -> dict:
    """Stack boxes along Z. layers are (name, thickness_m, k)."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("stack")
    occ = gmsh.model.occ
    z = 0.0
    volumes = []
    for name, thick, _k in layers:
        tag = occ.addBox(0.0, 0.0, z, 0.02, 0.02, thick)
        volumes.append((name, tag, z, z + thick))
        z += thick
    occ.fragment([(3, volumes[0][1])], [(3, item[1]) for item in volumes[1:]])
    occ.synchronize()
    # After fragment, volumes are rebuilt. Match them by their centre z.
    rebuilt = []
    for dim, tag in gmsh.model.getEntities(3):
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        centre = 0.5 * (zmin + zmax)
        name, _old, _z0, _z1 = min(volumes, key=lambda item: abs(0.5 * (item[2] + item[3]) - centre))
        rebuilt.append((name, tag, zmin, zmax))
        gmsh.model.addPhysicalGroup(3, [tag], tag)
        gmsh.model.setPhysicalName(3, tag, name)
        length = size[name]
        for _d, point in gmsh.model.getBoundary([(3, tag)], recursive=True):
            if _d == 0:
                gmsh.model.mesh.setSize([(0, point)], length)
    z_top = max(item[3] for item in rebuilt)
    gmsh.model.mesh.generate(3)
    nodes = _nodes()
    elements = _tets()
    payload = {
        "nodes": nodes,
        "elements": elements,
        "volumes": rebuilt,
        "z_top": z_top,
        "z_bottom": 0.0,
    }
    gmsh.finalize()
    return payload


def _nodes() -> dict[int, tuple[float, float, float]]:
    tags, coords, _ = gmsh.model.mesh.getNodes()
    out = {}
    for index, tag in enumerate(tags):
        out[int(tag)] = tuple(coords[3 * index: 3 * index + 3])
    return out


def _tets() -> list[tuple[int, tuple[int, int, int, int]]]:
    types, _tags, nodes = gmsh.model.mesh.getElements(3)
    found = []
    for elem_type, conn in zip(types, nodes):
        if elem_type != 4:
            continue
        for offset in range(0, len(conn), 4):
            found.append((len(found) + 1, tuple(int(conn[offset + i]) for i in range(4))))
    if not found:
        raise RuntimeError("Gmsh produced no 4-node tets")
    return found


def _write_and_solve(mesh: dict, materials: dict[str, float], films: list[tuple[str, float, float]], work: Path) -> dict[int, float]:
    """films: (which, sink C, h). which is 'bottom' or 'top'."""
    work.mkdir(parents=True, exist_ok=True)
    lines = ["*NODE"]
    for tag, (x, y, z) in sorted(mesh["nodes"].items()):
        lines.append(f"{tag}, {x:.8e}, {y:.8e}, {z:.8e}")
    by_volume: dict[str, list[int]] = {name: [] for name, *_rest in mesh["volumes"]}
    # Re-tag elements by the mean z of their nodes against volume bands.
    volume_of_element: dict[int, str] = {}
    for eid, nids in mesh["elements"]:
        z = sum(mesh["nodes"][nid][2] for nid in nids) / 4.0
        name = min(mesh["volumes"], key=lambda item: 0.0 if item[2] - 1e-9 <= z <= item[3] + 1e-9 else 1e9)
        # min with a key that is 0 inside the band
        inside = [item for item in mesh["volumes"] if item[2] - 1e-8 <= z <= item[3] + 1e-8]
        if not inside:
            raise RuntimeError(f"tet {eid} at z={z} is outside every layer")
        name = inside[0][0]
        volume_of_element[eid] = name
        by_volume[name].append(eid)
    lines.append("*ELEMENT, TYPE=DC3D4, ELSET=ALL")
    for eid, nids in mesh["elements"]:
        lines.append(f"{eid}, {nids[0]}, {nids[1]}, {nids[2]}, {nids[3]}")
    for name, eids in by_volume.items():
        if not eids:
            continue
        lines.append(f"*ELSET, ELSET={name}")
        for chunk_start in range(0, len(eids), 12):
            lines.append(", ".join(str(eid) for eid in eids[chunk_start:chunk_start + 12]))
        lines.append(f"*SOLID SECTION, ELSET={name}, MATERIAL={name}")
        lines.append(f"*MATERIAL, NAME={name}")
        lines.append("*CONDUCTIVITY")
        lines.append(f"{materials[name]:.6e}")
    lines.append("*INITIAL CONDITIONS, TYPE=TEMPERATURE")
    lines.append("Nall, 20")
    lines.append("*NSET, NSET=Nall, GENERATE")
    lo = min(mesh["nodes"])
    hi = max(mesh["nodes"])
    lines.append(f"{lo}, {hi}, 1")
    lines.append("*STEP")
    lines.append("*HEAT TRANSFER, STEADY STATE")
    lines.append("*FILM")
    tol = 1e-5
    for eid, nids in mesh["elements"]:
        coords = [mesh["nodes"][nid] for nid in nids]
        for face_index, local in enumerate(TET_FACES):
            zs = [coords[i][2] for i in local]
            if all(abs(z - mesh["z_bottom"]) < tol for z in zs):
                which = "bottom"
            elif all(abs(z - mesh["z_top"]) < tol for z in zs):
                which = "top"
            else:
                continue
            for label, sink, coeff in films:
                if label == which:
                    lines.append(f"{eid}, {FACE_LABEL[face_index]}, {sink:.2f}, {coeff:.4f}")
    lines.append("*NODE FILE")
    lines.append("NT")
    lines.append("*END STEP")
    inp = work / "job.inp"
    inp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run = subprocess.run([str(CCX), "-i", "job"], cwd=work, capture_output=True, text=True)
    if run.returncode != 0 or not (work / "job.frd").exists():
        raise RuntimeError((run.stdout or "")[-1500:] + (run.stderr or "")[-800:])
    return _read_frd(work / "job.frd")


def _read_frd(path: Path) -> dict[int, float]:
    """CalculiX 2.23 writes temperatures as '-1 <node> <temp>' after an NDTEMP card."""
    temps: dict[int, float] = {}
    reading = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "NDTEMP" in line:
            reading = True
            continue
        if not reading:
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "-1":
            temps[int(parts[1])] = float(parts[2])
        elif temps and parts and parts[0] == "-3":
            break
    if not temps:
        raise RuntimeError(f"no temperatures in {path}")
    return temps


def _face_mean(mesh: dict, temps: dict[int, float], z_value: float) -> float:
    values = [
        temp for tag, temp in temps.items()
        if tag in mesh["nodes"] and abs(mesh["nodes"][tag][2] - z_value) < 1e-5
    ]
    if not values:
        raise RuntimeError(f"no nodes on z={z_value}")
    return sum(values) / len(values)


def slab_check(work: Path) -> dict:
    layers = [("board", 0.030, 0.030)]
    mesh = _mesh_layers(layers, {"board": 0.004})
    temps = _write_and_solve(mesh, {"board": 0.030}, [("bottom", T_GAS, 25.0), ("top", T_AMB, 10.0)], work)
    outer = _face_mean(mesh, temps, mesh["z_top"])
    expected = _resistance_slab(0.030, 0.030)
    return {"outer_C": round(outer, 2), "expected_C": round(expected, 2), "error_C": round(outer - expected, 2)}


def wall_check(name: str, work: Path) -> dict:
    design = _load(name)
    report = evaluate(design)
    if design.skin == "blackwood":
        layers = [
            ("liner", design.liner_t / 1000.0, 16.0),
            ("board", design.ins_t / 1000.0, 0.030),
            ("skin", design.skin_t / 1000.0, 0.16),
        ]
        sizes = {"liner": 0.0004, "board": 0.004, "skin": 0.002}
    else:
        layers = [
            ("liner", design.liner_t / 1000.0, 16.0),
            ("board", design.ins_t / 1000.0, 0.030),
            ("skin", design.skin_t / 1000.0, 160.0),
        ]
        sizes = {"liner": 0.0004, "board": 0.004, "skin": 0.0005}
    mesh = _mesh_layers(layers, sizes)
    materials = {item[0]: item[2] for item in layers}
    temps = _write_and_solve(
        mesh, materials, [("bottom", T_GAS, 25.0), ("top", T_AMB, 10.0)], work,
    )
    outer = _face_mean(mesh, temps, mesh["z_top"])
    return {
        "dragon": design.dragon,
        "outer_C": round(outer, 2),
        "oned_C": round(report["wall_outer_C"], 2),
        "error_C": round(outer - report["wall_outer_C"], 2),
        "elements": len(mesh["elements"]),
    }


def handle_check(name: str, skin_c: float, work: Path) -> dict:
    """One jarrah bar, two stainless posts, two PTFE washers. Root nodes held at the skin temperature."""
    design = _load(name)
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("handle")
    occ = gmsh.model.occ
    # Grip along Y. Posts along X, from the root toward the bar.
    grip = occ.addBox(0.016, 0.0, -0.011, 0.022, 0.130, 0.022)
    posts = []
    washers = []
    for y in (0.045, 0.085):
        posts.append(occ.addBox(0.0, y - 0.003, -0.003, 0.016, 0.006, 0.006))
        washers.append(occ.addBox(0.013, y - 0.008, -0.008, 0.003, 0.016, 0.016))
    occ.fragment([(3, grip)], [(3, tag) for tag in posts + washers])
    occ.synchronize()
    volumes = []
    for dim, tag in gmsh.model.getEntities(3):
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        dx, dy, dz = xmax - xmin, ymax - ymin, zmax - zmin
        if dx > 0.02:
            kind = "grip"
            length = 0.004
        elif dx < 0.004 and dy < 0.018:
            kind = "washer"
            length = 0.0015
        else:
            kind = "post"
            length = 0.002
        volumes.append((kind, tag, xmin, xmax))
        for _d, point in gmsh.model.getBoundary([(3, tag)], recursive=True):
            if _d == 0:
                gmsh.model.mesh.setSize([(0, point)], length)
    gmsh.model.mesh.generate(3)
    mesh = {"nodes": _nodes(), "elements": _tets(), "volumes": [(k, t, 0.0, 1.0) for k, t, _a, _b in volumes], "z_top": 0.0, "z_bottom": 0.0}
    # Custom writer: conductivity by kind, Dirichlet on nodes with x < 1e-5 (the post roots), film on the grip surface.
    # Reuse the solver format by a dedicated writer.
    temps = _solve_handle(mesh, volumes, skin_c, work)
    grip_nodes = []
    for tag, (x, y, z) in mesh["nodes"].items():
        if x > 0.020 and tag in temps:
            grip_nodes.append(temps[tag])
    gmsh.finalize()
    if not grip_nodes:
        raise RuntimeError("handle mesh has no grip nodes")
    return {
        "dragon": design.dragon,
        "grip_C": round(sum(grip_nodes) / len(grip_nodes), 2),
        "grip_max_C": round(max(grip_nodes), 2),
        "oned_C": round(evaluate(design)["grip_C"], 2),
        "skin_root_C": round(skin_c, 2),
    }


def _solve_handle(mesh: dict, volumes: list, skin_c: float, work: Path) -> dict[int, float]:
    work.mkdir(parents=True, exist_ok=True)
    kind_of_tag = {tag: kind for kind, tag, _a, _b in volumes}
    # Element kind from its centre x.
    lines = ["*NODE"]
    for tag, (x, y, z) in sorted(mesh["nodes"].items()):
        lines.append(f"{tag}, {x:.8e}, {y:.8e}, {z:.8e}")
    kinds = {"grip": [], "post": [], "washer": []}
    for eid, nids in mesh["elements"]:
        x = sum(mesh["nodes"][nid][0] for nid in nids) / 4.0
        dx_span = max(mesh["nodes"][nid][0] for nid in nids) - min(mesh["nodes"][nid][0] for nid in nids)
        if x > 0.016:
            kind = "grip"
        elif dx_span < 0.004 and x > 0.012:
            kind = "washer"
        else:
            kind = "post"
        kinds[kind].append(eid)
    lines.append("*ELEMENT, TYPE=DC3D4, ELSET=ALL")
    for eid, nids in mesh["elements"]:
        lines.append(f"{eid}, {nids[0]}, {nids[1]}, {nids[2]}, {nids[3]}")
    k_of = {"grip": 0.16, "post": 16.0, "washer": 0.25}
    for kind, eids in kinds.items():
        if not eids:
            continue
        lines.append(f"*ELSET, ELSET={kind}")
        for start in range(0, len(eids), 12):
            lines.append(", ".join(str(eid) for eid in eids[start:start + 12]))
        lines.append(f"*SOLID SECTION, ELSET={kind}, MATERIAL={kind}")
        lines.append(f"*MATERIAL, NAME={kind}")
        lines.append("*CONDUCTIVITY")
        lines.append(f"{k_of[kind]:.6e}")
    root = [tag for tag, (x, _y, _z) in mesh["nodes"].items() if x < 1e-6]
    if not root:
        raise RuntimeError("handle has no root nodes")
    lines.append("*NSET, NSET=ROOT")
    for start in range(0, len(root), 12):
        lines.append(", ".join(str(tag) for tag in root[start:start + 12]))
    lines.append("*BOUNDARY")
    lines.append(f"ROOT, 11, 11, {skin_c:.2f}")
    # Film on grip faces: nodes with x > 0.037 (the outer end) or |z| > 0.010 or y near 0 or 0.130, and x > 0.016.
    film = ["*FILM"]
    tol = 1e-4
    for eid, nids in mesh["elements"]:
        coords = [mesh["nodes"][nid] for nid in nids]
        if sum(point[0] for point in coords) / 4.0 < 0.016:
            continue
        for face_index, local in enumerate(TET_FACES):
            face = [coords[i] for i in local]
            xs = [point[0] for point in face]
            ys = [point[1] for point in face]
            zs = [point[2] for point in face]
            exposed = (
                all(x > 0.0375 for x in xs)
                or all(z > 0.0105 for z in zs)
                or all(z < -0.0105 for z in zs)
                or all(y < tol for y in ys)
                or all(y > 0.1295 for y in ys)
                or all(abs(x - 0.016) < 0.001 for x in xs)
            )
            if exposed:
                film.append(f"{eid}, {FACE_LABEL[face_index]}, {T_AMB:.2f}, 10.0")
    # *BOUNDARY and *FILM belong inside the step.
    step_at = lines.index("*BOUNDARY")
    body = lines[:step_at] + ["*STEP", "*HEAT TRANSFER, STEADY STATE"] + lines[step_at:] + film
    body.extend(["*NODE FILE", "NT", "*END STEP"])
    (work / "job.inp").write_text("\n".join(body) + "\n", encoding="utf-8")
    run = subprocess.run([str(CCX), "-i", "job"], cwd=work, capture_output=True, text=True)
    if not (work / "job.frd").exists():
        raise RuntimeError((run.stdout or "")[-2000:])
    return _read_frd(work / "job.frd")


def main() -> None:
    out = ROOT / "design" / "variants" / "thermal-fea"
    slab = slab_check(out / "slab")
    print("SLAB", json.dumps(slab))
    if abs(slab["error_C"]) > 2.0:
        raise SystemExit(f"slab check off by {slab['error_C']} C")
    report = {"slab": slab, "walls": {}, "handles": {}}
    for name in ("morning", "moondancer"):
        wall = wall_check(name, out / name / "wall")
        print("WALL", name, json.dumps(wall))
        handle = handle_check(name, wall["outer_C"], out / name / "handle")
        print("HANDLE", name, json.dumps(handle))
        report["walls"][name] = wall
        report["handles"][name] = handle
    dest = ROOT / "design" / "variants" / "thermal-fea.json"
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("WROTE", dest)


if __name__ == "__main__":
    main()
