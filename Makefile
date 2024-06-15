
SHELL = /bin/bash

DOCKER_COMPOSE_FILE ?= docker-compose.yml

.EXPORT_ALL_VARIABLES:

.PHONY: up down clean psql

all: up setup run

help: ## Display this help.
	@sed -ne '/^##/s/## //p' $(firstword $(MAKEFILE_LIST))
	@sed -Ene '/@sed/!s/(\S+:)(.*)(## )(.*)/\1\t\4/gp' $(MAKEFILE_LIST)

up: ## Starts local development environment.
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d

down: ## Stops local development environment.
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

clean: ## Destroys local development environment.
	docker-compose -f $(DOCKER_COMPOSE_FILE) down --volumes --remove-orphans

psql: up ## Starts PostgreSQL interactive terminal.
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec postgres psql --dbname=$(PG_DATADASE) --username=$(PG_USERNAME)

setup:
	python3.10 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt

run: up setup
	source .venv/bin/activate && python main.py

test: up setup
	source .venv/bin/activate && pytest -vv