#!/usr/bin/env bash
# 11_clean.sh - Limpia contenedores, redes y volumenes del stack mv3d.
# No toca data/ ni outputs/ (estos viven fuera de los volumenes).
# Uso:
#   ./scripts/11_clean.sh
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
require_compose_file
load_env

echo -e "\n${BOLD}${YELLOW}[stack] Limpiando contenedores, redes y volumenes mv3d...${RESET}\n"
dc down -v --remove-orphans

echo ""
ok "Limpieza completada. Las carpetas data/ y outputs/ se mantienen."
