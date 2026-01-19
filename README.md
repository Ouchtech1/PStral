# Pstral - Assistant IA Pack Solutions

Application d'assistant IA pour génération de requêtes SQL Oracle et assistance conversationnelle, développée pour un usage interne Pack Solutions.

##  Démarrage Rapide

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

##  Sécurité

- **Authentification JWT** : Tous les utilisateurs doivent se connecter
- **Audit** : Toutes les actions sont loggées
- **Secrets** : Utiliser `.env` (jamais commité dans Git)

##  Notes Importantes

- **Compte admin par défaut** : `admin` / `admin123` (à changer en production)
- **Base de données** : SQLite pour dev, Oracle pour production
- **LLM** : Ollama avec modèle configurable via `OLLAMA_MODEL`

##  Technologies

- Backend: FastAPI, Python 3.11
- Frontend: React, Vite, Tailwind CSS
- AI: Ollama (Ministral/Mistral)
- Database: SQLite (dev), Oracle (prod)

##  Licence

Usage interne Pack Solutions uniquement.

