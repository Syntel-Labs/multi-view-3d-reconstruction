# Makefile -- comandos del stack mv3d (multi-view-3d-reconstruction)
# Servicios: hartley (backend SfM), galileo (frontend Three.js).

SHELL := /bin/bash

# =========================================================
# DEFAULTS — sobreescribibles desde la línea de comandos
# =========================================================
DATASET   ?= mi_dataset
DETECTOR  ?= sift
LOWE      ?= 0.75
RANSAC    ?= 1.0
MINMATCH  ?= 8
WINDOW    ?= 20
IQR       ?= 2.0
MAXREPROJ ?= 8.0
PARALLAX  ?= 0.01
NFEATURES ?= 4000

.PHONY: help build up up-fg down restart logs logs-backend logs-frontend ps \
        shell-backend shell-frontend pipeline lint lint-fix clean reset \
        install-frontend install-backend

# =========================================================
# AYUDA
# =========================================================

help: ## Listar comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# =========================================================
# STACK
# =========================================================

build: ## Construir imagenes docker
	docker compose build

up: ## Levantar stack en background
	docker compose up -d

up-fg: ## Levantar stack en foreground
	docker compose up

down: ## Detener stack
	docker compose down

restart: ## Reiniciar servicios
	docker compose restart

# =========================================================
# LOGS
# =========================================================

logs: ## Ver logs en tiempo real (todos los servicios)
	docker compose logs -f

logs-backend: ## Ver logs del backend (hartley)
	docker compose logs -f hartley

logs-frontend: ## Ver logs del frontend (galileo)
	docker compose logs -f galileo

# =========================================================
# UTILIDADES
# =========================================================

ps: ## Ver estado de servicios
	docker compose ps

shell-backend: ## Abrir shell en backend
	docker compose exec hartley sh

shell-frontend: ## Abrir shell en frontend
	docker compose exec galileo sh

# =========================================================
# PIPELINE SfM
# Uso: make pipeline DATASET=<nombre> [DETECTOR=sift|orb]
#        [LOWE=0.75] [RANSAC=1.0] [MINMATCH=8]
#        [WINDOW=20] [IQR=2.0] [MAXREPROJ=8.0]
#        [PARALLAX=0.01] [NFEATURES=4000]
# =========================================================

pipeline: ## Correr pipeline SfM
	docker compose exec hartley python -m sfm_pipeline.cli \
		--dataset          $(DATASET)   \
		--detector         $(DETECTOR)  \
		--lowe-ratio       $(LOWE)      \
		--ransac-threshold $(RANSAC)    \
		--min-matches      $(MINMATCH)  \
		--window           $(WINDOW)    \
		--iqr-factor       $(IQR)       \
		--max-reproj-error $(MAXREPROJ) \
		--min-parallax     $(PARALLAX)  \
		--n-features       $(NFEATURES)

# =========================================================
# CALIDAD DE CÓDIGO
# =========================================================

lint: ## Linter del backend (ruff)
	docker compose exec hartley ruff check src

lint-fix: ## Linter con autofix
	docker compose exec hartley ruff check --fix src

# =========================================================
# DEPENDENCIAS
# =========================================================

install-backend: ## Reinstalar dependencias del backend dentro del contenedor
	docker compose exec hartley pip install -r requirements.txt

install-frontend: ## Reinstalar dependencias del frontend dentro del contenedor
	docker compose exec galileo pnpm install

# =========================================================
# LIMPIEZA
# =========================================================

clean: ## Eliminar contenedores, redes y volumenes
	docker compose down -v --remove-orphans

reset: clean build up ## Reset completo: limpia y vuelve a levantar
