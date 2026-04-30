#!/usr/bin/env bash
# 02_stop.sh - Detiene el stack mv3d.
# Uso:
#   ./scripts/02_stop.sh
set -euo pipefail
source "$(dirname "$0")/lib.sh"

require_docker
require_compose_file
load_env

echo -e "\n${BOLD}${BLUE}[stack] Deteniendo stack mv3d...${RESET}\n"
dc down --remove-orphans

echo ""
ok "Stack detenido. Los datos en ./data y ./outputs estan intactos."
