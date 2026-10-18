#!/usr/bin/env python3
"""Shade an STL in isometric projection. No VTK.

    python3 research/argon-anatomy/drawings/render_stl.py
"""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
OUT = Path(__file__).resolve().parent


def load_stl(path: Path) -> np.ndarray:
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    triangles = np.zeros((count, 3, 3), dtype=np.float64)
    offset = 84
    for index in range(count):
        # normal (3f) + 3 vertices (9f) + attribute (u16)
        nums = struct.unpack_from("<12fH", data, offset)
        triangles[index, 0] = nums[3:6]
        triangles[index, 1] = nums[6:9]
        triangles[index, 2] = nums[9:12]
        offset += 50
    return triangles


def render(path: Path, dest: Path, size: int = 1000, paper: tuple[int, int, int] = (246, 243, 236)) -> None:
    """Z-buffered isometric. Painter's order zebra-stripes a faceted vault."""
    tris = load_stl(path)
    azimuth = np.deg2rad(40)
    elevation = np.deg2rad(28)
    ca, sa = np.cos(azimuth), np.sin(azimuth)
    ce, se = np.cos(elevation), np.sin(elevation)
    forward = np.array([sa * ce, ca * ce, se])
    right = np.array([ca, -sa, 0.0])
    up = np.cross(right, forward)
    up /= np.linalg.norm(up)

    flat = tris.reshape(-1, 3)
    projected = np.stack([flat @ right, flat @ up], axis=1).reshape(-1, 3, 2)
    depth = flat @ forward
    depth = depth.reshape(-1, 3)

    span = projected.max(axis=(0, 1)) - projected.min(axis=(0, 1))
    scale = (size * 0.82) / max(float(span.max()), 1.0)
    center = projected.mean(axis=(0, 1))
    screen = (projected - center) * scale
    screen[:, :, 1] *= -1
    screen[:, :, 0] += size / 2
    screen[:, :, 1] += size / 2

    light = np.array([0.25, -0.45, 0.86])
    light /= np.linalg.norm(light)
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    lengths[lengths == 0] = 1
    normals = normals / lengths[:, None]
    shade = np.clip(np.abs(normals @ light), 0.15, 1.0)

    color = np.zeros((size, size, 3), dtype=np.uint8)
    color[:, :] = paper
    zbuf = np.full((size, size), np.inf)

    for index in range(len(tris)):
        pts = screen[index]
        zs = depth[index]
        min_x = max(int(np.floor(pts[:, 0].min())), 0)
        max_x = min(int(np.ceil(pts[:, 0].max())), size - 1)
        min_y = max(int(np.floor(pts[:, 1].min())), 0)
        max_y = min(int(np.ceil(pts[:, 1].max())), size - 1)
        if max_x <= min_x or max_y <= min_y:
            continue
        tone = 0.22 + 0.78 * float(shade[index])
        rgb = (int(48 + 150 * tone), int(44 + 138 * tone), int(36 + 110 * tone))
        xs = np.arange(min_x, max_x + 1)
        ys = np.arange(min_y, max_y + 1)
        grid_x, grid_y = np.meshgrid(xs, ys)
        x0, y0 = pts[0]
        x1, y1 = pts[1]
        x2, y2 = pts[2]
        denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(denom) < 1e-8:
            continue
        w0 = ((y1 - y2) * (grid_x - x2) + (x2 - x1) * (grid_y - y2)) / denom
        w1 = ((y2 - y0) * (grid_x - x2) + (x0 - x2) * (grid_y - y2)) / denom
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
        if not inside.any():
            continue
        z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
        closer = inside & (z < zbuf[min_y : max_y + 1, min_x : max_x + 1])
        if not closer.any():
            continue
        view = zbuf[min_y : max_y + 1, min_x : max_x + 1]
        view[closer] = z[closer]
        pixel = color[min_y : max_y + 1, min_x : max_x + 1]
        pixel[closer] = rgb

    Image.fromarray(color, mode="RGB").save(dest)
    print(dest)


def main() -> None:
    jobs = [
        ("arc-lite.stl", "arc-lite.png"),
        ("tread.stl", "tread.png"),
        ("dome-xl.stl", "dome-xl.png"),
        ("dome-xl-cutaway.stl", "dome-xl-cutaway.png"),
        ("dome-xl-exploded.stl", "dome-xl-exploded.png"),
    ]
    for src, dest in jobs:
        render(MODELS / src, OUT / dest)


if __name__ == "__main__":
    main()
