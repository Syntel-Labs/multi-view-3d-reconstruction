from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from sfm_pipeline import config, export, features, matching, metrics, preprocess, triangulation
from sfm_pipeline.debug import PipelineLogger
from sfm_pipeline.geometry import (
    estimate_fundamental,
    fundamental_to_essential,
    inlier_ratio,
    recover_pose,
)
from sfm_pipeline.utils import (
    build_projection_matrix,
    list_images,
    load_intrinsics,
    reprojection_errors,
)

WINDOW = 6  # cubre (i, i+1), (i, i+2), (i, i+3)

# Umbral de distancia euclidea maxima desde el origen para considerar un punto
# 3D valido. Debe ser coherente con _MAX_POINT_DIST en triangulation.py.
_MAX_POINT_DIST = 1e5

# Factor IQR para el filtro de outliers final (1.5 es el estandar estadistico).
_IQR_FACTOR = 1.5


def _is_point_valid(pt: np.ndarray) -> bool:
    """Verificar que un punto 3D no es degenerado ni esta fuera de rango."""
    return (
        pt is not None
        and np.all(np.isfinite(pt))
        and np.linalg.norm(pt) < _MAX_POINT_DIST
    )


def _is_pose_valid(rvec: np.ndarray, tvec: np.ndarray) -> bool:
    """Verificar que rvec y tvec devueltos por solvePnPRansac no son degenerados."""
    return (
        np.all(np.isfinite(rvec))
        and np.all(np.isfinite(tvec))
        and np.linalg.norm(tvec) < _MAX_POINT_DIST
    )


