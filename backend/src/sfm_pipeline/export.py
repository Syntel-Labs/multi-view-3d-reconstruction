from __future__ import annotations

from pathlib import Path

import numpy as np


def write_ply(
    output_path: str | Path,
    points_xyz: np.ndarray,
    colors: np.ndarray | None = None,
) -> None:
    """Escribir nube de puntos en formato PLY ASCII.

    Args:
        output_path: ruta de salida (.ply).
        points_xyz: (N, 3) float — coordenadas x, y, z.
        colors: (N, 3) uint8 — canales R, G, B. Si None, usa blanco (255, 255, 255).

    Formato del contrato (cloud-ply.md):
        ply
        format ascii 1.0
        element vertex N
        property float x / y / z
        property uchar red / green / blue
        end_header
        x y z r g b
        ...
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = points_xyz.shape[0]

    if colors is None:
        colors = np.full((n, 3), 255, dtype=np.uint8)
    else:
        colors = np.asarray(colors, dtype=np.uint8)

    header = (
        "ply\n"
        "format ascii 1.0\n"
        f"element vertex {n}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar red\n"
        "property uchar green\n"
        "property uchar blue\n"
        "end_header\n"
    )

    with out_path.open("w", encoding="utf-8") as fh:
        fh.write(header)
        for (x, y, z), (r, g, b) in zip(points_xyz, colors):
            fh.write(f"{x} {y} {z} {r} {g} {b}\n")
