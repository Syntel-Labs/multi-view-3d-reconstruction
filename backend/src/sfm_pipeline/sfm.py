"""Pipeline incremental multi-vista que orquesta features, matching, geometria y triangulacion.

Modulo de la persona B. Salida: outputs/<nombre>/cloud.ply + metrics.json.
"""


def run_pipeline(dataset_name: str, output_dir: str) -> dict:
    """Ejecutar el pipeline SfM completo sobre un dataset registrado en datasets.yaml.

    Args:
        dataset_name: Nombre del dataset declarado en data/datasets.yaml.
        output_dir: Carpeta destino para cloud.ply y metrics.json.

    Returns:
        Resumen con metricas finales (numero de puntos, error de reproyeccion, etc.).
    """
    raise NotImplementedError
