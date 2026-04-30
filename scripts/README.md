# Scripts

Scripts shell para operar el stack `mv3d` (hartley + galileo). Contrato basico: `set -euo pipefail`, helpers desde `lib.sh`, `--help` por convencion, y aborto explicito con `die` ante requisitos faltantes.

## Convenciones

- `set -euo pipefail` obligatorio.
- `source "$(dirname "$0")/lib.sh"` para cargar helpers, colores, wrapper de `docker compose` y resolver alias de servicios.

## Listado

| Script | Proposito | Uso |
| :--- | :--- | :--- |
| `lib.sh` | Helpers compartidos. **No ejecutar directamente**. | `source` desde otros scripts. |
| `01_start.sh` | Levantar stack en background. | `./scripts/01_start.sh` |
| `02_stop.sh` | Detener stack. | `./scripts/02_stop.sh` |
| `03_restart.sh` | Reiniciar stack o servicio. | `./scripts/03_restart.sh [hartley\|galileo]` |
| `04_logs.sh` | Tail de logs por servicio. | `./scripts/04_logs.sh hartley [tail]` |
| `05_shell.sh` | Shell interactivo en un contenedor. | `./scripts/05_shell.sh hartley` |
| `06_pipeline.sh` | Correr pipeline SfM por CLI. | `./scripts/06_pipeline.sh <dataset>` |
| `07_export_logs.sh` | Exportar logs a `logs/`. | `./scripts/07_export_logs.sh [target] [tail]` |
| `08_build.sh` | Construir imagenes docker. | `./scripts/08_build.sh [servicio]` |
| `09_clean.sh` | Limpiar contenedores, redes y volumenes. | `./scripts/09_clean.sh` |

## Aliases de servicios

Definidos en `lib.sh`:

| Alias | Container | Descripcion |
| :--- | :--- | :--- |
| `hartley` | `mv3d-hartley` | Backend FastAPI + pipeline SfM (Python 3.12 + OpenCV). |
| `galileo` | `mv3d-galileo` | Frontend Three.js + Vite (pnpm). |

Los scripts aceptan tanto el alias corto como el nombre completo del contenedor.

## Equivalencias con Makefile

El `Makefile` en la raiz expone los mismos blancos como atajos. Los scripts existen para uso sin `make` instalado y para pipelines de CI.

| Script | Make |
| :--- | :--- |
| `08_build.sh` | `make build` |
| `01_start.sh` | `make up` |
| `02_stop.sh` | `make down` |
| `04_logs.sh hartley` | `make logs-backend` |
| `05_shell.sh hartley` | `make shell-backend` |
| `06_pipeline.sh <name>` | `make pipeline DATASET=<name>` |
| `09_clean.sh` | `make clean` |
