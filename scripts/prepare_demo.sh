#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env.demo ]]; then
  echo "Créez .env.demo à partir de .env.demo.example et définissez SECRET_KEY." >&2
  exit 2
fi

SECRET_KEY_VALUE="$(sed -n 's/^SECRET_KEY=//p' .env.demo | head -n 1)"
if [[ ${#SECRET_KEY_VALUE} -lt 32 || "$SECRET_KEY_VALUE" == "replace-with-a-random-32-character-secret" ]]; then
  echo "SECRET_KEY doit contenir au moins 32 caractères aléatoires dans .env.demo." >&2
  exit 2
fi

MODEL="$(docker compose --env-file .env.demo -f docker-compose.demo.yml config --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["services"]["ollama"]["environment"]["OLLAMA_MODEL"])')"
echo "Démarrage du moteur local…"
docker compose --env-file .env.demo -f docker-compose.demo.yml up -d ollama
for attempt in {1..30}; do
  if docker compose --env-file .env.demo -f docker-compose.demo.yml exec -T ollama ollama list >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    echo "Ollama n'est pas disponible après 60 secondes." >&2
    exit 1
  fi
  sleep 2
done
echo "Téléchargement ou vérification du modèle : $MODEL"
docker compose --env-file .env.demo -f docker-compose.demo.yml exec -T ollama ollama pull "$MODEL"
echo "Préchauffage par une inférence de contrôle…"
docker compose --env-file .env.demo -f docker-compose.demo.yml exec -T ollama ollama run "$MODEL" "Réponds uniquement par OK." >/dev/null
echo "Construction et démarrage de Pstral…"
docker compose --env-file .env.demo -f docker-compose.demo.yml up -d --build
echo "Pstral est prêt lorsque /ready répond 200."
