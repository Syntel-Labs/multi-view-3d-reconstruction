# Contrato - metrics.json

- Version: 0.1.0
- Productor: Persona B
- Consumidores: Persona C, Persona D

Define el archivo de metricas que acompana a cada `cloud.ply`.

## Ubicacion

```text
outputs/<name>/metrics.json
```

## Schema

```json
{
  "dataset": "string",
  "num_images": 0,
  "reprojection_error_mean": 0.0,
  "reprojection_error_median": 0.0,
  "ransac_inlier_ratio": 0.0,
  "num_3d_points": 0,
  "time_per_stage_seconds": {
    "features": 0.0,
    "matching": 0.0,
    "geometry": 0.0,
    "triangulation": 0.0,
    "multiview": 0.0
  }
}
```

## Reglas

- `reprojection_error_mean` y `reprojection_error_median` en pixeles.
- `ransac_inlier_ratio` en `[0, 1]`.
- `time_per_stage_seconds` debe sumar aproximadamente al tiempo total del job.
- Cualquier campo nuevo se agrega como opcional; eliminar campos requiere bumping de version.
