# Deploiement Pstral sur VPS IONOS

Guide de deploiement pour VPS IONOS Ubuntu 24.04 avec 8 Go RAM, 6 vCores, sans GPU.

## Prerequisites

- VPS IONOS avec Ubuntu 24.04
- Acces SSH root ou sudo
- Port 80 ouvert dans le firewall

## 1. Installation de Docker

Connectez-vous en SSH au serveur :

```bash
ssh root@your-server-ip
```

Installez Docker et Docker Compose :

```bash
# Mise a jour du systeme
apt update && apt upgrade -y

# Installation des dependances
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Ajout du depot Docker officiel
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation de Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verification
docker --version
docker compose version
```

## 2. Clonage du Projet

```bash
# Cloner le depot
git clone http://prd-git01.packsolutions.local/hhouchti/pstral.git
cd pstral

# Ou si le depot est prive, utilisez un token:
# git clone https://username:token@github.com/user/pstral.git
```

## 3. Configuration

```bash
# Copier le fichier d'environnement
cp env.ionos.example .env

# Editer la configuration
nano .env
```

**IMPORTANT** : Generez une cle secrete securisee :

```bash
# Generer SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Ou:
openssl rand -base64 32
```

Copiez le resultat dans `.env` pour `SECRET_KEY`.

## 4. Deploiement

```bash
# Lancer l'application
docker compose -f docker-compose.ionos.yml up -d

# Suivre les logs (premier demarrage long - telechargement du modele ~2 Go)
docker compose -f docker-compose.ionos.yml logs -f
```

Le premier demarrage prend plusieurs minutes car le modele AI (~2 Go) doit etre telecharge.

## 5. Verification

```bash
# Verifier que tous les services sont actifs
docker compose -f docker-compose.ionos.yml ps

# Tester l'API
curl http://localhost/health

# Tester Ollama
curl http://localhost:11434/api/tags
```

Accedez a l'application : `http://your-server-ip`

## 6. Gestion

### Commandes utiles

```bash
# Voir les logs
docker compose -f docker-compose.ionos.yml logs -f

# Logs d'un service specifique
docker compose -f docker-compose.ionos.yml logs -f ollama
docker compose -f docker-compose.ionos.yml logs -f backend
docker compose -f docker-compose.ionos.yml logs -f frontend

# Redemarrer un service
docker compose -f docker-compose.ionos.yml restart backend

# Arreter l'application
docker compose -f docker-compose.ionos.yml down

# Arreter et supprimer les volumes (ATTENTION: perte de donnees)
docker compose -f docker-compose.ionos.yml down -v
```

### Mise a jour

```bash
# Arreter l'application
docker compose -f docker-compose.ionos.yml down

# Mettre a jour le code
git pull

# Reconstruire et relancer
docker compose -f docker-compose.ionos.yml up -d --build
```

## Architecture

```
                    Internet
                       |
                       v
                  [Port 80]
                       |
                       v
            +-------------------+
            |      Nginx        |  256 Mo RAM
            |   (Frontend SPA)  |
            +-------------------+
                 |         |
                 v         v
            /api/*       /*
                 |         |
                 v         |
            +----------+   |
            | Backend  |<--+  1 Go RAM
            | FastAPI  |
            +----------+
                 |
                 v
            +----------+
            |  Ollama  |      5 Go RAM
            | (LLM AI) |
            +----------+
```

## Limites de Ressources

| Service  | RAM Limite | RAM Reserve | CPU |
|----------|------------|-------------|-----|
| Ollama   | 5 Go       | 4 Go        | 4   |
| Backend  | 1 Go       | 512 Mo      | 1.5 |
| Frontend | 256 Mo     | 128 Mo      | 0.5 |
| **Total**| **~6.25 Go** | -         | 6   |

Marge de securite : ~1.75 Go pour le systeme.

## Depannage

### Le modele ne se telecharge pas

```bash
# Verifier les logs Ollama
docker compose -f docker-compose.ionos.yml logs ollama

# Entrer dans le container et telecharger manuellement
docker exec -it pstral-ollama bash
ollama pull ministral:3b
```

### Erreur de memoire (OOM)

```bash
# Verifier l'utilisation memoire
docker stats

# Si OOM, reduire les limites dans docker-compose.ionos.yml
# Ou utiliser un modele plus petit
```

### Backend ne demarre pas

```bash
# Verifier que Ollama est pret
docker compose -f docker-compose.ionos.yml logs backend

# Le backend attend le healthcheck Ollama (peut prendre 2-3 min)
```

### Regenerer le mot de passe admin

```bash
# Supprimer la base de donnees utilisateurs
docker compose -f docker-compose.ionos.yml down
docker volume rm pstral_pstral-data
docker compose -f docker-compose.ionos.yml up -d
# Le compte admin/admin123 sera recree
```

## Securite en Production

1. **Changer le mot de passe admin** apres la premiere connexion
2. **Utiliser HTTPS** avec un reverse proxy (Traefik, Caddy) ou Let's Encrypt
3. **Firewall** : n'ouvrir que le port 80 (ou 443 pour HTTPS)
4. **Backups** : sauvegarder regulierement le volume `pstral-data`

## Support

Pour toute question ou probleme, contactez l'equipe Pack Solutions.

