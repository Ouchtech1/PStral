# Pstral - Guide de Déploiement Production Linux

Ce guide explique comment déployer Pstral sur un serveur Linux Enterprise (RHEL/Ubuntu/CentOS).

---

## Table des Matières

1. [Prérequis](#prérequis)
2. [Installation Rapide](#installation-rapide)
3. [Configuration Détaillée](#configuration-détaillée)
4. [Configuration Ollama & Modèles](#configuration-ollama--modèles)
5. [Optimisation GPU](#optimisation-gpu)
6. [Architecture](#architecture)
7. [Monitoring](#monitoring)
8. [Dépannage](#dépannage)
9. [Sécurité Production](#sécurité-production)

---

## Prérequis

### Serveur Minimum
- **OS**: Ubuntu 20.04+, RHEL 8+, CentOS 8+
- **RAM**: 8GB minimum (16GB recommandé)
- **CPU**: 4 cores minimum
- **Stockage**: 20GB SSD

### Logiciels Requis

1. **Docker & Docker Compose** (v2.0+)
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   
   # Vérifier l'installation
   docker --version
   docker compose version
   ```

2. **Ollama** (sur le host, pas dans Docker)
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
   
   # Démarrer le service
   sudo systemctl enable ollama
   sudo systemctl start ollama
   
   # Télécharger un modèle
   ollama pull ministral:latest
   ```

---

## Installation Rapide

```bash
# 1. Cloner/Copier le projet
git clone <repository-url> /opt/pstral
cd /opt/pstral

# 2. Configurer l'environnement
cp env.production.example .env
nano .env  # Modifier les variables

# 3. Générer une clé secrète sécurisée
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copier le résultat dans SECRET_KEY dans .env

# 4. Lancer l'application
docker compose -f docker-compose.prod.yml up --build -d

# 5. Vérifier le statut
docker compose -f docker-compose.prod.yml ps
```

**Accès**: `http://votre-serveur:5173`

---

## Configuration Détaillée

### Variables d'Environnement (.env)

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `OLLAMA_BASE_URL` | URL du serveur Ollama | `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | Modèle LLM à utiliser | `ministral:latest` |
| `MAX_HISTORY_MESSAGES` | Messages max en contexte | `10` |
| `MAX_FILE_CONTENT_LENGTH` | Taille max fichiers uploadés | `3000` |
| `SECRET_KEY` | Clé JWT (OBLIGATOIRE) | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée session (min) | `60` |
| `ORACLE_DSN` | Connexion Oracle | - |
| `ORACLE_USER` | Utilisateur Oracle | - |
| `ORACLE_PASSWORD` | Mot de passe Oracle | - |

### Exemple .env Production

```bash
# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=mistral:7b

# Contexte (ajuster selon le modèle)
MAX_HISTORY_MESSAGES=15
MAX_FILE_CONTENT_LENGTH=5000

# Sécurité
SECRET_KEY=votre-cle-securisee-de-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=480  # 8 heures

# Oracle (si utilisé)
ORACLE_DSN=oracle-server:1521/PROD
ORACLE_USER=app_user
ORACLE_PASSWORD=secure_password
```

---

## Configuration Ollama & Modèles

### Modèles Recommandés

| Modèle | RAM | Contexte | Vitesse | Qualité | Usage |
|--------|-----|----------|---------|---------|-------|
| `ministral:latest` | 3GB | 8K | ⚡⚡⚡ | ⭐⭐ | Dev/Test |
| `mistral:7b` | 5GB | 32K | ⚡⚡ | ⭐⭐⭐ | Production |
| `llama3:8b` | 6GB | 8K | ⚡⚡ | ⭐⭐⭐ | Production |
| `mixtral:8x7b` | 26GB | 32K | ⚡ | ⭐⭐⭐⭐ | Qualité max |
| `codellama:13b` | 9GB | 16K | ⚡⚡ | ⭐⭐⭐⭐ | SQL spécialisé |

### Changer de Modèle

```bash
# 1. Télécharger le nouveau modèle
ollama pull mistral:7b

# 2. Mettre à jour .env
echo "OLLAMA_MODEL=mistral:7b" >> .env

# 3. Redémarrer le backend
docker compose -f docker-compose.prod.yml restart backend
```

### Vérifier Ollama

```bash
# Status du service
systemctl status ollama

# Modèles installés
ollama list

# Test de génération
ollama run mistral:7b "Bonjour, comment vas-tu?"
```

---

## Optimisation GPU

### Prérequis GPU NVIDIA

```bash
# 1. Installer les drivers NVIDIA
sudo apt install nvidia-driver-535

# 2. Installer nvidia-container-toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 3. Configurer Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 4. Vérifier
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Performance GPU vs CPU

| Configuration | Tokens/sec | Temps réponse |
|---------------|------------|---------------|
| CPU (8 cores) | ~10-20 | 5-15 sec |
| GPU RTX 3060 | ~50-80 | 1-3 sec |
| GPU RTX 4090 | ~100-150 | <1 sec |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Serveur Linux                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐ │
│  │  Frontend   │    │   Backend   │    │     Ollama      │ │
│  │  (React)    │◄──►│  (FastAPI)  │◄──►│   (LLM local)   │ │
│  │  :5173      │    │   :8000     │    │    :11434       │ │
│  └─────────────┘    └──────┬──────┘    └─────────────────┘ │
│        Docker               │                   Host        │
│                      ┌──────▼──────┐                       │
│                      │   SQLite    │                       │
│                      │  (volume)   │                       │
│                      │  - users    │                       │
│                      │  - audit    │                       │
│                      │  - history  │                       │
│                      └─────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Monitoring

### Logs

```bash
# Tous les logs
docker compose -f docker-compose.prod.yml logs -f

# Backend uniquement
docker compose -f docker-compose.prod.yml logs -f backend

# Frontend uniquement
docker compose -f docker-compose.prod.yml logs -f frontend
```

### Health Check

```bash
# Status des conteneurs
docker compose -f docker-compose.prod.yml ps

# Health du backend
curl http://localhost:8000/health

# Métriques Prometheus (si activé)
curl http://localhost:8000/metrics
```

### Prometheus/Grafana (Optionnel)

```bash
# Lancer le stack monitoring
docker compose -f monitoring/docker-compose.monitoring.yml up -d

# Accès
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

---

## Dépannage

### Ollama non accessible

```bash
# Vérifier que Ollama écoute
curl http://localhost:11434/api/tags

# Si erreur, redémarrer
sudo systemctl restart ollama

# Vérifier les logs
journalctl -u ollama -f
```

### Backend ne démarre pas

    ```bash
# Voir les logs d'erreur
docker compose -f docker-compose.prod.yml logs backend

# Erreurs courantes:
# - "SECRET_KEY must be set" -> Configurer SECRET_KEY dans .env
# - "Connection refused" -> Ollama non démarré
```

### Réponses lentes

1. **Vérifier la charge CPU**: `htop`
2. **Vérifier la RAM**: `free -h`
3. **Utiliser un modèle plus léger**: `OLLAMA_MODEL=ministral:latest`
4. **Réduire l'historique**: `MAX_HISTORY_MESSAGES=5`

### Fichiers uploadés trop gros

Ajuster dans `.env`:
    ```bash
MAX_FILE_CONTENT_LENGTH=5000  # Augmenter si nécessaire
```

---

## Sécurité Production

### Checklist

- [ ] Clé `SECRET_KEY` unique et sécurisée
- [ ] HTTPS configuré (reverse proxy Nginx/Traefik)
- [ ] Firewall: seuls ports 80/443 exposés
- [ ] Mots de passe Oracle sécurisés
- [ ] Sauvegardes SQLite régulières
- [ ] Logs d'audit activés

### Configuration HTTPS avec Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name pstral.votre-entreprise.com;

    ssl_certificate /etc/ssl/certs/pstral.crt;
    ssl_certificate_key /etc/ssl/private/pstral.key;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Commandes Utiles

```bash
# Démarrer
docker compose -f docker-compose.prod.yml up -d

# Arrêter
docker compose -f docker-compose.prod.yml down

# Redémarrer
docker compose -f docker-compose.prod.yml restart

# Reconstruire après modification
docker compose -f docker-compose.prod.yml up --build -d

# Voir les logs en temps réel
docker compose -f docker-compose.prod.yml logs -f

# Entrer dans un conteneur
docker compose -f docker-compose.prod.yml exec backend bash
```

---

## Support

Pour toute question, contacter l'équipe Infrastructure Pack Solutions.
