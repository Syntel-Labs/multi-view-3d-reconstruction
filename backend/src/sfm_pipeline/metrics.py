from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from sfm_pipeline.utils import reprojection_errors


def compute_reprojection_error(
    pts3d: np.ndarray,
    pts2d: np.ndarray,
    k: np.ndarray,
    r: np.ndarray,
    t: np.ndarray,
) -> tuple[float, float]:
    """Calcular error de reproyeccion medio y mediano en pixeles.

    Delega en sfm_pipeline.utils.reprojection_errors.

    Args:
        pts3d: (N, 3) puntos 3D triangulados.
        pts2d: (N, 2) observaciones 2D correspondientes.
        k: matriz intrinseca (3, 3).
        r: matriz de rotacion (3, 3).
        t: vector de traslacion (3,) o (3, 1).

    Returns:
        (mean_px, median_px): error medio y mediano en pixeles.
    """
    errors = reprojection_errors(pts3d, pts2d, k, r, t)
    return float(np.mean(errors)), float(np.median(errors))


def write_metrics_json(output_path: str | Path, payload: dict) -> None:
    """Persistir metrics.json siguiendo el schema del contrato (metrics-json.md).

    Crea directorios padre si no existen.
    Escribe con indent=2.

    Args:
        output_path: ruta de salida del archivo JSON.
        payload: diccionario con los campos del schema (dataset, num_images, etc.).
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
