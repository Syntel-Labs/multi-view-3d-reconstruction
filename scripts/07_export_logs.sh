#!/usr/bin/env bash
# 07_export_logs.sh - Exporta logs de los contenedores mv3d a logs/.
# Acepta alias cortos (hartley, galileo) o "all".
# Uso:
#   ./scripts/07_export_logs.sh                     # todos los servicios
#   ./scripts/07_export_logs.sh hartley             # solo backend
#   ./scripts/07_export_logs.sh galileo 500         # frontend, ultimas 500 lineas
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
load_env

TARGET="${1:-all}"
TAIL="${2:-all}"

ALL_CONTAINERS=("mv3d-hartley" "mv3d-galileo")

LOGS_DIR="${PROJECT_DIR}/logs"
mkdir -p "${LOGS_DIR}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

export_container() {
  local container="$1"
  local outfile="${LOGS_DIR}/${container}_${TIMESTAMP}.log"

  if ! docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
    warn "Contenedor '${container}' no encontrado, omitiendo."
    return
  fi

  if [[ "$TAIL" == "all" ]]; then
    docker logs "${container}" > "${outfile}" 2>&1
  else
    docker logs --tail="${TAIL}" "${container}" > "${outfile}" 2>&1
  fi

  local lines
  lines=$(wc -l < "${outfile}")
  ok "${container} -> logs/${container}_${TIMESTAMP}.log (${lines} lineas)"
}

echo -e "\n${BOLD}${BLUE}[stack] Exportando logs a logs/...${RESET}\n"

case "$TARGET" in
  all)
    for c in "${ALL_CONTAINERS[@]}"; do
      export_container "$c"
    done
    ;;
  hartley|galileo)
    export_container "$(service_to_container "$TARGET")"
    ;;
  mv3d-*)
    export_container "$TARGET"
    ;;
  *)
    die "Target desconocido: '$TARGET'. Usa: hartley | galileo | all"
    ;;
esac

echo ""
info "Archivos en logs/:"
ls -lh "${LOGS_DIR}" | tail -n +2
