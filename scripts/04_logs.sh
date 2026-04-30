#!/usr/bin/env bash
# 04_logs.sh - Sigue los logs de un contenedor del stack mv3d.
# Acepta alias cortos (hartley, galileo) o el nombre completo (mv3d-*).
# Uso:
#   ./scripts/04_logs.sh hartley           # backend
#   ./scripts/04_logs.sh galileo           # frontend
#   ./scripts/04_logs.sh hartley 500       # ultimas 500 lineas
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
load_env

INPUT="${1:-}"
TAIL="${2:-200}"

[[ -z "$INPUT" ]] && die "Uso: ./04_logs.sh hartley | galileo [tail]"

if [[ "$INPUT" == mv3d-* ]]; then
  CONTAINER="$INPUT"
else
  CONTAINER="$(service_to_container "$INPUT")"
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  die "El contenedor '${CONTAINER}' no esta corriendo. Arrancaste el stack?"
fi

echo -e "\n${BOLD}${BLUE}[stack] Logs de ${CONTAINER} (ultimas ${TAIL} lineas)...${RESET}\n"
docker logs -f --tail="${TAIL}" "${CONTAINER}"
