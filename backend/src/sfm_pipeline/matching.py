"""Matching de descriptores con BFMatcher + Lowe's ratio test.

Modulo de la persona A. Contrato: docs/contracts/matches-npz.md.
"""


def match_descriptors(descriptors_a, descriptors_b, ratio: float = 0.75):
    """Hacer matching cruzado y filtrar con Lowe's ratio test."""
    raise NotImplementedError


def save_matches_npz(output_path: str, payload: dict) -> None:
    """Empaquetar keypoints, descriptores y matches en el formato del contrato matches.npz."""
    raise NotImplementedError
