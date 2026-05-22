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


def match_windowed(
    desc_arrays: list[np.ndarray],
    detector: str = "sift",
    ratio: float = 0.75,
    window: int = 3,
) -> dict[tuple[int, int], np.ndarray]:
    """Matchear cada imagen contra sus `window` vecinas siguientes.

    En vez de emparejar solo (i, i+1), genera pares (i, i+1), (i, i+2) …
    hasta (i, i+window), lo que permite que SfM encuentre correspondencias
    3D-2D incluso cuando el par inmediato tiene poco solapamiento.

    Args:
        desc_arrays: Lista de arrays (N_i, D) con descriptores de cada imagen.
            Un array None o vacío en la posición i hace que todos los pares
            que lo involucran se omitan silenciosamente.
        detector: "sift" (NORM_L2) u "orb" (NORM_HAMMING).
        ratio: Umbral del test de ratio de Lowe.
        window: Número de vecinos futuros a considerar (≥ 1).
            window=1 equivale al comportamiento consecutivo original.

    Returns:
        Diccionario {(i, j): array (M, 2) int32} donde cada fila contiene
        el índice de keypoint en la imagen i y el índice en la imagen j.
        Solo se incluyen pares con al menos un match válido.
    """
    if window < 1:
        raise ValueError(f"window debe ser >= 1, recibido: {window}")

    norm_type = cv2.NORM_HAMMING if detector == "orb" else cv2.NORM_L2
    matcher = cv2.BFMatcher(norm_type, crossCheck=False)

    results: dict[tuple[int, int], np.ndarray] = {}
    n = len(desc_arrays)

    for i in range(n):
        desc_i = desc_arrays[i]
        if desc_i is None or len(desc_i) == 0:
            continue

        for j in range(i + 1, min(i + window + 1, n)):
            desc_j = desc_arrays[j]
            if desc_j is None or len(desc_j) == 0:
                continue

            # knnMatch requiere al menos 2 descriptores en la imagen B
            if len(desc_j) < 2:
                continue

            raw = matcher.knnMatch(desc_i, desc_j, k=2)

            good = [
                (m.queryIdx, m.trainIdx)
                for m, n_match in raw
                if m.distance < ratio * n_match.distance
            ]

            if good:
                results[(i, j)] = np.array(good, dtype=np.int32)

    return results


def save_matches_npz(
    output_path: str | Path,
    image_paths: list[str],
    keypoints_list: list[np.ndarray],
    descriptors_list: list[np.ndarray],
    matches_pairs: dict[tuple[int, int], np.ndarray] | list[np.ndarray],
    detector: str,
    lowe_ratio: float,
) -> None:
    """Guardar keypoints, descriptores y matches en formato .npz segun el contrato.

    Acepta tanto el formato antiguo (lista de arrays para pares consecutivos)
    como el nuevo (diccionario {(i, j): array} de match_windowed).

    Args:
        output_path: Ruta de destino del archivo .npz.
        image_paths: Lista de rutas relativas a las imagenes del dataset.
        keypoints_list: Lista de arrays (N_i, 2) float32 con coordenadas (x, y).
        descriptors_list: Lista de arrays (N_i, D) con los descriptores de cada imagen.
        matches_pairs: Dict {(i, j): array (M, 2) int32} (salida de match_windowed)
            o lista de arrays para pares consecutivos (compatibilidad hacia atrás).
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

    # Soporte tanto para dict (windowed) como para list (consecutivo)
    if isinstance(matches_pairs, dict):
        for (i, j), match_array in matches_pairs.items():
            payload[f"matches_{i}_{j}"] = match_array
    else:
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
