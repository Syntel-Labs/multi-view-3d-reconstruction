"""Geometria epipolar: matriz fundamental F, esencial E y recuperacion de pose.

Referencia: docs/theory/08_sfm-geometry-reference.md
H&Z Capitulos 9 y 10.
"""

import logging

import cv2
import numpy as np

from sfm_pipeline.debug import PipelineLogger


def estimate_fundamental(
    points_a: np.ndarray,
    points_b: np.ndarray,
    ransac_threshold: float = 1.0,
    confidence: float = 0.99,
    max_iters: int = 2000,
    verbose: bool = False,
    log_level: int = logging.DEBUG,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimar la matriz fundamental F con RANSAC.

    Args:
        points_a: correspondencias en imagen A, shape (n, 2), dtype float32.
        points_b: correspondencias en imagen B, shape (n, 2), dtype float32.
        ransac_threshold: distancia maxima punto-linea epipolar en pixeles para inlier.
        confidence: probabilidad deseada de obtener F correcto.
        max_iters: numero maximo de iteraciones RANSAC.
        verbose: si True, imprime y loguea estadisticas detalladas.
        log_level: nivel de logging (logging.DEBUG / INFO / ...).

    Returns:
        F: matriz fundamental (3, 3).
        mask: array (n, 1) uint8 donde 1 indica inlier.

    Raises:
        ValueError: si hay menos de 8 correspondencias o F no puede estimarse.
    """
    log = PipelineLogger("F", verbose=verbose, log_level=log_level)
    n = len(points_a)

    log.section("Estimar matriz fundamental")
    log.param("n_correspondencias", n)
    log.param("ransac_threshold", ransac_threshold, "px")
    log.param("confidence", confidence)
    log.param("max_iters", max_iters)

    if n < 8:
        raise ValueError(f"Se necesitan al menos 8 puntos; se recibieron {n}.")

    F, mask = cv2.findFundamentalMat(
        points_a,
        points_b,
        method=cv2.FM_RANSAC,
        ransacReprojThreshold=ransac_threshold,
        confidence=confidence,
        maxIters=max_iters,
    )

    if F is None or F.shape != (3, 3):
        raise ValueError("findFundamentalMat no pudo estimar F con los puntos dados.")

    _, s_f, _ = np.linalg.svd(F)
    rank = int(np.sum(s_f > 1e-10))
    n_inliers = int(mask.sum())
    ratio = n_inliers / n

    # Distancias epipolares de los inliers
    pts_a_in = points_a[mask.ravel() == 1]
    pts_b_in = points_b[mask.ravel() == 1]
    pts_a_h = np.column_stack([pts_a_in, np.ones(len(pts_a_in))])
    pts_b_h = np.column_stack([pts_b_in, np.ones(len(pts_b_in))])
    lines = (F @ pts_a_h.T).T
    norms = np.sqrt(lines[:, 0] ** 2 + lines[:, 1] ** 2)
    dists = np.abs(np.sum(pts_b_h * lines, axis=1)) / (norms + 1e-10)

    log.matrix("F", F)
    log.stats("Valores singulares y rango", {
        "sigma_1": float(s_f[0]),
        "sigma_2": float(s_f[1]),
        "sigma_3": float(s_f[2]),
        "rank": rank,
    })
    log.stats("Inliers", {
        "n_inliers": n_inliers,
        "n_total": n,
        "ratio": ratio,
    })
    log.stats("Distancia epipolar inliers (px)", {
        "mean": float(dists.mean()),
        "median": float(np.median(dists)),
        "max": float(dists.max()),
        "std": float(dists.std()),
    })

    if ratio < 0.60:
        log.warn("inlier_ratio=%.1f%% < 60%% — revisar calidad de matches", ratio * 100)
    else:
        log.ok("inlier_ratio=%.1f%%", ratio * 100)

    return F, mask


def fundamental_to_essential(
    F: np.ndarray,
    K: np.ndarray,
    verbose: bool = False,
    log_level: int = logging.DEBUG,
) -> np.ndarray:
    """Calcular la matriz esencial E = K^T F K.

    Fuerza la estructura de E (rango 2, sigma_1 == sigma_2) mediante SVD.

    Args:
        F: matriz fundamental (3, 3).
        K: matriz intrinseca de la camara (3, 3).
        verbose: si True, imprime y loguea valores singulares antes y despues.
        log_level: nivel de logging.

    Returns:
        E: matriz esencial (3, 3) con rango 2 forzado.
    """
    log = PipelineLogger("E", verbose=verbose, log_level=log_level)

    log.section("E = K^T F K")
    E_raw = K.T @ F @ K
    _, s_raw, _ = np.linalg.svd(E_raw)

    log.stats("Singulares de E antes de correccion", {
        "sigma_1": float(s_raw[0]),
        "sigma_2": float(s_raw[1]),
        "sigma_3": float(s_raw[2]),
        "diferencia_s1_s2": float(abs(s_raw[0] - s_raw[1])),
    })

    # Forzar rango 2: sigma_1 == sigma_2 == promedio, sigma_3 == 0
    U, s, Vt = np.linalg.svd(E_raw)
    s_avg = (s[0] + s[1]) / 2.0
    s_corrected = np.array([s_avg, s_avg, 0.0])
    E = U @ np.diag(s_corrected) @ Vt

    _, s_post, _ = np.linalg.svd(E)
    log.stats("Singulares de E despues de correccion", {
        "sigma_1": float(s_post[0]),
        "sigma_2": float(s_post[1]),
        "sigma_3": float(s_post[2]),
        "diferencia_s1_s2": float(abs(s_post[0] - s_post[1])),
    })
    log.matrix("E corregida", E)
    log.ok("rango 2 forzado correctamente")

    return E


def recover_pose(
    E: np.ndarray,
    points_a: np.ndarray,
    points_b: np.ndarray,
    K: np.ndarray,
    mask: np.ndarray | None = None,
    verbose: bool = False,
    log_level: int = logging.DEBUG,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Descomponer E en R y t con verificacion de cheirality.

    Resuelve la ambiguedad de las 4 soluciones de pose eligiendo aquella
    en la que el mayor numero de puntos queda delante de ambas camaras.

    Args:
        E: matriz esencial (3, 3).
        points_a: correspondencias en imagen A, shape (n, 2), dtype float32.
        points_b: correspondencias en imagen B, shape (n, 2), dtype float32.
        K: matriz intrinseca (3, 3).
        mask: mascara de inliers de estimate_fundamental.
        verbose: si True, muestra las 4 soluciones de pose y la seleccionada.
        log_level: nivel de logging.

    Returns:
        R: matriz de rotacion (3, 3) de camara A a camara B.
        t: vector de traslacion (3, 1) unitario (escala indeterminada).
        n_inliers: numero de puntos que pasan la prueba de cheirality.
    """
    log = PipelineLogger("recoverPose", verbose=verbose, log_level=log_level)

    log.section("Descomposicion E -> R, t (cheirality)")
    log.param("n_puntos_entrada", len(points_a))

    # Mostrar las 4 soluciones candidatas antes de que OpenCV elija
    W = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float64)
    U, _, Vt = np.linalg.svd(E)
    candidates = [
        ("R1 +t", U @ W @ Vt,   U[:, 2].reshape(3, 1)),
        ("R1 -t", U @ W @ Vt,  -U[:, 2].reshape(3, 1)),
        ("R2 +t", U @ W.T @ Vt, U[:, 2].reshape(3, 1)),
        ("R2 -t", U @ W.T @ Vt,-U[:, 2].reshape(3, 1)),
    ]
    log.info("4 soluciones candidatas (antes de cheirality):")
    for label, R_c, t_c in candidates:
        angle = float(np.degrees(np.arccos(np.clip((np.trace(R_c) - 1) / 2, -1, 1))))
        log.stats(f"\t{label}", {
            "det_R": float(np.linalg.det(R_c)),
            "angulo_deg": angle,
            "t_x": float(t_c[0]),
            "t_y": float(t_c[1]),
            "t_z": float(t_c[2]),
        })

    n_inliers, R, t, _ = cv2.recoverPose(
        E, points_a, points_b, cameraMatrix=K, mask=mask,
    )

    angle_sel = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
    log.info("Solucion seleccionada por cheirality:")
    log.stats("Pose seleccionada", {
        "n_cheirality": n_inliers,
        "cheirality_ratio": n_inliers / max(len(points_a), 1),
        "angulo_rotacion_deg": angle_sel,
        "det_R": float(np.linalg.det(R)),
        "norma_t": float(np.linalg.norm(t)),
    })
    log.matrix("R", R)
    log.vector("t", t)

    return R, t, n_inliers


