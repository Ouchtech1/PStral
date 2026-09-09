# Validation de la démo Pstral

Date : 8 septembre 2026  
État : travail local non commité, profil `synthetic`

## État atteint

Le profil synthétique est **prêt techniquement pour une préparation sur le VPS** : l’API, le frontend, l’index FTS5 local, le catalogue SQL fermé et l’authentification ont été vérifiés sans connexion Oracle.

La validation sur le VPS n’est pas encore mesurée : le daemon Docker n’était pas disponible sur la machine de développement. La qualité métier finale n’est pas validée : les documents et requêtes actuellement livrés sont explicitement synthétiques.

## Vérifications exécutées

- `python3 -m compileall -q app scripts tests` : réussi.
- Environnement Python 3.11 (runtime du Dockerfile) : `14 passed` avec `pytest`.
- `python scripts/evaluate_demo.py` : 31 cas déterministes réussis (10 RAG, 15 sélections SQL, 4 cas de paramètres manquants et 6 refus hors catalogue).
- `npm ci --ignore-scripts` : réussi.
- `npm run build` : réussi avec Vite 5.4.21.
- `bash -n scripts/prepare_demo.sh` : réussi.
- `docker compose -f docker-compose.demo.yml config --quiet` avec une clé de test injectée : réussi.

La commande de préparation inclut désormais une inférence de contrôle après `ollama pull`; elle échouera avant le démarrage du backend si le modèle ne répond pas.

Les tests backend couvrent notamment l’absence de compte par défaut, l’authentification, les limites de charge, le corpus local, les dates et enums SQL, le rendu en lecture seule et l’absence d’appel d’exécution.

## Points non mesurés

- Construction et démarrage des images : impossible localement tant que le daemon Docker n’est pas démarré.
- Téléchargement, préchauffage et latence du modèle Qwen3.5-2B Q4_K_M : à exécuter sur le VPS cible.
- Mémoire réellement disponible, p95 de latence, annulation d’une inférence et comportement réseau hors Internet : à mesurer sur le VPS.
- Parcours navigateur complet avec HTTPS et presse-papiers : à vérifier sur l’URL interne.
- Exactitude des réponses sur le vrai schéma Oracle et les vrais documents : en attente du contenu métier et d’une revue humaine.

## Modèle et données de démonstration

Le choix provisoire est `hf.co/unsloth/Qwen3.5-2B-GGUF:Q4_K_M`, chargé seul par Ollama 0.33.3 avec deux threads, un contexte de 2 048 tokens et une sortie bornée. Les quotas Compose totalisent 2 vCPU (1,5 pour Ollama, 0,35 pour FastAPI et 0,15 pour Nginx). Le catalogue SQL porte la version `synthetic-2026-09-08` et le corpus la même version.

Avant la présentation, suivre [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md), exécuter `prepare_demo.sh`, créer le compte local et vérifier `/ready` ainsi que `evaluate_demo.py`. Ne pas annoncer de résultat Oracle tant que les modèles SQL n’ont pas été relus puis collés et vérifiés par l’utilisateur dans Oracle Dev.
