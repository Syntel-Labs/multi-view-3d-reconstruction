from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from sfm_pipeline import (
    config,
    export,
    features,
    matching,
    metrics,
    preprocess,
    triangulation,
)
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
)

# =========================================================
# CONFIG
# =========================================================

WINDOW = 20

_MAX_POINT_DIST = 1e4

_IQR_FACTOR = 3.0

_MIN_PARALLAX_DEG = 0.05

_MAX_REPROJ_ERROR = 4.0

_INIT_PAIR_CANDIDATES = 15

_MIN_INIT_INLIERS = 30


# =========================================================
# HELPERS
# =========================================================


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n < 1e-9:
        return v
    return v / n


def compute_parallax_angle(
    pt1: np.ndarray,
    pt2: np.ndarray,
    k_matrix: np.ndarray,
) -> float:
    k_inv = np.linalg.inv(k_matrix)

    p1 = np.array([pt1[0], pt1[1], 1.0])
    p2 = np.array([pt2[0], pt2[1], 1.0])

    ray1 = normalize(k_inv @ p1)
    ray2 = normalize(k_inv @ p2)

    cosang = np.clip(np.dot(ray1, ray2), -1.0, 1.0)

    return np.degrees(np.arccos(cosang))


def reprojection_error(
    point_3d: np.ndarray,
    point_2d: np.ndarray,
    k_matrix: np.ndarray,
    r: np.ndarray,
    t: np.ndarray,
) -> float:
    p = build_projection_matrix(k_matrix, r, t)

    x = np.append(point_3d, 1.0)

    proj = p @ x

    if abs(proj[2]) < 1e-9:
        return 1e9

    proj = proj[:2] / proj[2]

    return float(np.linalg.norm(proj - point_2d))


def _is_point_valid(pt: np.ndarray) -> bool:
    return (
        pt is not None
        and np.all(np.isfinite(pt))
        and np.linalg.norm(pt) < _MAX_POINT_DIST
    )


def _is_pose_valid(rvec: np.ndarray, tvec: np.ndarray) -> bool:
    return (
        np.all(np.isfinite(rvec))
        and np.all(np.isfinite(tvec))
        and np.linalg.norm(tvec) < _MAX_POINT_DIST
    )


# =========================================================
# INIT PAIR
# =========================================================


def _select_best_init_pair(
    matches_dict,
    kp_arrays,
    ransac_threshold,
    log,
):
    top_pairs = sorted(
        [p for p in matches_dict if len(matches_dict[p]) >= 80],
        key=lambda p: len(matches_dict[p]),
        reverse=True,
    )[:_INIT_PAIR_CANDIDATES]

    best_pair = None
    best_inliers = 0
    best_pts_a = None
    best_pts_b = None
    best_mask = None

    log.info("\tEvaluando pares iniciales...")

    for (i, j) in top_pairs:
        arr = matches_dict[(i, j)]

        pts_i = kp_arrays[i][arr[:, 0]].astype(np.float32)
        pts_j = kp_arrays[j][arr[:, 1]].astype(np.float32)

        f_tmp, mask_tmp = cv2.findFundamentalMat(
            pts_i,
            pts_j,
            cv2.FM_RANSAC,
            ransacReprojThreshold=ransac_threshold,
            confidence=0.999,
            maxIters=5000,
        )

        if f_tmp is None or mask_tmp is None:
            continue

        n_inliers = int(mask_tmp.sum())

        ratio = n_inliers / len(arr)

        log.info(
            "\tPar (%d,%d): %d matches -> %d inliers (%.2f%%)",
            i,
            j,
            len(arr),
            n_inliers,
            ratio * 100,
        )

        if n_inliers > best_inliers:
            best_pair = (i, j)
            best_inliers = n_inliers
            best_pts_a = pts_i
            best_pts_b = pts_j
            best_mask = mask_tmp

    if best_pair is None:
        raise RuntimeError("No se encontró un par inicial válido")

    sel = best_mask.ravel() == 1

    return (
        best_pair,
        best_pts_a[sel],
        best_pts_b[sel],
        best_inliers,
    )


# =========================================================
# MAIN PIPELINE
# =========================================================


