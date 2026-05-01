"""Script de uso unico: valida geometry.py sobre el par estereo sintetico.

Criterio de aceptacion (Entrega 1): inlier_ratio >= 0.60 sobre el par sintetico.
Uso dentro del contenedor (desde /app): python scripts/validate_geometry.py [--verbose]
"""

import logging
import sys

import numpy as np

sys.path.insert(0, "src")
from sfm_pipeline.geometry import debug_geometry_pipeline
from synthetic_stereo import generate_stereo_pair


def _rotation_angle_deg(R_est: np.ndarray, R_gt: np.ndarray) -> float:
    R_diff = R_est @ R_gt.T
    cos_angle = float(np.clip((np.trace(R_diff) - 1.0) / 2.0, -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_angle)))


def main() -> None:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    log_level = logging.DEBUG if verbose else logging.WARNING

    data = generate_stereo_pair(n_points=300, noise_std=0.5, seed=0)
    K = data["K"]
    R_gt = data["R_gt"]

    result = debug_geometry_pipeline(
        data["pts_img1"],
        data["pts_img2"],
        K,
        ransac_threshold=1.0,
        confidence=0.99,
        max_iters=2000,
        min_inlier_ratio=0.60,
        log_level=log_level,
        log_file="auto",
    )

    # Comparar R estimada con la ground truth
    angle_err = _rotation_angle_deg(result["R"], R_gt)
    print(f"  Error angular vs ground truth: {angle_err:.2f} grados (esperado < 5)")

    if not result["ok"] or angle_err > 5.0:
        print("\nFALLO: geometry.py no cumple los criterios de Entrega 1")
        sys.exit(1)

    print("RESULTADO FINAL: OK - geometry.py validado para Entrega 1\n")


if __name__ == "__main__":
    main()
