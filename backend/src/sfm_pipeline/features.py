from __future__ import annotations

import cv2
import numpy as np


def detect_sift(
    image_gray: np.ndarray,
    n_features: int = 0,
) -> tuple[list, np.ndarray]:
    """Detectar keypoints y calcular descriptores SIFT sobre una imagen en grises.

    Args:
        image_gray: Array NumPy (H, W) uint8 en escala de grises.
        n_features: Numero maximo de keypoints a retener; 0 significa sin limite.

    Returns:
        Tupla (keypoints, descriptors) donde keypoints es una lista de
        cv2.KeyPoint y descriptors es un array (N, 128) float32.

    Raises:
        ValueError: Si SIFT no produce descriptores (imagen sin textura o uniforme).
    """
    sift = cv2.SIFT_create(nfeatures=n_features)
    keypoints, des = sift.detectAndCompute(image_gray, None)
    if des is None:
        msg = "SIFT no produjo descriptores; la imagen puede carecer de textura."
        raise ValueError(msg)
    return list(keypoints), des


def detect_orb(
    image_gray: np.ndarray,
    n_features: int = 1000,
) -> tuple[list, np.ndarray]:
    """Detectar keypoints y calcular descriptores ORB sobre una imagen en grises.

    Args:
        image_gray: Array NumPy (H, W) uint8 en escala de grises.
        n_features: Numero maximo de keypoints a retener.

    Returns:
        Tupla (keypoints, descriptors) donde keypoints es una lista de
        cv2.KeyPoint y descriptors es un array (N, 32) uint8.

    Raises:
        ValueError: Si ORB no produce descriptores (imagen sin textura o uniforme).
    """
    orb = cv2.ORB_create(nfeatures=n_features)
    keypoints, des = orb.detectAndCompute(image_gray, None)
    if des is None:
        msg = "ORB no produjo descriptores; la imagen puede carecer de textura."
        raise ValueError(msg)
    return list(keypoints), des


def keypoints_to_array(keypoints: list) -> np.ndarray:
    """Convertir una lista de cv2.KeyPoint a un array de coordenadas (x, y).

    Args:
        keypoints: Lista de objetos cv2.KeyPoint.

    Returns:
        Array (N, 2) float32 con las coordenadas pixel (x, y) de cada keypoint.
        Si la lista esta vacia retorna un array de forma (0, 2) float32.
    """
    if not keypoints:
        return np.empty((0, 2), dtype=np.float32)
    return np.array([kp.pt for kp in keypoints], dtype=np.float32)
