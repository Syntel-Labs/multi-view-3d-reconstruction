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


def run_pipeline(
    dataset_name: str,
    output_dir: str | None = None,
    detector: str = "sift",
    lowe_ratio: float = 0.75,
    ransac_threshold: float = 1.0,
    min_matches: int = 8,
    log_file: str | None = "auto",
) -> dict:
    """Ejecutar el pipeline SfM completo sobre un dataset registrado en datasets.yaml.

    Lee imagenes, extrae features, calcula matches consecutivos, estima la geometria
    del par inicial y registra el resto de camaras con solvePnPRansac triangulando
    nuevos puntos en cada paso.

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
    out_dir = Path(output_dir) if output_dir else Path("outputs") / dataset_name
    out_dir.mkdir(parents=True, exist_ok=True)

    k_matrix = load_intrinsics(intrinsics_path)
    log.param("dataset", dataset_name)
    log.param("detector", detector)
    log.param("images_folder", str(images_folder))

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

    # 4. Matching de pares consecutivos
    t0 = time.perf_counter()
    log.section("MATCHING CONSECUTIVO")

    # matches_pairs[i] = array (M, 2) int32 con indices en kp_arrays[i] y kp_arrays[i+1]
    matches_pairs: list[np.ndarray] = []

    for i in range(n_imgs - 1):
        good = matching.match_descriptors(
            desc_arrays[i], desc_arrays[i + 1], detector=detector, ratio=lowe_ratio
        )
        pair_idxs = np.array([[m.queryIdx, m.trainIdx] for m in good], dtype=np.int32)
        matches_pairs.append(pair_idxs)
        log.info("\tPar (%d, %d): %d matches buenos", i, i + 1, len(pair_idxs))

    stage_times["matching"] = time.perf_counter() - t0

    # 5. Geometria del par inicial (0, 1)
    t0 = time.perf_counter()
    log.section("GEOMETRIA PAR INICIAL (0-1)")

    pair0 = matches_pairs[0]
    if len(pair0) < min_matches:
        raise RuntimeError(
            f"Par inicial tiene {len(pair0)} matches (minimo {min_matches}). "
            "Intenta con mas imagenes o un dataset con mayor solapamiento."
        )

    pts_a = kp_arrays[0][pair0[:, 0]].astype(np.float32)
    pts_b = kp_arrays[1][pair0[:, 1]].astype(np.float32)

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
    pts3d_init = pts3d_raw[valid_tri]
    pair0_valid = pair0_in[valid_tri]
    pts2d_init = pts_a_in[valid_tri]  # 2D en camara 0 para reprojection error

    if len(pts3d_init) == 0:
        raise RuntimeError("Triangulacion inicial no produjo ningun punto valido.")

    log.info("\tPuntos iniciales validos: %d (de %d triangulados)", len(pts3d_init), len(pts3d_raw))

    # Estructura de seguimiento: (img_idx, kp_idx) -> indice en cloud_pts
    cloud_pts: list[np.ndarray] = list(pts3d_init)
    kp_to_cloud: dict[tuple[int, int], int] = {}

    for j, (ki, kj) in enumerate(pair0_valid):
        kp_to_cloud[(0, int(ki))] = j
        kp_to_cloud[(1, int(kj))] = j

    camera_rs: list[np.ndarray | None] = [r0, r_init]
    camera_ts: list[np.ndarray | None] = [t0_vec, t_init]

    stage_times["triangulation"] = time.perf_counter() - t0

    # 7. Registro incremental de camaras
    t0 = time.perf_counter()
    log.section("MULTI-VISTA INCREMENTAL")
    pnp_ratios: list[float] = []
    lookback = 5  # camaras atras a consultar cuando el par consecutivo no alcanza

    for i in range(2, n_imgs):

        # 7a. Correspondencias 3D-2D: par consecutivo + ventana deslizante
        pts3d_for_pnp: list[np.ndarray] = []
        pts2d_for_pnp: list[np.ndarray] = []
        seen_cloud: set[int] = set()

        for row in matches_pairs[i - 1]:
            ki_prev, ki_curr = int(row[0]), int(row[1])
            cloud_idx = kp_to_cloud.get((i - 1, ki_prev))
            if cloud_idx is not None and cloud_idx not in seen_cloud:
                pts3d_for_pnp.append(cloud_pts[cloud_idx])
                pts2d_for_pnp.append(kp_arrays[i][ki_curr])
                seen_cloud.add(cloud_idx)

        # Si no hay suficientes, buscar en camaras registradas anteriores
        if len(pts3d_for_pnp) < min_matches:
            registered_before = [j for j in range(i - 2, -1, -1) if camera_rs[j] is not None]
            for j in registered_before[:lookback]:
                extra = matching.match_descriptors(
                    desc_arrays[j], desc_arrays[i], detector=detector, ratio=lowe_ratio
                )
                added = 0
                for m in extra:
                    cloud_idx = kp_to_cloud.get((j, m.queryIdx))
                    if cloud_idx is not None and cloud_idx not in seen_cloud:
                        pts3d_for_pnp.append(cloud_pts[cloud_idx])
                        pts2d_for_pnp.append(kp_arrays[i][m.trainIdx])
                        seen_cloud.add(cloud_idx)
                        added += 1
                if added:
                    log.info("\tImagen %d: ventana cam %d, +%d corr3D", i, j, added)
                if len(pts3d_for_pnp) >= min_matches:
                    break

        if len(pts3d_for_pnp) < min_matches:  # noqa: PLR2004
            n_corr = len(pts3d_for_pnp)
            log.warn("\tImagen %d: %d correspondencias 3D-2D insuficientes, saltando", i, n_corr)
            camera_rs.append(None)
            camera_ts.append(None)
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
            camera_rs.append(None)
            camera_ts.append(None)
            continue

        r_i, _ = cv2.Rodrigues(rvec)
        t_i = tvec
        camera_rs.append(r_i)
        camera_ts.append(t_i)

        ratio_pnp = len(pnp_inliers) / len(pts3d_for_pnp)
        pnp_ratios.append(ratio_pnp)
        log.info(
            "\tImagen %d: registrada, inlier_ratio=%.2f, corr3D=%d",
            i, ratio_pnp, len(pts3d_for_pnp),
        )

        # 7c. Triangular nuevos puntos usando la camara registrada mas reciente
        tri_j = next((jj for jj in range(i - 1, -1, -1) if camera_rs[jj] is not None), None)
        if tri_j is None:
            continue

        if tri_j == i - 1:
            tri_pairs = matches_pairs[i - 1]
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

        for j, tri_local in enumerate(valid_local):
            cld_idx = base_cloud_idx + j
            cloud_pts.append(new_pts3d[tri_local])
            kp_to_cloud[(i - 1, int(ki_prev_arr[tri_local]))] = cld_idx
            kp_to_cloud[(i, int(ki_curr_arr[tri_local]))] = cld_idx

        log.info("\tImagen %d: +%d nuevos puntos 3D", i, len(valid_local))

    stage_times["multiview"] = time.perf_counter() - t0

    # 8. Recolectar nube final y filtrar outliers geometricos
    pts3d_all = np.array(cloud_pts, dtype=np.float64)

    # Filtro IQR: eliminar puntos mas alla de 3*IQR del percentil 25-75 en cada eje.
    # Captura triangulaciones degeneradas de rayos casi paralelos (Z ~ 1e14).
    q25 = np.percentile(pts3d_all, 25, axis=0)
    q75 = np.percentile(pts3d_all, 75, axis=0)
    iqr = q75 - q25
    iqr = np.where(iqr < 1e-9, 1.0, iqr)  # evitar IQR==0 en nubes planas
    inlier_mask = np.all(
        (pts3d_all >= q25 - 3.0 * iqr) & (pts3d_all <= q75 + 3.0 * iqr),
        axis=1,
    )
    n_before = len(pts3d_all)
    pts3d_all = pts3d_all[inlier_mask]
    log.info(
        "\tFiltro IQR: %d -> %d puntos (eliminados %d outliers)",
        n_before, len(pts3d_all), n_before - len(pts3d_all),
    )

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
