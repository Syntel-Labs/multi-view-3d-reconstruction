from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_image(image_path: str | Path, grayscale: bool = False) -> np.ndarray:
    """Cargar imagen desde disco respetando el canal BGR de OpenCV.

    Args:
        image_path: Ruta al archivo de imagen.
        grayscale: Si es True carga directamente en escala de grises.

    Returns:
        Array NumPy con la imagen (H, W, 3) BGR o (H, W) si grayscale.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
        ValueError: Si OpenCV no puede decodificar el archivo como imagen.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        msg = f"No se encontro el archivo de imagen: {image_path}"
        raise FileNotFoundError(msg)

    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(str(image_path), flag)
    if img is None:
        msg = f"OpenCV no pudo decodificar la imagen: {image_path}"
        raise ValueError(msg)
    return img


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convertir una imagen BGR a escala de grises.

    Si la imagen ya es de un canal (2D) se devuelve sin modificacion
    para evitar una conversion innecesaria.

    Args:
        image: Array NumPy (H, W, 3) BGR o (H, W) gris.

    Returns:
        Array NumPy (H, W) en escala de grises.
    """
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def gaussian_blur(image: np.ndarray, kernel_size: int = 5, sigma: float = 1.0) -> np.ndarray:
    """Aplicar filtro Gaussiano para reducir ruido antes de la deteccion de keypoints.

    Args:
        image: Array NumPy de la imagen (cualquier numero de canales).
        kernel_size: Tamano del kernel; debe ser impar. Si se recibe un valor
            par se incrementa en 1 automaticamente.
        sigma: Desviacion estandar del kernel Gaussiano.

    Returns:
        Imagen suavizada con el mismo shape y dtype que la entrada.
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
