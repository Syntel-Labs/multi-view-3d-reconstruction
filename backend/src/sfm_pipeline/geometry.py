"""Geometria epipolar: matriz fundamental F, esencial E y recuperacion de pose.

Modulo de la persona B. Brecha del curso: algoritmo de 8 puntos y descomposicion de E con
verificacion de cheirality. Ver docs/course-references.md.
"""


def estimate_fundamental(points_a, points_b):
    """Estimar F con findFundamentalMat + RANSAC."""
    raise NotImplementedError


def fundamental_to_essential(fundamental, intrinsics_k):
    """Calcular E = K^T F K."""
    raise NotImplementedError


def recover_pose(essential, points_a, points_b, intrinsics_k):
    """Descomponer E en R y t con verificacion de cheirality."""
    raise NotImplementedError
