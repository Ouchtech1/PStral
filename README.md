# Pstral - Assistant IA Pack Solutions

Application d'assistant IA pour génération de requêtes SQL Oracle et assistance conversationnelle, développée pour un usage interne Pack Solutions.

## Démo locale et interne

La démo est volontairement limitée à deux parcours :

- **Questions métier** : recherche locale dans un corpus documentaire versionné, puis réponse sourcée par le modèle Ollama local.
- **SQL Oracle** : sélection d'un modèle SQL relu dans un catalogue fermé. Pstral affiche uniquement la requête ; l'utilisateur la copie ensuite dans Oracle Dev.

Aucune connexion Oracle, exécution SQL, téléversement de fichier, historique persistant ou appel cloud n'est nécessaire pour cette version.

```bash
cp .env.demo.example .env.demo
# Renseigner SECRET_KEY avec au moins 32 caractères aléatoires
./scripts/prepare_demo.sh
docker compose -f docker-compose.demo.yml --env-file .env.demo run --rm backend python scripts/create_user.py
```

Le guide opérationnel complet est dans [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md), et les informations à fournir plus tard pour le vrai schéma Oracle sont dans [SCHEMA_HANDOFF.md](SCHEMA_HANDOFF.md).

## Profils existants hors démo

Les commandes ci-dessous concernent les anciens profils de développement/production. Pour la présentation sur 2 vCPU et 4 Go, utiliser exclusivement `docker-compose.demo.yml` et [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md).

### Windows (Développement)
```powershell
# 1. Démarrer Docker Desktop
# 2. Configurer .env (voir env.production.example)
# 3. Lancer
.\start.ps1
```

### Linux (Production)
```bash
# 1. Configurer .env
cp env.production.example .env
nano .env

# 2. Lancer
docker compose -f docker-compose.prod.yml up --build -d
```

Voir [README_WINDOWS.md](README_WINDOWS.md) et [DEPLOY.md](DEPLOY.md) pour plus de détails.

##  Structure du Projet

```
├── backend/          # API FastAPI
├── frontend/         # Interface React/Vite
├── monitoring/       # Prometheus/Grafana
└── docker-compose.yml
```

## Sécurité

- **Authentification JWT** : Tous les utilisateurs doivent se connecter
- **Audit** : Toutes les actions sont loggées
- **Secrets** : Utiliser `.env` (jamais commité dans Git)

## Notes importantes

- Aucun compte par défaut n'est créé. Le premier compte est provisionné par `backend/scripts/create_user.py`.
- La démo utilise SQLite uniquement pour les comptes, l'index documentaire et l'audit technique ; elle ne se connecte pas à Oracle.
- Le modèle est local et configurable via `OLLAMA_MODEL` (Qwen3.5-2B quantifié par défaut dans `.env.demo.example`).

##  Technologies

- Backend: FastAPI, Python 3.11
- Frontend: React, Vite, Tailwind CSS
- AI: Ollama avec modèle local configurable
- Données: SQLite local pour comptes, index et audit ; aucune connexion Oracle dans la démo

##  Licence

Usage interne Pack Solutions uniquement.
