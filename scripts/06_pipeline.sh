#!/usr/bin/env bash
# 06_pipeline.sh - Corre el pipeline SfM por CLI sobre un dataset registrado.
# Reemplaza al antiguo install_model.sh del stack n8n.
# Uso:
#   ./scripts/06_pipeline.sh <dataset_name>
#   ./scripts/06_pipeline.sh object-360
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
load_env

DATASET="${1:-}"
[[ -z "$DATASET" ]] && die "Uso: ./06_pipeline.sh <dataset_name>"

CONTAINER="$(service_to_container "hartley")"
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  die "El contenedor '${CONTAINER}' no esta corriendo. Ejecuta ./scripts/01_start.sh primero."
fi

echo -e "\n${BOLD}${BLUE}[${CONTAINER}] Pipeline SfM sobre dataset: ${DATASET}${RESET}\n"

docker exec -it "${CONTAINER}" python -m sfm_pipeline.cli --dataset "${DATASET}"

echo ""
ok "Pipeline completado para dataset: ${DATASET}"
echo ""
info "Resultados esperados en outputs/${DATASET}/"
