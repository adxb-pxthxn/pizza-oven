#!/usr/bin/env python3
"""Shade one or more binary STLs in isometric projection.

Each body is a dict with a path and an RGB colour. No VTK.

    python3 design/tailgate/drawings/render_colored.py
"""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def load_stl(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if data[:5] == b"solid" and b"\x00" not in data[:80]:
        raise ValueError(f"{path} looks like ASCII STL; export binary")
    count = struct.unpack_from("<I", data, 80)[0]
    if 84 + count * 50 > len(data):
        raise ValueError(f"{path} triangle count {count} does not fit the file")
    triangles = np.zeros((count, 3, 3), dtype=np.float64)
    offset = 84
    for index in range(count):
        nums = struct.unpack_from("<12fH", data, offset)
        triangles[index, 0] = nums[3:6]
        triangles[index, 1] = nums[6:9]
        triangles[index, 2] = nums[9:12]
        offset += 50
    return triangles


def render_bodies(
    bodies: list[tuple[np.ndarray, tuple[int, int, int]]],
    dest: Path,
    *,
    size: int = 1400,
    title: str = "",
    subtitle: str = "",
    azimuth_deg: float = 38,
    elevation_deg: float = 24,
    paper: tuple[int, int, int] = (244, 240, 232),
    frame: tuple[np.ndarray, np.ndarray] | None = None,
) -> None:
    """Painter's-order shaded triangles. `bodies` are (triangles, rgb).

    `frame` is (min_xyz, max_xyz). The camera scale comes from that box so a
    long leg can leave the picture without shrinking the oven.
    """
    if not bodies:
        raise ValueError("no bodies")
    azimuth = np.deg2rad(azimuth_deg)
    elevation = np.deg2rad(elevation_deg)
    ca, sa = np.cos(azimuth), np.sin(azimuth)
    ce, se = np.cos(elevation), np.sin(elevation)
    forward = np.array([sa * ce, ca * ce, se])
    right = np.array([ca, -sa, 0.0])
    up = np.cross(right, forward)
    up /= np.linalg.norm(up)
    light = np.array([0.35, -0.55, 0.76])
    light /= np.linalg.norm(light)
    fill = np.array([0.15, 0.35, 0.55])
    fill /= np.linalg.norm(fill)

    if frame is None:
        flat = np.concatenate([tris.reshape(-1, 3) for tris, _ in bodies], axis=0)
        lo, hi = flat.min(axis=0), flat.max(axis=0)
    else:
        lo, hi = frame
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    projected_corners = np.stack([corners @ right, corners @ up], axis=1)
    span = projected_corners.max(axis=0) - projected_corners.min(axis=0)
    scale = (size * 0.78) / max(float(span.max()), 1.0)
    center = (projected_corners.max(axis=0) + projected_corners.min(axis=0)) / 2

    tris_all = []
    for tris, color in bodies:
        if len(tris) == 0:
            continue
        normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
        lengths = np.linalg.norm(normals, axis=1)
        lengths[lengths == 0] = 1
        normals = normals / lengths[:, None]
        facing = normals @ forward
        shade = np.clip(0.30 + 0.58 * np.clip(normals @ light, 0, 1) + 0.16 * np.clip(normals @ fill, 0, 1), 0.22, 1.12)
        depth = tris.mean(axis=1) @ forward
        flat = tris.reshape(-1, 3)
        projected = np.stack([flat @ right, flat @ up], axis=1).reshape(-1, 3, 2)
        screen = (projected - center) * scale
        screen[:, :, 1] *= -1
        screen[:, :, 0] += size * 0.50
        screen[:, :, 1] += size * 0.56
        base = np.array(color, dtype=np.float64)
        for index in range(len(tris)):
            # Keep the face that points at the camera. A 1.2 mm shell's
            # underside otherwise speckles through the outer surface.
            if facing[index] <= 0.02:
                continue
            rgb = tuple(int(max(0, min(255, channel))) for channel in base * shade[index])
            pts = tuple((float(p[0]), float(p[1])) for p in screen[index])
            tris_all.append((float(depth[index]), pts, rgb))
    # Z-buffer. Painter's order showed the far wall through the mouth.
    color_img = np.zeros((size, size, 3), dtype=np.uint8)
    color_img[:, :] = paper
    zbuf = np.full((size, size), -np.inf)
    order = np.argsort([item[0] for item in tris_all])
    # Depth sort is only the draw order; the buffer rejects anything behind.
    for index in order:
        depth, pts, rgb = tris_all[index]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        min_x = max(int(min(xs)), 0)
        max_x = min(int(max(xs)) + 1, size - 1)
        min_y = max(int(min(ys)), 0)
        max_y = min(int(max(ys)) + 1, size - 1)
        if max_x <= min_x or max_y <= min_y:
            continue
        if (max_x - min_x) * (max_y - min_y) > 80_000:
            continue
        (x0, y0), (x1, y1), (x2, y2) = pts
        denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(denom) < 1e-6:
            continue
        grid_x, grid_y = np.meshgrid(np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1))
        w0 = ((y1 - y2) * (grid_x - x2) + (x2 - x1) * (grid_y - y2)) / denom
        w1 = ((y2 - y0) * (grid_x - x2) + (x0 - x2) * (grid_y - y2)) / denom
        w2 = 1.0 - w0 - w1
        mask = (w0 >= -0.01) & (w1 >= -0.01) & (w2 >= -0.01)
        region = zbuf[min_y:max_y + 1, min_x:max_x + 1]
        update = mask & (depth > region)
        if not np.any(update):
            continue
        region[update] = depth
        zbuf[min_y:max_y + 1, min_x:max_x + 1] = region
        block = color_img[min_y:max_y + 1, min_x:max_x + 1]
        block[update] = rgb
        color_img[min_y:max_y + 1, min_x:max_x + 1] = block
    image = Image.fromarray(color_img, mode="RGB")
    draw = ImageDraw.Draw(image)
    if title:
        draw.text((36, 28), title, fill=(28, 26, 22))
    if subtitle:
        draw.text((36, 56), subtitle, fill=(90, 78, 64))
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)


def main() -> None:
    print("import this module and call render_bodies")


if __name__ == "__main__":
    main()
