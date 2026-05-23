#!/usr/bin/env sh

set -eu

# Este script descarga el modelo configurado en el contenedor de Ollama.
# Uso:
#   ./scripts/pull-model.sh
#   OLLAMA_MODEL=qwen:0.5b ./scripts/pull-model.sh

MODEL="${OLLAMA_MODEL:-tinyllama}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

echo "Esperando a que el servicio ollama este disponible..."
docker compose -f "${COMPOSE_FILE}" up -d ollama

until docker compose -f "${COMPOSE_FILE}" exec -T ollama ollama list >/dev/null 2>&1; do
  sleep 2
done

echo "Descargando modelo: ${MODEL}"
docker compose -f "${COMPOSE_FILE}" exec -T ollama ollama pull "${MODEL}"

echo "Modelo descargado correctamente."
