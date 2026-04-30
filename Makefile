# Makefile -- comandos del stack mv3d (multi-view-3d-reconstruction)
# Servicios: hartley (backend SfM), galileo (frontend Three.js).

SHELL := /bin/bash

.PHONY: help build up up-fg down restart logs logs-backend logs-frontend ps \
        shell-backend shell-frontend pipeline lint lint-fix clean reset \
        install-frontend install-backend

help: ## Listar comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

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

logs: ## Ver logs en tiempo real (todos los servicios)
	docker compose logs -f

logs-backend: ## Ver logs del backend (hartley)
	docker compose logs -f hartley

logs-frontend: ## Ver logs del frontend (galileo)
	docker compose logs -f galileo

ps: ## Ver estado de servicios
	docker compose ps

shell-backend: ## Abrir shell en backend
	docker compose exec hartley sh

shell-frontend: ## Abrir shell en frontend
	docker compose exec galileo sh

pipeline: ## Correr pipeline SfM por CLI; uso: make pipeline DATASET=<nombre>
	docker compose exec hartley python -m sfm_pipeline.cli --dataset $(DATASET)

lint: ## Linter del backend (ruff)
	docker compose exec hartley ruff check src

lint-fix: ## Linter con autofix
	docker compose exec hartley ruff check --fix src

install-backend: ## Reinstalar dependencias del backend dentro del contenedor
	docker compose exec hartley pip install -r requirements.txt

install-frontend: ## Reinstalar dependencias del frontend dentro del contenedor
	docker compose exec galileo pnpm install

clean: ## Eliminar contenedores, redes y volumenes
	docker compose down -v --remove-orphans

reset: clean build up ## Reset completo: limpia y vuelve a levantar
