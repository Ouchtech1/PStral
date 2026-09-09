# Runbook de démonstration Pstral

## Préparer une fois

1. Copier `.env.demo.example` vers `.env.demo` et remplacer `SECRET_KEY` par une valeur aléatoire d’au moins 32 caractères.
2. Installer Docker Compose et vérifier que la machine cible dispose de 4 Go de RAM et de 2 vCPU disponibles.
3. Lancer `chmod +x scripts/prepare_demo.sh && ./scripts/prepare_demo.sh` depuis `PStral-main`. Le script télécharge puis préchauffe le modèle par une inférence de contrôle avant le démarrage complet ; le fonctionnement ultérieur n’effectue aucun téléchargement.
4. Créer un compte avec `docker compose --env-file .env.demo -f docker-compose.demo.yml run --rm backend python scripts/create_user.py`.
5. Lancer le contrôle déterministe avant la présentation :

   ```bash
   docker compose --env-file .env.demo -f docker-compose.demo.yml run --rm backend python scripts/evaluate_demo.py
   ```

   Il vérifie le corpus local et le catalogue SQL relu sans appeler Oracle ni sortir de données du serveur.
6. Ouvrir l’URL HTTPS interne fournie par l’équipe infrastructure. Le service expose uniquement Nginx ; Ollama et FastAPI restent sur le réseau Docker privé.

Pour utiliser le schéma métier, remplacer les fichiers synthétiques dans `backend/app/demo_assets/` ou monter un répertoire interne en lecture seule, puis reconstruire l’index avec `docker compose ... run --rm backend python scripts/index_demo.py`. Ne pas ajouter de données clients au dépôt Git.

## Vérifier avant la présentation

```bash
docker compose --env-file .env.demo -f docker-compose.demo.yml ps
curl -fsS http://localhost/health
curl -fsS http://localhost/ready
docker compose --env-file .env.demo -f docker-compose.demo.yml exec ollama ollama list
```

Le champ `model` de `/ready`, la version du corpus et la version du catalogue doivent correspondre à la fiche de validation. Un statut 503 indique que le modèle n’est pas chargé ou que le catalogue/index sont invalides.

Après la préparation du modèle, l’équipe infrastructure doit appliquer sa règle habituelle de sortie réseau limitée au réseau interne. `OLLAMA_NO_CLOUD=1` désactive les fonctions cloud d’Ollama mais ne remplace pas ce pare-feu.

## Scénario

1. Se connecter avec le compte préparé.
2. Ouvrir **Questions métier**, poser une question couverte et ouvrir **Sources internes**.
3. Poser une question absente pour montrer le refus explicite.
4. Revenir à l’écran d’accueil, ouvrir **SQL Oracle**, poser une question correspondant à un modèle connu.
5. Vérifier la clarification lorsque la date, le statut ou un autre paramètre manque.
6. Cliquer **Copier** et coller dans l’outil Oracle de développement de l’utilisateur. Pstral n’exécute aucune requête et n’affiche aucun résultat Oracle.
7. Montrer que la déconnexion efface la session du navigateur. Recharger la page pour vérifier qu’aucun historique n’est restauré.

Ne pas introduire de données clients réelles dans les questions de présentation. Garder une question de secours par mode et un compte de présentation distinct du compte administrateur.

## Arrêter et récupérer

```bash
docker compose --env-file .env.demo -f docker-compose.demo.yml logs --tail=100 backend ollama
docker compose --env-file .env.demo -f docker-compose.demo.yml down
```

Après une erreur de modèle, vérifier le volume Ollama et relancer la commande de préparation. Après une modification du corpus ou du catalogue, reconstruire l’index puis vérifier `/ready` avant d’ouvrir l’interface.
