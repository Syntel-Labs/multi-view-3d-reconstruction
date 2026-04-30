#!/usr/bin/env bash
# lib.sh - utilidades compartidas por todos los scripts del stack mv3d.
# NO ejecutar directamente. Se importa con: source "$(dirname "$0")/lib.sh"

# Colores
BLUE="\e[34m"; GREEN="\e[32m"; RED="\e[31m"
YELLOW="\e[33m"; BOLD="\e[1m"; RESET="\e[0m"

# Rutas
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPTS_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
ENV_FILE="${PROJECT_DIR}/.env"
ENV_EXAMPLE_FILE="${PROJECT_DIR}/.env.example"

# Stack - prefijo mv3d-* para los contenedores (y la red mv3d-observatory).
STACK_PREFIX="mv3d"

# Alias internos (DNS en la red observatory) -> contenedores en `docker ps`:
#   hartley  -> mv3d-hartley  (backend SfM, FastAPI + OpenCV)
#   galileo  -> mv3d-galileo  (frontend Three.js + Vite)
STACK_SERVICES=("hartley" "galileo")

service_to_container() {
  local svc="$1"
  [[ -z "$svc" ]] && { echo ""; return; }
  echo "${STACK_PREFIX}-${svc}"
}

# Helpers
die()  { echo -e "${RED}[ERROR] $*${RESET}" >&2; exit 1; }
info() { echo -e "${BLUE}[stack]${RESET} $*"; }
ok()   { echo -e "${GREEN}[OK]${RESET} $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET} $*"; }

# Preflight
require_docker() {
  command -v docker >/dev/null 2>&1 || die "Docker no esta instalado."
  docker info >/dev/null 2>&1      || die "El daemon de Docker no esta corriendo."
}

require_compose_file() {
  [[ -f "${COMPOSE_FILE}" ]] || die "No se encontro: ${COMPOSE_FILE}"
}

require_env_file() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    warn ".env no encontrado. Copiando desde .env.example..."
    [[ -f "${ENV_EXAMPLE_FILE}" ]] \
      || die "Tampoco existe .env.example. Revisa la instalacion."
    cp "${ENV_EXAMPLE_FILE}" "${ENV_FILE}"
    warn "Revisa y ajusta ${ENV_FILE} antes de continuar."
    exit 1
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "$1 no esta instalado."
}

# Carga el .env sin exportar variables innecesarias al shell padre.
load_env() {
  require_env_file
  # shellcheck disable=SC2046
  export $(grep -v '^\s*#' "${ENV_FILE}" | grep -v '^\s*$' | xargs)
}

# Compose wrapper.
dc() {
  docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
}
