from __future__ import annotations

import cv2
import numpy as np

from sfm_pipeline.utils import build_projection_matrix  # noqa: F401

# Distancia maxima aceptable desde el origen del mundo (en unidades de escena).
# Puntos mas alla de este umbral se consideran degenerados.
_MAX_POINT_DIST = 1e5


def triangulate_points(
    p1: np.ndarray,
    p2: np.ndarray,
    points_a: np.ndarray,
    points_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Triangular puntos 3D usando DLT lineal (cv2.triangulatePoints).

    Args:
        p1: matriz de proyeccion camara 1 (3, 4).
        p2: matriz de proyeccion camara 2, shape (3, 4).
        points_a: correspondencias en imagen 1, shape (N, 2), float32 o float64.
        points_b: correspondencias en imagen 2, shape (N, 2), float32 o float64.

    Returns:
        pts3d: puntos 3D en coordenadas de mundo (N, 3) float64.
        valid_mask: mascara booleana (N,) — True si el punto tiene profundidad
                    positiva en ambas camaras, no es infinito y no esta
                    a distancia degenerada del origen.

    Raises:
        ValueError: si arrays tienen formas incompatibles o menos de 1 punto.
    """
    if points_a.shape != points_b.shape:
        raise ValueError(
            f"points_a y points_b deben tener la misma forma; "
            f"recibido {points_a.shape} vs {points_b.shape}."
        )
    if points_a.ndim != 2 or points_a.shape[1] != 2:  # noqa: PLR2004
        raise ValueError(
            f"Se esperan arrays (N, 2); recibido shape {points_a.shape}."
        )
    if points_a.shape[0] < 1:
        raise ValueError("Se necesita al menos 1 correspondencia para triangular.")

    pts_a = points_a.astype(np.float64).T   # (2, N)
    pts_b = points_b.astype(np.float64).T   # (2, N)

    pts4d = cv2.triangulatePoints(p1, p2, pts_a, pts_b)  # (4, N)

    w = pts4d[3]

    # w cercano a cero produce divisiones que explotan a e+16 / e+17.
    # Marcar esos puntos como invalidos antes de dividir.
    w_degenerate = np.abs(w) < 1e-7

    # Division segura: usar 1.0 donde w es degenerado para evitar inf/nan,
    # esos puntos se eliminan luego por valid_mask.
    w_safe = np.where(w_degenerate, 1.0, w)
    pts3d = (pts4d[:3] / w_safe).T.astype(np.float64)  # (N, 3)

    pts_h = np.vstack([pts3d.T, np.ones((1, pts3d.shape[0]))])  # (4, N)

    z_cam1 = (p1 @ pts_h)[2]   # profundidad en camara 1
    z_cam2 = (p2 @ pts_h)[2]   # profundidad en camara 2

    # Distancia euclidea desde el origen del mundo.
    dist_from_origin = np.linalg.norm(pts3d, axis=1)

    valid_mask = (
        (~w_degenerate)                          # w no degenerado
        & (z_cam1 > 0)                           # frente a camara 1
        & (z_cam2 > 0)                           # frente a camara 2
        & np.isfinite(pts3d).all(axis=1)         # sin inf / nan
        & (dist_from_origin < _MAX_POINT_DIST)   # distancia razonable
    )

    return pts3d, valid_mask
