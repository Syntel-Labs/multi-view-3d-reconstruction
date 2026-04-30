"""Deteccion y descripcion de keypoints con SIFT y ORB.

Modulo de la persona A. Contrato: docs/contracts/matches-npz.md.
"""


def detect_sift(image_gray):
    """Detectar keypoints y calcular descriptores SIFT."""
    raise NotImplementedError


def detect_orb(image_gray, n_features: int = 5000):
    """Detectar keypoints y calcular descriptores ORB."""
    raise NotImplementedError
