# Remise du schéma métier pour Pstral

La version de démonstration attend un sous-ensemble réduit et relu du domaine assurance vie. Fournir les éléments dans l’environnement interne autorisé, pas dans un dépôt public et pas à un fournisseur de modèle.

À fournir :

- version Oracle cible et conventions de schéma ;
- noms qualifiés des tables ou vues autorisées ;
- colonnes, types, clés et relations avec cardinalités ;
- règles de statut, dates, périmètres et exclusions ;
- indicateurs métier et risques de doublons dans les agrégations ;
- questions de démonstration et requêtes Oracle attendues, revues par un connaisseur de la base ;
- documents de référence versionnés, datés et accessibles à tous les participants.

Ne fournir ni mot de passe Oracle, ni export de lignes clients, ni identifiant permettant une connexion. Pstral ne se connecte pas à Oracle dans cette version.

Le catalogue est ensuite remplacé par des modèles déclaratifs : intention, variantes, paramètres typés, valeurs autorisées, SQL Oracle approuvé et hypothèses. Le LLM sélectionne un modèle et ses paramètres ; le serveur rend la requête par code. Une jointure ou une règle absente du catalogue déclenche une clarification, jamais une invention.

Après intégration : reconstruire l’index, exécuter le jeu de cas métier, vérifier chaque requête dans l’outil Oracle de développement de l’utilisateur, puis faire une revue humaine avant la démonstration.
