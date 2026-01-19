# Guide de démarrage - Ministral SQL Assistant sur Windows

Ce guide vous explique comment lancer le projet **Ministral SQL Assistant** sur votre machine Windows en utilisant Docker.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

1. **Docker Desktop pour Windows**
   - Télécharger depuis : https://www.docker.com/products/docker-desktop
   - Démarrer Docker Desktop avant de lancer le projet

2. **Ollama** (déjà installé selon vos indications)
   - Vérifier que le modèle `ministral-3:3b` est disponible :
     ```powershell
     ollama list
     ```
   - Si le modèle n'est pas présent :
     ```powershell
     ollama pull ministral-3:3b
     ```
   - Démarrer Ollama (si ce n'est pas déjà fait) :
     ```powershell
     ollama serve
     ```

3. **Oracle Database** (optionnel)
   - Le backend fonctionnera en mode "mock" si Oracle n'est pas configuré
   - Si vous avez Oracle, configurez les variables dans le fichier `.env`

## 🚀 Démarrage rapide

### Méthode 1 : Utiliser les scripts PowerShell (Recommandé)

1. **Créer le fichier `.env`** :
   ```powershell
   # Si le fichier .env n'existe pas, créez-le avec ce contenu :
   @"
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   OLLAMA_MODEL=ministral-3:3b
   ORACLE_DSN=host.docker.internal/XEPDB1
   ORACLE_USER=system
   ORACLE_PASSWORD=oracle
   VITE_API_URL=http://localhost:8000/api/v1
   "@ | Out-File -FilePath .env -Encoding utf8
   ```

2. **Lancer le projet** :
   ```powershell
   .\start.ps1
   ```

3. **Accéder à l'application** :
   - Frontend : http://localhost:5173
   - Backend API : http://localhost:8000
   - Health Check : http://localhost:8000/health

### Méthode 2 : Commandes Docker Compose manuelles

1. **Créer le fichier `.env`** (voir ci-dessus)

2. **Lancer les conteneurs** :
   ```powershell
   docker-compose up --build
   ```

3. **En arrière-plan (détaché)** :
   ```powershell
   docker-compose up --build -d
   ```

## 🛠️ Scripts disponibles

### `start.ps1`
Script de démarrage intelligent qui :
- Vérifie que Docker Desktop est démarré
- Vérifie la présence du fichier `.env`
- Vérifie la connexion à Ollama
- Vérifie la disponibilité des ports
- Lance les conteneurs Docker

**Usage** :
```powershell
.\start.ps1
```

### `stop.ps1`
Arrête tous les conteneurs Docker du projet.

**Usage** :
```powershell
.\stop.ps1
```

### `logs.ps1`
Affiche les logs des conteneurs en temps réel.

**Usage** :
```powershell
# Tous les services
.\logs.ps1

# Un service spécifique
.\logs.ps1 backend
.\logs.ps1 frontend
```

## 📝 Commandes Docker Compose utiles

### Vérifier l'état des services
```powershell
docker-compose ps
```

### Voir les logs
```powershell
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Redémarrer un service
```powershell
docker-compose restart backend
docker-compose restart frontend
```

### Arrêter les conteneurs
```powershell
docker-compose down
```

### Arrêter et supprimer les volumes
```powershell
docker-compose down -v
```

### Reconstruire les images
```powershell
docker-compose build --no-cache
```

## 🔧 Configuration

### Variables d'environnement (`.env`)

Le fichier `.env` à la racine du projet contient :

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `OLLAMA_BASE_URL` | URL d'Ollama | `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | Modèle Ollama à utiliser | `ministral-3:3b` |
| `ORACLE_DSN` | DSN Oracle (optionnel) | `host.docker.internal/XEPDB1` |
| `ORACLE_USER` | Utilisateur Oracle (optionnel) | `system` |
| `ORACLE_PASSWORD` | Mot de passe Oracle (optionnel) | `oracle` |
| `VITE_API_URL` | URL de l'API backend | `http://localhost:8000/api/v1` |

### Modifier la configuration

1. Éditez le fichier `.env`
2. Redémarrez les conteneurs :
   ```powershell
   docker-compose down
   docker-compose up --build
   ```

## 🐛 Dépannage

### Docker Desktop n'est pas démarré
**Erreur** : `Cannot connect to the Docker daemon`

**Solution** : Démarrer Docker Desktop depuis le menu Démarrer de Windows.

### Port déjà utilisé
**Erreur** : `port is already allocated`

**Solution** :
- Vérifier quel processus utilise le port :
  ```powershell
  # Port 8000
  Get-NetTCPConnection -LocalPort 8000
  
  # Port 5173
  Get-NetTCPConnection -LocalPort 5173
  ```
- Arrêter le processus ou modifier les ports dans `docker-compose.yml`

### Ollama non accessible
**Erreur** : Le backend ne peut pas se connecter à Ollama

**Solution** :
1. Vérifier qu'Ollama est démarré :
   ```powershell
   # Dans un nouveau terminal
   ollama serve
   ```
2. Vérifier que le modèle est disponible :
   ```powershell
   ollama list
   ```
3. Si nécessaire, télécharger le modèle :
   ```powershell
   ollama pull ministral-3:3b
   ```

### Le backend ne démarre pas
**Solution** :
1. Vérifier les logs :
   ```powershell
   docker-compose logs backend
   ```
2. Vérifier la connexion à la base de données Oracle (si configurée)
3. Le backend fonctionne en mode "mock" si Oracle n'est pas disponible

### Le frontend ne se charge pas
**Solution** :
1. Vérifier que le backend est accessible :
   ```powershell
   curl http://localhost:8000/health
   ```
2. Vérifier les logs :
   ```powershell
   docker-compose logs frontend
   ```
3. Vérifier la variable `VITE_API_URL` dans `.env`

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         Windows Host                     │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Ollama     │  │   Oracle     │    │
│  │  :11434      │  │  (Optionnel) │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │            │
└─────────┼─────────────────┼────────────┘
          │                 │
          │ host.docker.internal
          │                 │
┌─────────┼─────────────────┼────────────┐
│ Docker  │                 │            │
│ Compose │                 │            │
│         │                 │            │
│  ┌──────▼──────┐  ┌───────▼──────┐    │
│  │   Backend   │  │   Frontend   │    │
│  │  FastAPI    │  │    React     │    │
│  │  :8000      │  │    :5173     │    │
│  └─────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

## 🔗 URLs importantes

- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **API Documentation** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

## 📚 Ressources supplémentaires

- Documentation Docker : https://docs.docker.com/
- Documentation Ollama : https://ollama.ai/docs
- Documentation FastAPI : https://fastapi.tiangolo.com/

## ⚠️ Notes importantes

- Sur Windows, `host.docker.internal` est automatiquement résolu par Docker Desktop
- Si Oracle n'est pas configuré, le backend fonctionnera en mode "mock" (pas d'erreur)
- Le frontend utilise Vite en mode dev avec hot-reload
- Les volumes montent le code source pour le développement
- Les modifications du code sont reflétées automatiquement (hot-reload)

## 🎯 Prochaines étapes

Une fois le projet lancé :

1. Ouvrez http://localhost:5173 dans votre navigateur
2. Sélectionnez un mode (SQL, Email, Wiki, ou Chat)
3. Commencez à interagir avec l'assistant IA

Bon développement ! 🚀