def run_pipeline(
    dataset_name: str,
    output_dir: str | None = None,
    detector: str = "sift",
    lowe_ratio: float = 0.72,
    ransac_threshold: float = 1.0,
    min_matches: int = 8,
    log_file: str | None = "auto",
):

    t_total = time.perf_counter()

    log = PipelineLogger("sfm", verbose=True, log_file=log_file)

    registry = config.load_datasets_registry("data/datasets.yaml")

    dataset = config.get_dataset(registry, dataset_name)

    images_folder = Path(
        dataset.get("images_path")
        or Path(dataset["path"]) / "images"
    )

    intrinsics_path = Path(dataset["intrinsics"])

    out_dir = (
        Path(output_dir)
        if output_dir
        else Path("outputs") / dataset_name
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    k_matrix = load_intrinsics(intrinsics_path)

    image_paths = list_images(images_folder)

    n_imgs = len(image_paths)

    if n_imgs < 2:
        raise RuntimeError("Muy pocas imágenes")

    # =====================================================
    # FEATURES
    # =====================================================

    log.section("FEATURES")

    kp_arrays = []

    desc_arrays = []

    for idx, path in enumerate(image_paths):
        img = preprocess.load_image(path)

        gray = preprocess.to_grayscale(img)

        if detector == "orb":
            kps, des = features.detect_orb(gray)
        else:
            kps, des = features.detect_sift(gray)

        pts = features.keypoints_to_array(kps)

        kp_arrays.append(pts)

        desc_arrays.append(des)

        log.info("\tImagen %d -> %d keypoints", idx, len(pts))

    # =====================================================
    # MATCHING
    # =====================================================

    log.section("MATCHING")

    matches_dict = matching.match_windowed(
        desc_arrays=desc_arrays,
        detector=detector,
        ratio=lowe_ratio,
        window=WINDOW,
    )

    # =====================================================
    # INIT PAIR
    # =====================================================

    log.section("INIT PAIR")

    init_pair, pts_a_in, pts_b_in, n_inliers = (
        _select_best_init_pair(
            matches_dict,
            kp_arrays,
            ransac_threshold,
            log,
        )
    )

    cam_a, cam_b = init_pair

    log.info(
        "\tPar inicial (%d,%d) con %d inliers",
        cam_a,
        cam_b,
        n_inliers,
    )

    pts_a_all = kp_arrays[cam_a][
        matches_dict[init_pair][:, 0]
    ].astype(np.float32)

    pts_b_all = kp_arrays[cam_b][
        matches_dict[init_pair][:, 1]
    ].astype(np.float32)

    f_mat, mask_f = estimate_fundamental(
        pts_a_all,
        pts_b_all,
        ransac_threshold=ransac_threshold,
        verbose=True,
    )

    sel = mask_f.ravel() == 1

    pts_a_in = pts_a_all[sel]

    pts_b_in = pts_b_all[sel]

    pair0_in = matches_dict[init_pair][sel]

    e_mat = fundamental_to_essential(
        f_mat,
        k_matrix,
        verbose=True,
    )

    r_init, t_init, _ = recover_pose(
        e_mat,
        pts_a_in,
        pts_b_in,
        k_matrix,
        verbose=True,
    )

    # =====================================================
    # TRIANGULATION
    # =====================================================

    log.section("TRIANGULATION")

    r0 = np.eye(3)

    t0_vec = np.zeros((3, 1))

    p0 = build_projection_matrix(k_matrix, r0, t0_vec)

    p1 = build_projection_matrix(k_matrix, r_init, t_init)

    pts3d_raw, valid_tri = triangulation.triangulate_points(
        p0,
        p1,
        pts_a_in,
        pts_b_in,
    )

    pts3d = []

    pair_valid = []

    for idx, valid in enumerate(valid_tri):

        if not valid:
            continue

        pt3d = pts3d_raw[idx]

        if not _is_point_valid(pt3d):
            continue

        angle = compute_parallax_angle(
            pts_a_in[idx],
            pts_b_in[idx],
            k_matrix,
        )

        if angle < _MIN_PARALLAX_DEG:
            continue

        err1 = reprojection_error(
            pt3d,
            pts_a_in[idx],
            k_matrix,
            r0,
            t0_vec,
        )

        err2 = reprojection_error(
            pt3d,
            pts_b_in[idx],
            k_matrix,
            r_init,
            t_init,
        )

        if err1 > _MAX_REPROJ_ERROR:
            continue

        if err2 > _MAX_REPROJ_ERROR:
            continue

        pts3d.append(pt3d)

        pair_valid.append(pair0_in[idx])

    pts3d = np.array(pts3d)

    if len(pts3d) == 0:
        raise RuntimeError("No quedaron puntos válidos")

    log.info("\tPuntos válidos: %d", len(pts3d))

    # =====================================================
    # CAMERAS
    # =====================================================

    camera_rs = [None] * n_imgs

    camera_ts = [None] * n_imgs

    camera_rs[cam_a] = r0

    camera_ts[cam_a] = t0_vec

    camera_rs[cam_b] = r_init

    camera_ts[cam_b] = t_init

    cloud_pts = list(pts3d)

    kp_to_cloud = {}

    for idx, (ka, kb) in enumerate(pair_valid):
        kp_to_cloud[(cam_a, int(ka))] = idx
        kp_to_cloud[(cam_b, int(kb))] = idx

    # =====================================================
    # INCREMENTAL
    # =====================================================

    log.section("INCREMENTAL")

    pnp_ratios = []

    for i in range(n_imgs):

        if camera_rs[i] is not None:
            continue

        pts3d_pnp = []

        pts2d_pnp = []

        used = set()

        source_pairs = sorted(
            [
                (j, i)
                for (j, k) in matches_dict
                if k == i and camera_rs[j] is not None
            ],
            reverse=True,
        )

        for (j, _) in source_pairs:

            pair = matches_dict[(j, i)]

            for row in pair:

                kj = int(row[0])

                ki = int(row[1])

                cloud_idx = kp_to_cloud.get((j, kj))

                if cloud_idx is None:
                    continue

                if cloud_idx in used:
                    continue

                pt3d = cloud_pts[cloud_idx]

                if not _is_point_valid(pt3d):
                    continue

                pts3d_pnp.append(pt3d)

                pts2d_pnp.append(kp_arrays[i][ki])

                used.add(cloud_idx)

        if len(pts3d_pnp) < min_matches:
            log.warn("\tImagen %d: insuficientes corr", i)
            continue

        pts3d_pnp = np.array(pts3d_pnp, dtype=np.float64)

        pts2d_pnp = np.array(pts2d_pnp, dtype=np.float32)

        success, rvec, tvec, inliers = cv2.solvePnPRansac(
            pts3d_pnp,
            pts2d_pnp,
            k_matrix,
            None,
            reprojectionError=2.0,
            confidence=0.999,
            iterationsCount=5000,
        )

        if not success or inliers is None:
            continue

        if len(inliers) < 8:
            continue

        if not _is_pose_valid(rvec, tvec):
            continue

        r_i, _ = cv2.Rodrigues(rvec)

        t_i = tvec

        camera_rs[i] = r_i

        camera_ts[i] = t_i

        ratio = len(inliers) / len(pts3d_pnp)

        pnp_ratios.append(ratio)

        log.info(
            "\tCam %d registrada -> ratio %.2f",
            i,
            ratio,
        )

        # =============================================
        # TRIANGULATE NEW
        # =============================================

        prev_cam = max(
            [
                j
                for j in range(i)
                if camera_rs[j] is not None
            ]
        )

        pair_key = (prev_cam, i)

        if pair_key not in matches_dict:
            continue

        tri_pairs = matches_dict[pair_key]

        p_prev = build_projection_matrix(
            k_matrix,
            camera_rs[prev_cam],
            camera_ts[prev_cam],
        )

        p_curr = build_projection_matrix(
            k_matrix,
            camera_rs[i],
            camera_ts[i],
        )

        pts_prev = []

        pts_curr = []

        pair_indices = []

        for row in tri_pairs:

            kj = int(row[0])

            ki = int(row[1])

            if (prev_cam, kj) in kp_to_cloud:
                continue

            if (i, ki) in kp_to_cloud:
                continue

            pts_prev.append(kp_arrays[prev_cam][kj])

            pts_curr.append(kp_arrays[i][ki])

            pair_indices.append((kj, ki))

        if len(pts_prev) < 8:
            continue

        pts_prev = np.array(pts_prev, dtype=np.float32)

        pts_curr = np.array(pts_curr, dtype=np.float32)

        new_pts3d, valid_mask = triangulation.triangulate_points(
            p_prev,
            p_curr,
            pts_prev,
            pts_curr,
        )

        added = 0

        for idx, valid in enumerate(valid_mask):

            if not valid:
                continue

            pt3d = new_pts3d[idx]

            if not _is_point_valid(pt3d):
                continue

            angle = compute_parallax_angle(
                pts_prev[idx],
                pts_curr[idx],
                k_matrix,
            )

            if angle < _MIN_PARALLAX_DEG:
                continue

            err1 = reprojection_error(
                pt3d,
                pts_prev[idx],
                k_matrix,
                camera_rs[prev_cam],
                camera_ts[prev_cam],
            )

            err2 = reprojection_error(
                pt3d,
                pts_curr[idx],
                k_matrix,
                camera_rs[i],
                camera_ts[i],
            )

            if err1 > _MAX_REPROJ_ERROR:
                continue

            if err2 > _MAX_REPROJ_ERROR:
                continue

            cloud_idx = len(cloud_pts)

            cloud_pts.append(pt3d)

            kj, ki = pair_indices[idx]

            kp_to_cloud[(prev_cam, kj)] = cloud_idx

            kp_to_cloud[(i, ki)] = cloud_idx

            added += 1

        log.info("\tCam %d -> +%d puntos", i, added)

    # =====================================================
    # FINAL FILTER
    # =====================================================

    pts3d_all = np.array(cloud_pts)

    finite_mask = np.all(np.isfinite(pts3d_all), axis=1)

    dist_mask = (
        np.linalg.norm(pts3d_all, axis=1)
        < _MAX_POINT_DIST
    )

    pts3d_all = pts3d_all[finite_mask & dist_mask]

    if len(pts3d_all) > 0:

        q25 = np.percentile(pts3d_all, 25, axis=0)

        q75 = np.percentile(pts3d_all, 75, axis=0)

        iqr = q75 - q25

        iqr = np.where(iqr < 1e-9, 1.0, iqr)

        mask = np.all(
            (
                pts3d_all >= q25 - _IQR_FACTOR * iqr
            )
            &
            (
                pts3d_all <= q75 + _IQR_FACTOR * iqr
            ),
            axis=1,
        )

        pts3d_all = pts3d_all[mask]

    # =====================================================
    # METRICS
    # =====================================================

    all_errors = []

    for cam_idx in range(n_imgs):

        if camera_rs[cam_idx] is None:
            continue

        r = camera_rs[cam_idx]

        t = camera_ts[cam_idx]

        for (img_id, kp_id), cloud_idx in kp_to_cloud.items():

            if img_id != cam_idx:
                continue

            if cloud_idx >= len(cloud_pts):
                continue

            pt3d = cloud_pts[cloud_idx]

            pt2d = kp_arrays[img_id][kp_id]

            err = reprojection_error(
                pt3d,
                pt2d,
                k_matrix,
                r,
                t,
            )

            if np.isfinite(err):
                all_errors.append(err)

    rep_mean = float(np.mean(all_errors))

    rep_median = float(np.median(all_errors))

    valid_cams = sum(r is not None for r in camera_rs)

    mean_ratio = (
        float(np.mean(pnp_ratios))
        if pnp_ratios
        else 0.0
    )

    result = {
        "dataset": dataset_name,
        "num_images": valid_cams,
        "reprojection_error_mean": round(rep_mean, 4),
        "reprojection_error_median": round(rep_median, 4),
        "ransac_inlier_ratio": round(mean_ratio, 4),
        "num_3d_points": len(pts3d_all),
        "time_total": round(time.perf_counter() - t_total, 3),
    }

    # =====================================================
    # EXPORT
    # =====================================================

    ply_path = out_dir / "cloud.ply"

    metrics_path = out_dir / "metrics.json"

    export.write_ply(str(ply_path), pts3d_all)

    metrics.write_metrics_json(
        str(metrics_path),
        result,
    )

    log.summary({
        "Imagenes registradas":
            (valid_cams, valid_cams >= 2),

        "Puntos 3D":
            (len(pts3d_all), len(pts3d_all) > 100),

        "Reprojection error":
            (rep_mean, rep_mean < 5.0),
    })

    return result
