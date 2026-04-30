#!/usr/bin/env bash
# 10_build.sh - Construir las imagenes docker del stack mv3d.
# Uso:
#   ./scripts/10_build.sh                      # build de todo
#   ./scripts/10_build.sh hartley              # solo backend
#   ./scripts/10_build.sh galileo              # solo frontend
#   ./scripts/10_build.sh --no-cache           # sin cache
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
require_compose_file
load_env

echo -e "\n${BOLD}${BLUE}[stack] Construyendo imagenes mv3d...${RESET}\n"
dc build "$@"

echo ""
ok "Build completado."
