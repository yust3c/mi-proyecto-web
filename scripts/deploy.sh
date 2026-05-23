#!/usr/bin/env sh

set -eu

# Script de despliegue para ejecutarse en la VM.
# Supone que el proyecto esta clonado en /opt/proyecto-ollama
# y que existe un archivo .env con las variables de produccion.

PROJECT_DIR="${PROJECT_DIR:-/opt/proyecto-ollama}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

cd "${PROJECT_DIR}"

echo "Actualizando imagenes desde GHCR..."
docker compose -f "${COMPOSE_FILE}" pull

echo "Recreando servicios en segundo plano..."
docker compose -f "${COMPOSE_FILE}" up -d

echo "Eliminando imagenes antiguas no utilizadas..."
docker image prune -f

echo "Despliegue completado."
