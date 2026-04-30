# Backend - mv3d-hartley

Servicio Python 3.12 con el pipeline clasico Structure from Motion y la API FastAPI que expone el endpoint de reconstruccion al frontend.

## Estructura

```text
backend/
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── scripts/                    # scripts Python de uso unico (orb_test.py, etc.)
└── src/
    └── sfm_pipeline/
        ├── __init__.py
        ├── config.py           # carga de .env y datasets.yaml
        ├── preprocess.py       # filtrado y conversion a grises (Persona A)
        ├── features.py         # SIFT / ORB (Persona A)
        ├── matching.py         # BFMatcher + Lowe ratio test (Persona A)
        ├── geometry.py         # F, E, recoverPose (Persona B)
        ├── triangulation.py    # DLT (Persona B)
        ├── sfm.py              # multi-vista incremental (Persona B)
        ├── export.py           # exportacion .ply (Persona B)
        ├── metrics.py          # reprojection error y metricas (Persona B)
        ├── cli.py              # CLI entrypoint
        └── api/
            └── server.py       # FastAPI app (Persona C)
```

## Modulos y responsables

| Modulo | Responsable | Documentacion |
| :--- | :--- | :--- |
| `preprocess.py`, `features.py`, `matching.py` | A | `docs/contracts/matches-npz.md` |
| `geometry.py`, `triangulation.py`, `sfm.py`, `export.py`, `metrics.py` | B | `docs/contracts/cloud-ply.md`, `docs/contracts/metrics-json.md` |
| `api/server.py`, `cli.py` integracion | C | `docs/contracts/cli-sfm.md` |

## Comandos

Dentro del contenedor `mv3d-hartley` (entrar con `make shell-backend`):

```bash
python -m sfm_pipeline.cli --dataset gamecube
ruff check src
```

Desde host con make:

```bash
make pipeline DATASET=gamecube
make lint
```

## Variables de entorno

Definidas en `.env` (ver `.env.example` en la raiz). Las usadas por el backend son `DATA_DIR`, `OUTPUTS_DIR`, `DATASETS_CONFIG`, `BACKEND_HOST`, `BACKEND_INTERNAL_PORT`, `LOG_LEVEL`.
