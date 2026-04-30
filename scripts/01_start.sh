#!/usr/bin/env bash
# 01_start.sh - Levanta el stack mv3d (hartley + galileo).
# Uso:
#   ./scripts/01_start.sh
#   ./scripts/01_start.sh --help
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

for arg in "$@"; do
  case "$arg" in
    --help) grep '^# ' "$0" | sed 's/^# //'; exit 0 ;;
    *)      die "Argumento desconocido: $arg" ;;
  esac
done

require_docker
require_compose_file
load_env

echo -e "\n${BOLD}${BLUE}[stack] Iniciando mv3d (hartley + galileo)...${RESET}\n"

dc down --remove-orphans 2>/dev/null || true
dc up -d --remove-orphans

echo ""
ok "Stack iniciado."
echo ""
dc ps
