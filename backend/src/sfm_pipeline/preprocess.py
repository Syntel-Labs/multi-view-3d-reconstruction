"""Preprocesamiento de imagenes: carga, conversion a grises y filtrado Gaussiano.

Modulo de la persona A. Contrato: docs/contracts/matches-npz.md.
"""


def load_image(image_path: str):
    """Cargar imagen desde disco respetando BGR de OpenCV."""
    raise NotImplementedError


def to_grayscale(image):
    """Convertir BGR a escala de grises."""
    raise NotImplementedError


def gaussian_blur(image, kernel_size: int = 5, sigma: float = 1.0):
    """Aplicar filtro Gaussiano para reducir ruido antes de la deteccion de keypoints."""
    raise NotImplementedError