def run_pipeline(
    dataset_name: str,
    output_dir: str | None = None,
    detector: str = "sift",
    lowe_ratio: float = 0.75,
    ransac_threshold: float = 1.0,
    min_matches: int = 6,
    log_file: str | None = "auto",
) -> dict:
    """Ejecutar el pipeline SfM completo sobre un dataset registrado en datasets.yaml.

    Lee imagenes, extrae features, calcula matches con ventana deslizante, estima la
    geometria del par inicial y registra el resto de camaras con solvePnPRansac
    triangulando nuevos puntos en cada paso.

    Args:
        dataset_name: Nombre del dataset declarado en data/datasets.yaml.
        output_dir: Carpeta destino para cloud.ply y metrics.json.
                    Por defecto: outputs/<dataset_name>/.
        detector: Detector de features; "sift" (default) o "orb".
        lowe_ratio: Umbral del test de ratio de Lowe para matching.
        ransac_threshold: Umbral de inlier en pixeles para RANSAC de F.
        min_matches: Minimo de matches validos para procesar un par.
        log_file: "auto" para generar ruta automatica en outputs/logs/,
                  ruta explicita, o None para no guardar a disco.

    Returns:
        Diccionario con el schema de metrics.json: dataset, num_images,
        reprojection_error_mean, reprojection_error_median, ransac_inlier_ratio,
        num_3d_points, time_per_stage_seconds.

    Raises:
        ValueError: Si el dataset no existe o la configuracion es invalida.
        RuntimeError: Si no hay suficientes imagenes o el par inicial falla.
    """
    t_total_start = time.perf_counter()
    stage_times: dict[str, float] = {}

    log = PipelineLogger("sfm", verbose=True, log_file=log_file)
    log.section("SFM PIPELINE")

    # 1. Cargar configuracion del dataset
    registry = config.load_datasets_registry("data/datasets.yaml")
    dataset = config.get_dataset(registry, dataset_name)

    images_folder = Path(dataset.get("images_path") or Path(dataset["path"]) / "images")
    intrinsics_path = Path(dataset["intrinsics"])
    if not intrinsics_path.exists():
        raise ValueError(
            f"Archivo de intrinsics no encontrado: {intrinsics_path}. "
            "Verifica la clave 'intrinsics' en datasets.yaml."
        )
    out_dir = Path(output_dir) if output_dir else Path("outputs") / dataset_name
    out_dir.mkdir(parents=True, exist_ok=True)

    k_matrix = load_intrinsics(intrinsics_path)
    log.param("dataset", dataset_name)
    log.param("detector", detector)
    log.param("images_folder", str(images_folder))
    log.param("window", WINDOW)

    # 2. Cargar imagenes
    image_paths = list_images(images_folder)
    n_imgs = len(image_paths)
    if n_imgs < 2:
        raise RuntimeError(
            f"Se necesitan al menos 2 imagenes; se encontraron {n_imgs} en {images_folder}."
        )
    log.param("n_imagenes", n_imgs)

    # 3. Extraccion de features
    t0 = time.perf_counter()
    log.section("FEATURES")

    images_bgr: list[np.ndarray] = []
    kp_arrays: list[np.ndarray] = []    # (N_i, 2) float32
    desc_arrays: list[np.ndarray] = []

    for idx, img_path in enumerate(image_paths):
        img_bgr = preprocess.load_image(img_path)
        gray = preprocess.to_grayscale(img_bgr)
        images_bgr.append(img_bgr)

        if detector == "orb":
            kps, des = features.detect_orb(gray)
        else:
            kps, des = features.detect_sift(gray)

        pts = features.keypoints_to_array(kps)
        kp_arrays.append(pts)
        desc_arrays.append(des)
        log.info("\tImagen %d (%s): %d keypoints", idx, img_path.name, len(pts))

    stage_times["features"] = time.perf_counter() - t0

    # 4. Windowed matching: pares (i, i+1), (i, i+2) ... (i, i+WINDOW)
    t0 = time.perf_counter()
    log.section(f"MATCHING VENTANA (window={WINDOW})")

    # matches_dict[(i, j)] = array (M, 2) int32 con indices en kp_arrays[i] y kp_arrays[j]
    matches_dict: dict[tuple[int, int], np.ndarray] = matching.match_windowed(
        desc_arrays=desc_arrays,
        detector=detector,
        ratio=lowe_ratio,
        window=WINDOW,
    )

    for (i, j), arr in sorted(matches_dict.items()):
        log.info("\tPar (%d, %d): %d matches buenos", i, j, len(arr))

    stage_times["matching"] = time.perf_counter() - t0

    # 5. Geometria del par inicial — usar el par (0, 1) o el mejor par disponible
    t0 = time.perf_counter()
    log.section("GEOMETRIA PAR INICIAL")

    init_candidates = [(i, j) for (i, j) in matches_dict if i == 0]
    if not init_candidates:
        raise RuntimeError("No hay matches validos para ningun par inicial.")

    init_pair = max(init_candidates, key=lambda p: len(matches_dict[p]))
    pair0 = matches_dict[init_pair]
    log.info("\tPar inicial seleccionado: %s con %d matches", init_pair, len(pair0))

    if len(pair0) < min_matches:
        raise RuntimeError(
            f"Par inicial {init_pair} tiene {len(pair0)} matches (minimo {min_matches}). "
            "Intenta con mas imagenes o un dataset con mayor solapamiento."
        )

    cam_a, cam_b = init_pair
    pts_a = kp_arrays[cam_a][pair0[:, 0]].astype(np.float32)
    pts_b = kp_arrays[cam_b][pair0[:, 1]].astype(np.float32)

    f_mat, mask_f = estimate_fundamental(
        pts_a, pts_b, ransac_threshold=ransac_threshold, verbose=True
    )
    ratio_f = inlier_ratio(mask_f)

    e_mat = fundamental_to_essential(f_mat, k_matrix, verbose=True)

    inlier_sel = mask_f.ravel() == 1
    pts_a_in = pts_a[inlier_sel]
    pts_b_in = pts_b[inlier_sel]
    pair0_in = pair0[inlier_sel]

    r_init, t_init, _ = recover_pose(e_mat, pts_a_in, pts_b_in, k_matrix, verbose=True)

    stage_times["geometry"] = time.perf_counter() - t0

    # 6. Triangulacion del par inicial
    t0 = time.perf_counter()
    log.section("TRIANGULACION INICIAL")

    r0 = np.eye(3, dtype=np.float64)
    t0_vec = np.zeros((3, 1), dtype=np.float64)
    p0_mat = build_projection_matrix(k_matrix, r0, t0_vec)
    p1_mat = build_projection_matrix(k_matrix, r_init, t_init)

    pts3d_raw, valid_tri = triangulation.triangulate_points(p0_mat, p1_mat, pts_a_in, pts_b_in)

    # Guardar solo puntos validos: triangulate_points ya filtra w degenerado,
    # profundidad negativa, inf/nan y distancia excesiva.
    pts3d_init = pts3d_raw[valid_tri]
    pair0_valid = pair0_in[valid_tri]
    pts2d_init = pts_a_in[valid_tri]

    if len(pts3d_init) == 0:
        raise RuntimeError("Triangulacion inicial no produjo ningun punto valido.")

    log.info("\tPuntos iniciales validos: %d (de %d triangulados)", len(pts3d_init), len(pts3d_raw))

    # Estructura de seguimiento: (img_idx, kp_idx) -> indice en cloud_pts
    cloud_pts: list[np.ndarray] = list(pts3d_init)
    kp_to_cloud: dict[tuple[int, int], int] = {}

    camera_rs: list[np.ndarray | None] = [None] * n_imgs
    camera_ts: list[np.ndarray | None] = [None] * n_imgs
    camera_rs[cam_a] = r0
    camera_ts[cam_a] = t0_vec
    camera_rs[cam_b] = r_init
    camera_ts[cam_b] = t_init

    for j, (ki, kj) in enumerate(pair0_valid):
        kp_to_cloud[(cam_a, int(ki))] = j
        kp_to_cloud[(cam_b, int(kj))] = j

    stage_times["triangulation"] = time.perf_counter() - t0

    # 7. Registro incremental de camaras
    t0 = time.perf_counter()
    log.section("MULTI-VISTA INCREMENTAL")
    pnp_ratios: list[float] = []
    lookback = 10

    for i in range(2, n_imgs):
        if camera_rs[i] is not None:
            continue

        # 7a. Correspondencias 3D-2D
        pts3d_for_pnp: list[np.ndarray] = []
        pts2d_for_pnp: list[np.ndarray] = []
        seen_cloud: set[int] = set()

        source_pairs = sorted(
            [(j, i) for (j, k) in matches_dict if k == i and camera_rs[j] is not None],
            key=lambda p: p[0],
            reverse=True,
        )

        for (j, _) in source_pairs:
            pair_ji = matches_dict[(j, i)]
            for row in pair_ji:
                ki_prev, ki_curr = int(row[0]), int(row[1])
                cloud_idx = kp_to_cloud.get((j, ki_prev))
                if cloud_idx is None or cloud_idx in seen_cloud:
                    continue
                pt = cloud_pts[cloud_idx]
                # Descartar puntos corruptos antes de pasarlos a PnP.
                if not _is_point_valid(pt):
                    continue
                pts3d_for_pnp.append(pt)
                pts2d_for_pnp.append(kp_arrays[i][ki_curr])
                seen_cloud.add(cloud_idx)

        # Fallback: buscar en camaras registradas con match on-the-fly
        if len(pts3d_for_pnp) < min_matches:
            registered_before = [j for j in range(i - 1, -1, -1) if camera_rs[j] is not None]
            for j in registered_before[:lookback]:
                if (j, i) in matches_dict:
                    continue
                extra = matching.match_descriptors(
                    desc_arrays[j], desc_arrays[i], detector=detector, ratio=lowe_ratio
                )
                added = 0
                for m in extra:
                    cloud_idx = kp_to_cloud.get((j, m.queryIdx))
                    if cloud_idx is None or cloud_idx in seen_cloud:
                        continue
                    pt = cloud_pts[cloud_idx]
                    if not _is_point_valid(pt):
                        continue
                    pts3d_for_pnp.append(pt)
                    pts2d_for_pnp.append(kp_arrays[i][m.trainIdx])
                    seen_cloud.add(cloud_idx)
                    added += 1
                if added:
                    log.info("\tImagen %d: fallback cam %d, +%d corr3D", i, j, added)
                if len(pts3d_for_pnp) >= min_matches:
                    break

        if len(pts3d_for_pnp) < min_matches:
            log.warn(
                "\tImagen %d: %d correspondencias 3D-2D insuficientes, saltando",
                i, len(pts3d_for_pnp),
            )
            continue

        # 7b. solvePnPRansac
        pts3d_pnp = np.array(pts3d_for_pnp, dtype=np.float64)
        pts2d_pnp = np.array(pts2d_for_pnp, dtype=np.float32)

        success, rvec, tvec, pnp_inliers = cv2.solvePnPRansac(
            pts3d_pnp,
            pts2d_pnp,
            k_matrix,
            None,
            reprojectionError=ransac_threshold * 2.0,
            confidence=0.99,
            iterationsCount=1000,
        )

        if not success or pnp_inliers is None or len(pnp_inliers) < 4:  # noqa: PLR2004
            log.warn("\tImagen %d: solvePnPRansac fallo, saltando", i)
            continue

        # Validar que la pose no es degenerada antes de aceptarla.
        if not _is_pose_valid(rvec, tvec):
            tvec_norm = float(np.linalg.norm(tvec))
            log.warn("\tImagen %d: pose degenerada (tvec=%.2e), saltando", i, tvec_norm)
            continue

        r_i, _ = cv2.Rodrigues(rvec)
        t_i = tvec
        camera_rs[i] = r_i
        camera_ts[i] = t_i

        ratio_pnp = len(pnp_inliers) / len(pts3d_for_pnp)
        pnp_ratios.append(ratio_pnp)
        log.info(
            "\tImagen %d: registrada, inlier_ratio=%.2f, corr3D=%d",
            i, ratio_pnp, len(pts3d_for_pnp),
        )

        # 7c. Triangular nuevos puntos
        tri_j = next((jj for jj in range(i - 1, -1, -1) if camera_rs[jj] is not None), None)
        if tri_j is None:
            continue

        tri_pair_key = (tri_j, i)
        if tri_pair_key in matches_dict:
            tri_pairs = matches_dict[tri_pair_key]
        else:
            extra_tri = matching.match_descriptors(
                desc_arrays[tri_j], desc_arrays[i], detector=detector, ratio=lowe_ratio
            )
            tri_pairs = (
                np.array([[m.queryIdx, m.trainIdx] for m in extra_tri], dtype=np.int32)
                if extra_tri
                else np.empty((0, 2), dtype=np.int32)
            )

        if len(tri_pairs) == 0:
            continue

        p_prev = build_projection_matrix(k_matrix, camera_rs[tri_j], camera_ts[tri_j])
        p_curr = build_projection_matrix(k_matrix, r_i, t_i)

        new_ki_prev: list[int] = []
        new_ki_curr: list[int] = []
        for row in tri_pairs:
            ki_j, ki_c = int(row[0]), int(row[1])
            if kp_to_cloud.get((tri_j, ki_j)) is None and kp_to_cloud.get((i, ki_c)) is None:
                new_ki_prev.append(ki_j)
                new_ki_curr.append(ki_c)

        if len(new_ki_prev) < 4:  # noqa: PLR2004
            continue

        ki_prev_arr = np.array(new_ki_prev, dtype=np.int32)
        ki_curr_arr = np.array(new_ki_curr, dtype=np.int32)
        new_pts_prev = kp_arrays[tri_j][ki_prev_arr].astype(np.float32)
        new_pts_curr = kp_arrays[i][ki_curr_arr].astype(np.float32)

        new_pts3d, new_valid = triangulation.triangulate_points(
            p_prev, p_curr, new_pts_prev, new_pts_curr
        )

        base_cloud_idx = len(cloud_pts)
        valid_local = np.where(new_valid)[0]

        added_new = 0
        for tri_local in valid_local:
            pt = new_pts3d[tri_local]
            # Doble chequeo: triangulate_points ya filtra, pero si algo se cuela
            # por precision de punto flotante lo descartamos aqui.
            if not _is_point_valid(pt):
                continue
            cld_idx = base_cloud_idx + added_new
            cloud_pts.append(pt)
            kp_to_cloud[(tri_j, int(ki_prev_arr[tri_local]))] = cld_idx
            kp_to_cloud[(i, int(ki_curr_arr[tri_local]))] = cld_idx
            added_new += 1

        log.info("\tImagen %d: +%d nuevos puntos 3D", i, added_new)

    stage_times["multiview"] = time.perf_counter() - t0

    # 8. Recolectar nube final y filtrar outliers geometricos con IQR estandar
    pts3d_all = np.array(cloud_pts, dtype=np.float64)

    # Primer pase: eliminar cualquier punto no finito o fuera del umbral absoluto
    # que haya sobrevivido hasta aqui (defensa en profundidad).
    finite_mask = np.all(np.isfinite(pts3d_all), axis=1)
    dist_mask = np.linalg.norm(pts3d_all, axis=1) < _MAX_POINT_DIST
    pts3d_all = pts3d_all[finite_mask & dist_mask]
    n_after_hard = len(pts3d_all)

    # Segundo pase: IQR con factor 1.5 (estandar de Tukey).
    # Con factor 5.0 los outliers de magnitud e+16 sesgaban q25/q75 y el
    # filtro quedaba inutilizado; 1.5 elimina outliers estadisticos reales.
    if n_after_hard > 0:
        q25 = np.percentile(pts3d_all, 25, axis=0)
        q75 = np.percentile(pts3d_all, 75, axis=0)
        iqr = q75 - q25
        iqr = np.where(iqr < 1e-9, 1.0, iqr)
        inlier_mask = np.all(
            (pts3d_all >= q25 - _IQR_FACTOR * iqr) & (pts3d_all <= q75 + _IQR_FACTOR * iqr),
            axis=1,
        )
        n_before_iqr = len(pts3d_all)
        pts3d_all = pts3d_all[inlier_mask]
        log.info(
            "\tFiltro IQR (factor=%.1f): %d -> %d puntos (eliminados %d outliers)",
            _IQR_FACTOR, n_before_iqr, len(pts3d_all), n_before_iqr - len(pts3d_all),
        )
    else:
        log.warn("\tNo quedaron puntos validos tras el filtro de distancia absoluta.")

    # 9. Calcular metricas
    rep_errors = reprojection_errors(pts3d_init, pts2d_init, k_matrix, r0, t0_vec)
    rep_mean = float(rep_errors.mean())
    rep_median = float(np.median(rep_errors))

    valid_cams = sum(1 for r in camera_rs if r is not None)
    mean_pnp_ratio = float(np.mean(pnp_ratios)) if pnp_ratios else ratio_f

    stage_times["total"] = time.perf_counter() - t_total_start

    result: dict = {
        "dataset": dataset_name,
        "num_images": valid_cams,
        "reprojection_error_mean": round(rep_mean, 4),
        "reprojection_error_median": round(rep_median, 4),
        "ransac_inlier_ratio": round(mean_pnp_ratio, 4),
        "num_3d_points": len(pts3d_all),
        "time_per_stage_seconds": {
            "features": round(stage_times.get("features", 0.0), 3),
            "matching": round(stage_times.get("matching", 0.0), 3),
            "geometry": round(stage_times.get("geometry", 0.0), 3),
            "triangulation": round(stage_times.get("triangulation", 0.0), 3),
            "multiview": round(stage_times.get("multiview", 0.0), 3),
        },
    }

    # 10. Exportar artefactos
    ply_path = out_dir / "cloud.ply"
    metrics_path = out_dir / "metrics.json"

    export.write_ply(str(ply_path), pts3d_all)
    metrics.write_metrics_json(str(metrics_path), result)

    log.info("\tPLY guardado en: %s", ply_path)
    log.info("\tMetrics guardado en: %s", metrics_path)

    log.summary({
        "Imagenes registradas":    (valid_cams, valid_cams >= 2),
        "Puntos 3D":               (len(pts3d_all), len(pts3d_all) > 100),
        "Reprojection error (px)": (rep_mean, rep_mean < 5.0),
    })

    return result
