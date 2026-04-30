#!/usr/bin/env bash
# 03_restart.sh - Reinicia el stack o un contenedor especifico.
# Acepta alias cortos (hartley, galileo) o el nombre completo (mv3d-*).
# Uso:
#   ./scripts/03_restart.sh            # reinicia todo
#   ./scripts/03_restart.sh hartley    # solo backend
#   ./scripts/03_restart.sh galileo    # solo frontend
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
require_compose_file
load_env

INPUT="${1:-}"

if [[ -n "$INPUT" ]]; then
  case "$INPUT" in
    hartley|galileo)  CONTAINER="$(service_to_container "$INPUT")" ;;
    mv3d-*)           CONTAINER="$INPUT" ;;
    *) die "Argumento desconocido: $INPUT. Uso: [hartley|galileo]" ;;
  esac

  if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    die "El contenedor '${CONTAINER}' no esta corriendo."
  fi
  echo -e "\n${BOLD}${BLUE}[stack] Reiniciando contenedor: ${CONTAINER}...${RESET}\n"
  docker restart "${CONTAINER}"
else
  echo -e "\n${BOLD}${BLUE}[stack] Reiniciando stack completo...${RESET}\n"
  dc down --remove-orphans
  dc up -d --remove-orphans
fi

echo ""
ok "Reiniciado correctamente."
echo ""
dc ps
