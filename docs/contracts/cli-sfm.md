# Contrato - CLI sfm

- Version: 0.1.0
- Productor: Persona B
- Consumidor: Persona C (lo invoca como subprocess desde el backend)

Define la interfaz CLI del pipeline.

## Invocacion

Dentro del contenedor `mv3d-hartley`:

```bash
python -m sfm_pipeline.cli --dataset <name> [--output <ruta>]
```

Desde host con make:

```bash
make pipeline DATASET=<name>
```

## Argumentos

| Argumento | Obligatorio | Default | Descripcion |
| :--- | :--- | :--- | :--- |
| `--dataset` | si | - | Nombre del dataset (debe existir en `data/datasets.yaml`). |
| `--output` | no | `outputs/<dataset>/` | Carpeta destino. |

## Salidas

- `outputs/<dataset>/cloud.ply` (ver [`cloud-ply.md`](cloud-ply.md)).
- `outputs/<dataset>/metrics.json` (ver [`metrics-json.md`](metrics-json.md)).
- `outputs/<dataset>/logs/<timestamp>.log` con la traza del job.

## Codigos de salida

| Codigo | Significado |
| :--- | :--- |
| 0 | Reconstruccion completada sin errores. |
| 1 | Error generico (excepcion no controlada). |
| 2 | Dataset no encontrado en `datasets.yaml`. |
| 3 | Error en validacion de inputs (imagenes faltantes, intrinsics invalido, etc.). |
| 4 | Reprojection error supero el umbral configurado (degradado, no critico). |

## Endpoint HTTP equivalente

`POST /reconstruct` del backend invoca este CLI internamente. Ver `backend/src/sfm_pipeline/api/server.py`.
