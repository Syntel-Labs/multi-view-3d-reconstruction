# multi-view-3d-reconstruction

Pipeline clasico de Structure from Motion (SfM) para reconstruir geometria 3D a partir de multiples fotografias, con demo web. Proyecto final del curso CC3045 - Vision por Computadora.

Documentacion completa en [docs/](docs/README.md).

## Stack

- Backend: Python 3.12 + OpenCV + FastAPI (contenedor `mv3d-hartley`).
- Frontend: Three.js + Vite + pnpm (contenedor `mv3d-galileo`).
- Orquestacion: Docker Compose con red `mv3d-observatory`.

## Estructura

```text
multi-view-3d-reconstruction/
├── backend/        # pipeline SfM y API FastAPI (Python 3.12)
├── frontend/       # visor Three.js + Vite (pnpm)
├── data/           # datasets de entrada (mapeados en data/datasets.yaml)
├── outputs/        # nubes .ply y metricas generadas
├── scripts/        # scripts de uso unico para Docker y pipeline
├── docs/           # plan, contratos, bitacoras, prompts, presentacion, final
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Requisitos

- Docker Desktop o Docker Engine + Docker Compose v2.
- Make (opcional, para los atajos del Makefile).

## Primer arranque

```bash
cp .env.example .env
make build
make up
```

- Backend: <http://localhost:8000>
- Frontend: <http://localhost:5173>

## Comandos comunes

```bash
make help              # listar todos los comandos
make logs              # ver logs en tiempo real
make shell-backend     # shell dentro de mv3d-hartley
make pipeline DATASET=object-360   # correr pipeline CLI sobre un dataset
make down              # detener stack
make clean             # limpiar contenedores, redes y volumenes
```

## Datasets

Cada dataset vive en `data/<name>/` con `images/`, `intrinsics.json` y `README.md`. El registro central esta en [`data/datasets.yaml`](data/datasets.yaml).

## Equipo y plan

Roles, contratos de interfaz, cronograma y entregas en [`docs/plan.md`](docs/plan.md).
