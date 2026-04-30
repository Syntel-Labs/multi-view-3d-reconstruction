"""Calculo de metricas del pipeline: reprojection error, inlier ratio y tiempos por etapa.

Modulo de la persona B. Contrato: docs/contracts/metrics-json.md.
"""


def reprojection_error(points_3d, points_2d, projection_matrix) -> float:
    """Calcular error de reproyeccion en pixeles."""
    raise NotImplementedError


def write_metrics_json(output_path: str, payload: dict) -> None:
    """Persistir metrics.json siguiendo el schema del contrato."""
    raise NotImplementedError
