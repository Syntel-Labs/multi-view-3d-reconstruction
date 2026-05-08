from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def match_descriptors(
    descriptors_a: np.ndarray,
    descriptors_b: np.ndarray,
    detector: str = "sift",
    ratio: float = 0.75,
) -> list:
    """Emparejar descriptores con BFMatcher y filtrar con el test de ratio de Lowe.

    Args:
        descriptors_a: Array (N, D) de descriptores de la imagen A.
        descriptors_b: Array (M, D) de descriptores de la imagen B.
        detector: Tipo de detector usado; "sift" usa NORM_L2, "orb" usa NORM_HAMMING.
        ratio: Umbral del test de ratio de Lowe; valor tipico 0.75.

    Returns:
        Lista de cv2.DMatch que superaron el test de ratio.

    Raises:
        ValueError: Si alguno de los arrays de descriptores es None o esta vacio.
    """
    if descriptors_a is None or len(descriptors_a) == 0:
        msg = "descriptors_a es None o esta vacio."
        raise ValueError(msg)
    if descriptors_b is None or len(descriptors_b) == 0:
        msg = "descriptors_b es None o esta vacio."
        raise ValueError(msg)

    norm_type = cv2.NORM_HAMMING if detector == "orb" else cv2.NORM_L2
    matcher = cv2.BFMatcher(norm_type, crossCheck=False)

    raw_matches = matcher.knnMatch(descriptors_a, descriptors_b, k=2)

    good_matches = [
        m
        for m, n in raw_matches
        if m.distance < ratio * n.distance
    ]
    return good_matches


def save_matches_npz(
    output_path: str | Path,
    image_paths: list[str],
    keypoints_list: list[np.ndarray],
    descriptors_list: list[np.ndarray],
    matches_pairs: list[np.ndarray],
    detector: str,
    lowe_ratio: float,
) -> None:
    """Guardar keypoints, descriptores y matches en formato .npz segun el contrato.

    Los pares de matches se guardan con clave matches_<i>_<j> para pares
    consecutivos (i, i+1).

    Args:
        output_path: Ruta de destino del archivo .npz.
        image_paths: Lista de rutas relativas a las imagenes del dataset.
        keypoints_list: Lista de arrays (N_i, 2) float32 con coordenadas (x, y).
        descriptors_list: Lista de arrays (N_i, D) con los descriptores de cada imagen.
        matches_pairs: Lista de arrays (M, 2) int32 con indices de keypoints por par
            consecutivo; el elemento k corresponde al par (k, k+1).
        detector: Nombre del detector usado ("sift" o "orb").
        lowe_ratio: Umbral de ratio de Lowe aplicado durante el matching.

    Returns:
        None
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, object] = {
        "image_paths": np.array(image_paths),
        "detector": detector,
        "lowe_ratio": np.float32(lowe_ratio),
    }

    for i, kps in enumerate(keypoints_list):
        payload[f"keypoints_{i}"] = kps

    for i, desc in enumerate(descriptors_list):
        payload[f"descriptors_{i}"] = desc

    for k, match_array in enumerate(matches_pairs):
        payload[f"matches_{k}_{k + 1}"] = match_array

    np.savez_compressed(str(output_path), **payload)


def load_matches_npz(path: str | Path) -> dict:
    """Cargar un archivo matches.npz y reconstruir su contenido como diccionario.

    Args:
        path: Ruta al archivo .npz generado por save_matches_npz.

    Returns:
        Diccionario con las claves del contrato: image_paths (lista Python),
        detector (str), lowe_ratio (float), keypoints_<i>, descriptors_<i>
        y matches_<i>_<j> como arrays NumPy.
    """
    archive = np.load(str(path), allow_pickle=False)
    result: dict = {}

    for key in archive.files:
        if key == "image_paths":
            result[key] = archive[key].tolist()
        elif key == "detector":
            result[key] = str(archive[key])
        elif key == "lowe_ratio":
            result[key] = float(archive[key])
        else:
            result[key] = archive[key]

    return result
