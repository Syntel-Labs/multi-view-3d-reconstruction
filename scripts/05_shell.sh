#!/usr/bin/env bash
# 05_shell.sh - Shell interactiva dentro de un contenedor del stack mv3d.
# Acepta alias cortos (hartley, galileo) o el nombre completo (mv3d-*).
# Uso:
#   ./scripts/05_shell.sh hartley
#   ./scripts/05_shell.sh galileo
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
load_env

INPUT="${1:-}"
[[ -z "$INPUT" ]] && die "Uso: ./05_shell.sh hartley | galileo"

if [[ "$INPUT" == mv3d-* ]]; then
  CONTAINER="$INPUT"
else
  CONTAINER="$(service_to_container "$INPUT")"
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  die "El contenedor '${CONTAINER}' no esta corriendo. Arrancaste el stack?"
fi

# Preferir bash; caer a sh si no esta disponible.
if docker exec "${CONTAINER}" bash -c "exit" 2>/dev/null; then
  SHELL_CMD="bash"
else
  SHELL_CMD="sh"
fi

echo -e "\n${BOLD}${BLUE}[stack] Shell (${SHELL_CMD}) en ${CONTAINER}...${RESET}"

case "$INPUT" in
  hartley|mv3d-hartley)
    echo -e "${YELLOW}Tip: corre el pipeline con 'python -m sfm_pipeline.cli --dataset <name>'${RESET}\n" ;;
  galileo|mv3d-galileo)
    echo -e "${YELLOW}Tip: 'pnpm install' para deps; 'pnpm dev' ya corre por defecto${RESET}\n" ;;
esac

docker exec -it "${CONTAINER}" "${SHELL_CMD}"