def inlier_ratio(mask: np.ndarray) -> float:
    """Calcular la fraccion de inliers sobre el total de correspondencias.

    Args:
        mask: array (n, 1) o (n,) uint8 devuelto por findFundamentalMat.

    Returns:
        Fraccion en [0, 1].
    """
    m = mask.ravel()
    return float(m.sum()) / float(len(m))


# ---------------------------------------------------------------------------
# Pipeline de debug completo
# ---------------------------------------------------------------------------

def debug_geometry_pipeline(
    points_a: np.ndarray,
    points_b: np.ndarray,
    K: np.ndarray,
    ransac_threshold: float = 1.0,
    confidence: float = 0.99,
    max_iters: int = 2000,
    min_inlier_ratio: float = 0.60,
    log_level: int = logging.DEBUG,
    log_file: str | None = None,
) -> dict:
    """Ejecutar el pipeline F -> E -> pose con logging detallado de cada paso.

    Args:
        points_a: correspondencias en imagen A, shape (n, 2), dtype float32.
        points_b: correspondencias en imagen B, shape (n, 2), dtype float32.
        K: matriz intrinseca (3, 3).
        ransac_threshold: umbral de inlier en pixeles para RANSAC de F.
        confidence: confianza RANSAC.
        max_iters: iteraciones maximas RANSAC.
        min_inlier_ratio: umbral minimo de inliers para emitir advertencia.
        log_level: nivel de logging.
        log_file: ruta al archivo de log, "auto" para generarla automaticamente
                  en outputs/logs/, o None para no escribir a disco.

    Returns:
        Diccionario con todas las salidas intermedias:
        {F, mask, inlier_ratio, E, R, t, n_cheirality, ok, log_file}
    """
    logging.basicConfig(level=log_level, format="%(levelname)s\t%(message)s")
    log = PipelineLogger("pipeline", verbose=True, log_level=log_level, log_file=log_file)

    log.section("DEBUG GEOMETRY PIPELINE")
    log.param("n_puntos", len(points_a))
    log.param("ransac_threshold", ransac_threshold, "px")
    log.param("confidence", confidence)
    log.param("max_iters", max_iters)
    log.param("min_inlier_ratio", f"{min_inlier_ratio:.0%}")

    F, mask = estimate_fundamental(
        points_a, points_b,
        ransac_threshold=ransac_threshold,
        confidence=confidence,
        max_iters=max_iters,
        verbose=True,
        log_level=log_level,
    )
    ratio = inlier_ratio(mask)

    E = fundamental_to_essential(F, K, verbose=True, log_level=log_level)

    pts_a_in = points_a[mask.ravel() == 1]
    pts_b_in = points_b[mask.ravel() == 1]
    R, t, n_ch = recover_pose(E, pts_a_in, pts_b_in, K, verbose=True, log_level=log_level)

    cheirality_ratio = n_ch / max(len(pts_a_in), 1)
    ok = log.summary({
        "Inlier ratio F":     (ratio, ratio >= min_inlier_ratio),
        "Cheirality ratio":   (cheirality_ratio, cheirality_ratio >= 0.5),
        "det(R)":             (float(np.linalg.det(R)), abs(np.linalg.det(R) - 1.0) < 1e-4),
        "|t|":                (float(np.linalg.norm(t)), abs(np.linalg.norm(t) - 1.0) < 1e-4),
    })

    if log.log_file:
        log.info("Log guardado en: %s", log.log_file)

    return {
        "F": F,
        "mask": mask,
        "inlier_ratio": ratio,
        "E": E,
        "R": R,
        "t": t,
        "n_cheirality": n_ch,
        "ok": ok,
        "log_file": log.log_file,
    }
