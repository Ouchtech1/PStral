# Pstral - Guide Complet d'Architecture et de Compréhension

**Document de référence pour comprendre le projet de A à Z**

*Version 1.0 - Janvier 2026*

---

## Table des Matières

1. [Introduction et Contexte](#1-introduction-et-contexte)
2. [Le Problème Initial](#2-le-problème-initial)
3. [La Solution Proposée](#3-la-solution-proposée)
4. [Choix Technologiques](#4-choix-technologiques)
5. [Architecture Globale](#5-architecture-globale)
6. [Phase 1 : Le Cœur - Communication avec l'IA](#6-phase-1--le-cœur---communication-avec-lia)
7. [Phase 2 : L'Interface Utilisateur](#7-phase-2--linterface-utilisateur)
8. [Phase 3 : Sécurité et Authentification](#8-phase-3--sécurité-et-authentification)
9. [Phase 4 : Fonctionnalités Métier](#9-phase-4--fonctionnalités-métier)
10. [Phase 5 : Déploiement Production](#10-phase-5--déploiement-production)
11. [Flux de Données Complet](#11-flux-de-données-complet)
12. [Glossaire Technique](#12-glossaire-technique)
13. [FAQ - Questions Fréquentes](#13-faq---questions-fréquentes)
14. [Annexes](#14-annexes)

---

# 1. Introduction et Contexte

## 1.1 Qu'est-ce que Pstral ?

Pstral est un **assistant IA interne** développé pour Pack Solutions. Son rôle principal est d'aider les employés à :

- **Générer des requêtes SQL Oracle** à partir de questions en langage naturel
- **Répondre à des questions techniques** sur la documentation interne
- **Assister dans les tâches quotidiennes** liées aux bases de données

## 1.2 Pourquoi ce nom ?

"Pstral" est un jeu de mots combinant :
- **P**ack **S**olutions
- Mis**tral** (le modèle d'IA français utilisé)

## 1.3 Qui utilise cette application ?

- **Développeurs** : Pour générer rapidement des requêtes SQL complexes
- **Analystes** : Pour interroger les données sans connaître SQL
- **Support technique** : Pour trouver des informations rapidement

---

# 2. Le Problème Initial

## 2.1 Contexte Entreprise

Pack Solutions est une entreprise française qui utilise des bases de données **Oracle** pour stocker ses données métier. Les employés ont souvent besoin de :

1. Écrire des requêtes SQL pour extraire des informations
2. Comprendre la structure des tables existantes
3. Obtenir de l'aide sur la syntaxe Oracle spécifique

## 2.2 Les Problèmes Identifiés

### Problème 1 : Dépendance aux experts SQL
> "Chaque fois que j'ai besoin d'une requête complexe, je dois demander à un développeur senior. Ça prend du temps et ça les dérange."

**Impact** : Perte de productivité, goulot d'étranglement sur les experts.

### Problème 2 : Risques de sécurité avec ChatGPT
> "J'aimerais utiliser ChatGPT, mais je ne peux pas lui envoyer des informations sur notre schéma de base de données - c'est confidentiel."

**Impact** : Impossibilité d'utiliser les outils IA publics pour des données sensibles.

### Problème 3 : Conformité RGPD
> "Les données de nos clients ne doivent jamais quitter nos serveurs."

**Impact** : Obligation légale de garder les données en France, sur des serveurs contrôlés.

### Problème 4 : Coût des solutions commerciales
> "Les solutions IA entreprise coûtent très cher et nécessitent des contrats longs."

**Impact** : Budget limité, besoin d'une solution économique.

## 2.3 Cahier des Charges Résumé

| Exigence | Priorité |
|----------|----------|
| IA qui tourne en local (pas de cloud) | Critique |
| Génération de requêtes SQL Oracle | Haute |
| Interface simple et intuitive | Haute |
| Authentification des utilisateurs | Haute |
| Traçabilité des actions (audit) | Moyenne |
| Déploiement sur serveur Linux | Moyenne |

---

# 3. La Solution Proposée

## 3.1 Vue d'Ensemble

La solution est une **application web** composée de trois parties :

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    [Navigateur Web]                                             │
│          │                                                      │
│          ▼                                                      │
│    ┌─────────────┐                                              │
│    │  FRONTEND   │  ← Interface utilisateur (React)             │
│    │  (React)    │                                              │
│    └──────┬──────┘                                              │
│           │                                                      │
│           ▼                                                      │
│    ┌─────────────┐                                              │
│    │  BACKEND    │  ← Logique métier, sécurité (FastAPI)        │
│    │  (FastAPI)  │                                              │
│    └──────┬──────┘                                              │
│           │                                                      │
│           ▼                                                      │
│    ┌─────────────┐                                              │
│    │   OLLAMA    │  ← Moteur IA local (Ministral 3B)            │
│    │   (LLM)     │                                              │
│    └─────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 Pourquoi Trois Couches ?

### Séparation des responsabilités

Chaque couche a un rôle précis :

| Couche | Responsabilité | Analogie |
|--------|---------------|----------|
| **Frontend** | Affichage, interactions utilisateur | La vitrine d'un magasin |
| **Backend** | Logique métier, sécurité, validation | L'arrière-boutique |
| **LLM** | Intelligence artificielle, génération de texte | L'expert consulté |

### Avantages de cette séparation

1. **Sécurité** : Le frontend ne parle jamais directement à l'IA
2. **Évolutivité** : On peut changer le modèle IA sans toucher au frontend
3. **Testabilité** : Chaque couche peut être testée indépendamment

---

# 4. Choix Technologiques

## 4.1 Frontend : React + Vite + Tailwind CSS

### Pourquoi React ?

**Problème** : On doit créer une interface interactive qui se met à jour en temps réel (streaming des réponses IA).

**Solution** : React est un framework JavaScript qui permet de créer des interfaces dynamiques facilement.

**Alternatives considérées** :
| Technologie | Avantages | Inconvénients | Verdict |
|-------------|-----------|---------------|---------|
| React | Écosystème riche, standard industrie | Courbe d'apprentissage | ✅ Choisi |
| Vue.js | Plus simple | Moins de bibliothèques | ❌ |
| Angular | Complet | Trop lourd pour ce projet | ❌ |
| Vanilla JS | Pas de dépendances | Code spaghetti | ❌ |

### Pourquoi Vite ?

**Problème** : Les outils de build JavaScript traditionnels (Webpack) sont lents.

**Solution** : Vite est un outil de build moderne, ultra-rapide.

```
Comparaison temps de démarrage :
- Webpack : ~10 secondes
- Vite    : ~0.5 seconde
```

### Pourquoi Tailwind CSS ?

**Problème** : Écrire du CSS classique prend du temps et génère beaucoup de code.

**Solution** : Tailwind permet d'écrire le style directement dans le HTML avec des classes utilitaires.

```html
<!-- CSS classique : 2 fichiers -->
<div class="card">...</div>
/* styles.css */
.card { padding: 16px; background: white; border-radius: 8px; }

<!-- Tailwind : tout en un -->
<div class="p-4 bg-white rounded-lg">...</div>
```

## 4.2 Backend : FastAPI (Python)

### Pourquoi Python ?

**Problème** : L'équipe connaît déjà Python, et la plupart des bibliothèques IA sont en Python.

**Solution** : Utiliser Python pour le backend permet de réutiliser les compétences existantes.

### Pourquoi FastAPI ?

**Problème** : On a besoin d'une API qui supporte le **streaming** (envoi progressif des réponses IA).

**Solution** : FastAPI est un framework Python moderne qui supporte nativement :
- Le streaming (Server-Sent Events)
- La validation automatique des données
- La documentation automatique (Swagger)
- Les performances élevées (async/await)

**Alternatives considérées** :
| Framework | Streaming | Performance | Documentation auto | Verdict |
|-----------|-----------|-------------|-------------------|---------|
| FastAPI | ✅ Natif | ✅ Excellente | ✅ Oui | ✅ Choisi |
| Flask | ⚠️ Manuel | ⚠️ Moyenne | ❌ Non | ❌ |
| Django | ⚠️ Complexe | ⚠️ Moyenne | ❌ Non | ❌ |
| Express (Node) | ✅ Natif | ✅ Bonne | ❌ Non | ❌ Pas Python |

## 4.3 LLM : Ollama + Ministral 3B

### Pourquoi Ollama ?

**Problème** : Comment exécuter un modèle d'IA en local sans compétences en Machine Learning ?

**Solution** : Ollama est un outil qui simplifie l'exécution de modèles IA localement.

```bash
# Sans Ollama : Installation complexe
pip install torch transformers accelerate
# + Configuration CUDA, mémoire, etc.

# Avec Ollama : Une seule commande
ollama pull ministral:3b
ollama run ministral:3b
```

### Pourquoi Ministral 3B ?

**Problème** : On a un serveur avec 8 Go de RAM, pas de GPU. Quel modèle choisir ?

**Solution** : Ministral 3B est un modèle français, léger et performant.

| Modèle | Taille | RAM requise | Qualité SQL | Verdict |
|--------|--------|-------------|-------------|---------|
| GPT-4 | Cloud | N/A | Excellente | ❌ Pas local |
| Llama 70B | 40 Go | 64 Go | Excellente | ❌ Trop gros |
| Mistral 7B | 4 Go | 16 Go | Bonne | ⚠️ Limite |
| **Ministral 3B** | 2 Go | 8 Go | Correcte | ✅ Choisi |

### Qu'est-ce qu'un LLM ?

Un **Large Language Model** (LLM) est un programme qui a "lu" des milliards de textes et qui peut :
- Comprendre des questions en langage naturel
- Générer du texte cohérent
- Suivre des instructions

**Analogie** : C'est comme un stagiaire très cultivé qui a lu toute la documentation du monde, mais qui peut parfois se tromper ou inventer des choses.

## 4.4 Base de Données : SQLite

### Pourquoi SQLite ?

**Problème** : On doit stocker des données (utilisateurs, conversations, logs) sans installer un serveur de base de données.

**Solution** : SQLite est une base de données intégrée dans un simple fichier.

```
PostgreSQL/MySQL : Serveur séparé, configuration complexe
SQLite          : Un fichier .db, aucune configuration
```

**Utilisé pour** :
- `users.db` : Comptes utilisateurs
- `conversations.db` : Historique des chats
- `audit.db` : Logs des actions

**Note** : Pour la production avec beaucoup d'utilisateurs, on migrerait vers PostgreSQL.

## 4.5 Conteneurisation : Docker

### Pourquoi Docker ?

**Problème** : "Ça marche sur ma machine" - Le code fonctionne en développement mais pas en production.

**Solution** : Docker crée des "conteneurs" qui embarquent tout l'environnement nécessaire.

**Analogie** : 
- Sans Docker : Vous envoyez une recette de cuisine (le code) et espérez que le cuisinier (le serveur) a tous les ingrédients.
- Avec Docker : Vous envoyez un plat préparé sous vide (le conteneur) qui contient déjà tout.

```
┌─────────────────────────────────────────┐
│            Conteneur Docker             │
│  ┌─────────────────────────────────┐    │
│  │  Application                    │    │
│  │  + Python 3.11                  │    │
│  │  + Toutes les dépendances       │    │
│  │  + Configuration                │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

# 5. Architecture Globale

## 5.1 Structure des Dossiers

```
Pstral/
│
├── backend/                    # Code serveur (Python/FastAPI)
│   ├── app/
│   │   ├── api/               # Points d'entrée HTTP
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py        # Connexion/inscription
│   │   │           ├── chat.py        # Conversation avec l'IA
│   │   │           ├── sql_execute.py # Exécution SQL
│   │   │           └── audit.py       # Logs d'audit
│   │   │
│   │   ├── core/              # Configuration et sécurité
│   │   │   ├── config.py      # Variables d'environnement
│   │   │   ├── auth.py        # Gestion JWT
│   │   │   └── security.py    # Validation des requêtes
│   │   │
│   │   ├── domain/            # Logique métier
│   │   │   ├── models/        # Structures de données
│   │   │   └── services/      # Services métier
│   │   │
│   │   ├── infrastructure/    # Connexions externes
│   │   │   ├── database/      # SQLite, Oracle
│   │   │   └── llm/           # Communication Ollama
│   │   │
│   │   └── main.py            # Point d'entrée
│   │
│   ├── Dockerfile             # Image Docker backend
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                  # Code client (React)
│   ├── src/
│   │   ├── components/        # Composants visuels
│   │   │   ├── Chat/          # Interface de chat
│   │   │   ├── Auth/          # Page de connexion
│   │   │   └── Layout/        # Structure de page
│   │   │
│   │   ├── contexts/          # État global (Auth)
│   │   ├── services/          # Appels API
│   │   └── App.jsx            # Composant racine
│   │
│   ├── Dockerfile.prod        # Image Docker production
│   └── nginx.conf             # Configuration serveur web
│
├── ollama/                    # Configuration IA
│   └── entrypoint.sh          # Script de démarrage
│
├── docker-compose.yml         # Développement local
└── docker-compose.ionos.yml   # Production IONOS
```

## 5.2 Pourquoi cette Structure ?

### Pattern "Clean Architecture"

L'idée est de séparer le code en couches indépendantes :

```
┌─────────────────────────────────────────────────────────────────┐
│                         API (endpoints/)                        │
│   Reçoit les requêtes HTTP, valide les entrées, retourne JSON   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN (services/)                         │
│   Contient la logique métier, indépendante de la technologie    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE (database/, llm/)                │
│   Communique avec les systèmes externes (BDD, IA, APIs)         │
└─────────────────────────────────────────────────────────────────┘
```

**Avantage** : Si on change de base de données (SQLite → PostgreSQL), seule la couche Infrastructure change.

---

# 6. Phase 1 : Le Cœur - Communication avec l'IA

## 6.1 Le Problème à Résoudre

> Comment envoyer une question à l'IA et recevoir une réponse en temps réel ?

## 6.2 La Solution : Streaming avec Server-Sent Events

### Pourquoi le Streaming ?

Sans streaming :
```
Utilisateur: "Génère une requête SQL pour..."
[Attente 10 secondes...]
IA: "Voici la requête complète : SELECT ... FROM ... WHERE ..."
```

Avec streaming :
```
Utilisateur: "Génère une requête SQL pour..."
IA: "Voici"
IA: " la"
IA: " requête"
IA: " : SELECT"
IA: " ..."
(L'utilisateur voit la réponse s'écrire en temps réel)
```

### Comment ça Marche ?

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│ Frontend │         │ Backend  │         │  Ollama  │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │
     │  POST /chat        │                    │
     │ ────────────────▶  │                    │
     │                    │  POST /api/generate│
     │                    │ ────────────────▶  │
     │                    │                    │
     │                    │  ◀─ chunk 1 ───────│
     │  ◀─ chunk 1 ───────│                    │
     │                    │  ◀─ chunk 2 ───────│
     │  ◀─ chunk 2 ───────│                    │
     │                    │  ◀─ chunk 3 ───────│
     │  ◀─ chunk 3 ───────│                    │
     │        ...         │        ...         │
```

## 6.3 Le Code Expliqué

### Backend : `ollama_client.py`

**Fichier** : `backend/app/infrastructure/llm/ollama_client.py`

```python
# Ce fichier gère la communication avec Ollama

import httpx
from typing import AsyncGenerator

async def stream_chat(messages: list, model: str) -> AsyncGenerator[str, None]:
    """
    Envoie une conversation à Ollama et retourne les réponses en streaming.
    
    Paramètres:
    - messages: Liste des messages de la conversation
    - model: Nom du modèle à utiliser (ex: "ministral:3b")
    
    Retourne:
    - Un générateur qui produit des morceaux de texte
    """
    
    # Prépare la requête pour Ollama
    payload = {
        "model": model,
        "messages": messages,
        "stream": True  # Active le streaming
    }
    
    # Ouvre une connexion HTTP persistante
    async with httpx.AsyncClient() as client:
        # Envoie la requête en mode streaming
        async with client.stream(
            "POST",
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=300  # 5 minutes max
        ) as response:
            # Lit chaque ligne reçue
            async for line in response.aiter_lines():
                if line:
                    # Parse le JSON et extrait le contenu
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content  # Envoie le morceau au frontend
```

**Vocabulaire** :
- `async` / `await` : Permet au code d'attendre sans bloquer
- `yield` : Retourne une valeur et "pause" la fonction
- `AsyncGenerator` : Fonction qui peut retourner plusieurs valeurs progressivement

### Backend : `chat.py` (Endpoint)

**Fichier** : `backend/app/api/v1/endpoints/chat.py`

```python
# Ce fichier définit l'API que le frontend appelle

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint principal pour discuter avec l'IA.
    
    Le frontend envoie:
    {
        "messages": [
            {"role": "user", "content": "Génère une requête pour..."}
        ],
        "mode": "sql"
    }
    
    Le backend retourne un flux de texte.
    """
    
    # 1. Construit le contexte selon le mode
    system_prompt = get_system_prompt(request.mode)
    
    # 2. Limite l'historique pour ne pas dépasser la mémoire du modèle
    messages = limit_history(request.messages, max_messages=10)
    
    # 3. Crée la fonction qui génère le streaming
    async def generate():
        async for chunk in stream_chat(messages, model="ministral:3b"):
            yield chunk
    
    # 4. Retourne une réponse streaming
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Frontend : `api.js`

**Fichier** : `frontend/src/services/api.js`

```javascript
// Ce fichier contient les fonctions pour appeler le backend

export async function* streamChat(messages, mode, signal) {
    /**
     * Appelle l'API de chat et retourne les réponses en streaming.
     * 
     * Le "async function*" crée un "générateur asynchrone" :
     * une fonction qui peut retourner plusieurs valeurs au fil du temps.
     */
    
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, mode }),
        signal  // Permet d'annuler la requête
    });
    
    // Obtient un "reader" pour lire le flux
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // Boucle infinie jusqu'à la fin du flux
    while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;  // Fin du streaming
        
        // Décode les bytes en texte et l'envoie
        const chunk = decoder.decode(value);
        yield chunk;  // Retourne ce morceau au composant React
    }
}
```

### Frontend : `ChatInterface.jsx`

**Fichier** : `frontend/src/components/Chat/ChatInterface.jsx`

```jsx
// Ce composant gère l'affichage du chat

const ChatInterface = ({ mode }) => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    
    const handleSendMessage = async (content) => {
        // 1. Ajoute le message utilisateur à l'affichage
        const userMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        
        // 2. Ajoute un message "vide" pour l'IA (sera rempli progressivement)
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
        
        // 3. Appelle l'API en streaming
        const generator = streamChat([...messages, userMessage], mode);
        
        // 4. Pour chaque morceau reçu, met à jour le message IA
        for await (const chunk of generator) {
            setMessages(prev => {
                const updated = [...prev];
                // Ajoute le chunk au dernier message
                updated[updated.length - 1].content += chunk;
                return updated;
            });
        }
        
        setIsLoading(false);
    };
    
    return (
        <div>
            {messages.map((msg, i) => (
                <MessageBubble key={i} {...msg} />
            ))}
            <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
    );
};
```

## 6.4 Résumé du Flux

```
1. Utilisateur tape "Génère une requête pour lister les clients"
                          │
                          ▼
2. Frontend envoie POST /api/v1/chat avec le message
                          │
                          ▼
3. Backend reçoit la requête, ajoute le "system prompt" SQL
                          │
                          ▼
4. Backend appelle Ollama avec la conversation complète
                          │
                          ▼
5. Ollama génère la réponse token par token
                          │
                          ▼
6. Chaque token est renvoyé au Backend puis au Frontend
                          │
                          ▼
7. Frontend affiche chaque token, créant l'effet "machine à écrire"
```

---

# 7. Phase 2 : L'Interface Utilisateur

## 7.1 Le Problème à Résoudre

> Comment créer une interface de chat intuitive qui ressemble aux applications modernes ?

## 7.2 Structure des Composants React

```
App.jsx                    ← Point d'entrée, gère l'authentification
    │
    ├── LoginPage.jsx      ← Page de connexion (si non authentifié)
    │
    └── AuthenticatedApp   ← Application principale (si authentifié)
            │
            ├── Sidebar.jsx        ← Menu latéral (conversations)
            │
            └── ChatInterface.jsx  ← Zone de chat
                    │
                    ├── MessageBubble.jsx  ← Bulle de message
                    │
                    └── ChatInput.jsx      ← Zone de saisie
```

## 7.3 Concepts React Expliqués

### Les Composants

Un composant React est une **fonction qui retourne du HTML**.

```jsx
// Composant simple
function Greeting({ name }) {
    return <h1>Bonjour, {name}!</h1>;
}

// Utilisation
<Greeting name="Jean" />  // Affiche: <h1>Bonjour, Jean!</h1>
```

### L'État (State)

L'état permet à un composant de "se souvenir" de données.

```jsx
function Counter() {
    // useState retourne [valeur, fonctionPourModifier]
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Compteur: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                +1
            </button>
        </div>
    );
}
```

### Les Effets (useEffect)

Les effets permettent d'exécuter du code à certains moments.

```jsx
function ChatInterface({ sessionId }) {
    const [messages, setMessages] = useState([]);
    
    // S'exécute quand sessionId change
    useEffect(() => {
        // Charge les messages sauvegardés
        const saved = localStorage.getItem(`chat_${sessionId}`);
        if (saved) {
            setMessages(JSON.parse(saved));
        }
    }, [sessionId]);  // Dépendance : s'exécute si sessionId change
    
    // S'exécute quand messages change
    useEffect(() => {
        // Sauvegarde les messages
        localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages));
    }, [messages]);
    
    return <div>...</div>;
}
```

## 7.4 Le Composant MessageBubble Expliqué

**Fichier** : `frontend/src/components/Chat/MessageBubble.jsx`

```jsx
const MessageBubble = ({ role, content, isThinking }) => {
    // role = "user" ou "assistant"
    // content = le texte du message
    // isThinking = true si l'IA est en train de réfléchir
    
    const isUser = role === 'user';
    
    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            {/* Bulle de message */}
            <div className={`
                px-6 py-4 rounded-2xl
                ${isUser 
                    ? 'bg-gradient-to-br from-indigo-600 to-purple-700 text-white' 
                    : 'bg-glass-surface text-slate-200'
                }
            `}>
                {isThinking ? (
                    // Animation de chargement
                    <div className="flex items-center gap-3">
                        <div className="animate-bounce">●</div>
                        <div className="animate-bounce">●</div>
                        <div className="animate-bounce">●</div>
                        <span>Réflexion en cours...</span>
                    </div>
                ) : (
                    // Affiche le contenu avec formatage Markdown
                    <Markdown>{content}</Markdown>
                )}
            </div>
        </div>
    );
};
```

### Les Classes Tailwind Expliquées

| Classe | Effet | Équivalent CSS |
|--------|-------|----------------|
| `flex` | Active Flexbox | `display: flex` |
| `justify-end` | Aligne à droite | `justify-content: flex-end` |
| `px-6` | Padding horizontal 24px | `padding-left: 24px; padding-right: 24px` |
| `py-4` | Padding vertical 16px | `padding-top: 16px; padding-bottom: 16px` |
| `rounded-2xl` | Coins arrondis | `border-radius: 16px` |
| `bg-gradient-to-br` | Dégradé vers bas-droite | `background: linear-gradient(...)` |
| `text-white` | Texte blanc | `color: white` |

---

# 8. Phase 3 : Sécurité et Authentification

## 8.1 Le Problème à Résoudre

> Comment s'assurer que seuls les employés autorisés peuvent utiliser l'application ?

## 8.2 La Solution : JWT (JSON Web Tokens)

### Qu'est-ce qu'un JWT ?

Un JWT est un "ticket d'entrée" numérique qui prouve l'identité de l'utilisateur.

```
┌─────────────────────────────────────────────────────────────────┐
│                          JWT Token                              │
├─────────────────────────────────────────────────────────────────┤
│  Header     │  {"alg": "HS256", "typ": "JWT"}                   │
├─────────────────────────────────────────────────────────────────┤
│  Payload    │  {"sub": "admin", "exp": 1737500000}              │
│             │  (qui + expiration)                               │
├─────────────────────────────────────────────────────────────────┤
│  Signature  │  HMAC-SHA256(header + payload, SECRET_KEY)        │
│             │  (preuve que le serveur a créé ce token)          │
└─────────────────────────────────────────────────────────────────┘
```

### Flux d'Authentification

```
1. Utilisateur entre son login/mot de passe
                    │
                    ▼
2. Frontend envoie POST /api/v1/auth/login
                    │
                    ▼
3. Backend vérifie les identifiants dans la BDD
                    │
                    ▼
4. Si OK, Backend génère un JWT et le retourne
                    │
                    ▼
5. Frontend stocke le JWT dans localStorage
                    │
                    ▼
6. Pour chaque requête suivante, Frontend envoie:
   Header: "Authorization: Bearer <JWT>"
                    │
                    ▼
7. Backend vérifie le JWT avant de traiter la requête
```

## 8.3 Le Code Expliqué

### Backend : `auth.py` (Core)

**Fichier** : `backend/app/core/auth.py`

```python
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Configuration du hashage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe correspond à son hash.
    
    Pourquoi hasher ?
    - On ne stocke JAMAIS les mots de passe en clair
    - Si la BDD est volée, les mots de passe restent secrets
    
    bcrypt est un algorithme lent exprès (pour ralentir les attaques)
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Crée un JWT contenant les données de l'utilisateur.
    
    Exemple de data: {"sub": "admin"}
    
    Le token résultant contient:
    - Les données (sub = subject = username)
    - La date d'expiration
    - Une signature cryptographique
    """
    to_encode = data.copy()
    
    # Ajoute une expiration (24 heures)
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    
    # Signe le token avec la clé secrète
    # Si quelqu'un modifie le token, la signature ne correspondra plus
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )
    
    return encoded_jwt


async def get_current_user(token: str) -> User:
    """
    Vérifie un JWT et retourne l'utilisateur correspondant.
    
    Cette fonction est appelée automatiquement par FastAPI
    pour chaque endpoint protégé.
    """
    try:
        # Décode et vérifie le token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        
        # Récupère l'utilisateur de la BDD
        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Utilisateur inconnu")
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
```

### Frontend : `AuthContext.jsx`

**Fichier** : `frontend/src/contexts/AuthContext.jsx`

```jsx
// Ce fichier gère l'état d'authentification global

import { createContext, useContext, useState, useEffect } from 'react';

// Crée un "contexte" = espace de stockage accessible partout
const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    // Au chargement, vérifie si un token existe
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            // Vérifie que le token est encore valide
            verifyToken(token)
                .then(user => setUser(user))
                .catch(() => localStorage.removeItem('token'))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);
    
    const login = async (username, password) => {
        // Appelle l'API de login
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            body: new URLSearchParams({ username, password })
        });
        
        if (!response.ok) {
            throw new Error('Identifiants incorrects');
        }
        
        const data = await response.json();
        
        // Stocke le token
        localStorage.setItem('token', data.access_token);
        
        // Met à jour l'état
        setUser(data.user);
    };
    
    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };
    
    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

// Hook personnalisé pour utiliser le contexte
export function useAuth() {
    return useContext(AuthContext);
}
```

## 8.4 Sécurité SQL : Protection contre les Injections

### Le Problème

Un utilisateur malveillant pourrait essayer d'exécuter des commandes dangereuses :

```
Utilisateur: "Génère une requête pour : DROP TABLE clients; --"
```

### La Solution

**Fichier** : `backend/app/core/security.py`

```python
DANGEROUS_KEYWORDS = ["DROP", "DELETE", "UPDATE", "TRUNCATE", "ALTER"]

def validate_query(query: str) -> tuple[bool, str]:
    """
    Vérifie qu'une requête SQL est sûre à exécuter.
    
    Règles:
    1. Seules les requêtes SELECT sont autorisées
    2. Les mots-clés dangereux sont bloqués
    3. Les injections SQL classiques sont détectées
    """
    query_upper = query.upper()
    
    # Vérifie que c'est un SELECT
    if not query_upper.strip().startswith("SELECT"):
        return False, "Seules les requêtes SELECT sont autorisées"
    
    # Vérifie les mots-clés dangereux
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in query_upper:
            return False, f"Mot-clé interdit: {keyword}"
    
    return True, "OK"
```

---

# 9. Phase 4 : Fonctionnalités Métier

## 9.1 Les Modes de Conversation

### Pourquoi des Modes ?

L'IA doit savoir quel type de réponse vous attendez :

| Mode | Comportement | Exemple de prompt système |
|------|--------------|---------------------------|
| `sql` | Génère des requêtes Oracle | "Tu es un expert SQL Oracle. Génère des requêtes optimisées..." |
| `chat` | Conversation générale | "Tu es un assistant technique. Réponds de façon concise..." |

### Implémentation

**Fichier** : `backend/app/core/prompts.py`

```python
SYSTEM_PROMPTS = {
    "sql": """Tu es un expert en bases de données Oracle.
    
    Ton rôle:
    - Générer des requêtes SQL à partir de questions en français
    - Utiliser la syntaxe Oracle (NVL, ROWNUM, TO_DATE, etc.)
    - Expliquer chaque requête générée
    
    Format de réponse:
    1. Requête SQL dans un bloc ```sql
    2. Explication en français
    
    Important:
    - Ne génère JAMAIS de DROP, DELETE, UPDATE
    - Utilise des alias clairs
    - Optimise les performances (index, sous-requêtes)
    """,
    
    "chat": """Tu es un assistant technique pour Pack Solutions.
    
    Ton rôle:
    - Répondre aux questions techniques
    - Aider à résoudre les problèmes
    - Être concis et précis
    """
}

def get_system_prompt(mode: str) -> str:
    return SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["chat"])
```

## 9.2 Export des Conversations

### Export JSON

```javascript
const handleExportJSON = () => {
    const data = {
        mode,
        exportedAt: new Date().toISOString(),
        messages
    };
    
    // Crée un fichier téléchargeable
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Déclenche le téléchargement
    const a = document.createElement('a');
    a.href = url;
    a.download = `pstral-chat-${Date.now()}.json`;
    a.click();
};
```

### Export PDF

Utilise l'API d'impression du navigateur :

```javascript
const handleExportPDF = () => {
    // Ouvre une nouvelle fenêtre avec le contenu formaté
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head><title>Export Pstral</title></head>
            <body>
                ${messages.map(m => `<p>${m.content}</p>`).join('')}
            </body>
        </html>
    `);
    
    // Ouvre la boîte de dialogue d'impression
    // L'utilisateur peut choisir "Enregistrer en PDF"
    printWindow.print();
};
```

## 9.3 Exécution SQL

### Le Flux

```
1. L'IA génère une requête SQL
                │
                ▼
2. L'utilisateur clique sur "Exécuter"
                │
                ▼
3. Frontend envoie POST /api/v1/sql/execute
                │
                ▼
4. Backend valide la requête (sécurité)
                │
                ▼
5. Si OK, Backend exécute sur Oracle
                │
                ▼
6. Backend retourne les résultats
                │
                ▼
7. Frontend affiche dans une modal
```

---

# 10. Phase 5 : Déploiement Production

## 10.1 Le Problème à Résoudre

> Comment faire fonctionner l'application sur un serveur avec seulement 8 Go de RAM ?

## 10.2 Architecture Docker Production

```
┌─────────────────────────────────────────────────────────────────┐
│                      VPS IONOS (8 Go RAM)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Docker Compose                        │   │
│   │                                                         │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │   │
│   │   │   Nginx     │  │   Backend   │  │    Ollama     │  │   │
│   │   │   256 Mo    │  │    1 Go     │  │     5 Go      │  │   │
│   │   │   :80       │  │   :8000     │  │   :11434      │  │   │
│   │   └──────┬──────┘  └──────┬──────┘  └───────────────┘  │   │
│   │          │                │                │            │   │
│   │          └────────────────┴────────────────┘            │   │
│   │                    Réseau Docker                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   RAM utilisée: ~6.25 Go / 8 Go (marge de sécurité: 1.75 Go)   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 10.3 Le Fichier docker-compose.ionos.yml Expliqué

```yaml
version: '3.8'

services:
  # Service 1 : Ollama (IA)
  ollama:
    image: ollama/ollama:latest
    volumes:
      # Stocke les modèles de façon persistante
      - ollama-data:/root/.ollama
      # Monte le script de démarrage
      - ./ollama/entrypoint.sh:/entrypoint.sh
    entrypoint: ["/bin/bash", "/entrypoint.sh"]
    deploy:
      resources:
        limits:
          memory: 5G  # Maximum 5 Go de RAM
    healthcheck:
      # Vérifie que Ollama répond
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Service 2 : Backend (API)
  backend:
    build: ./backend
    depends_on:
      ollama:
        condition: service_healthy  # Attend qu'Ollama soit prêt
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434  # Nom du service Docker
      - SECRET_KEY=${SECRET_KEY}  # Depuis le fichier .env
    deploy:
      resources:
        limits:
          memory: 1G  # Maximum 1 Go de RAM

  # Service 3 : Frontend (Nginx)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"  # Expose sur le port 80 (HTTP)
    depends_on:
      - backend
    deploy:
      resources:
        limits:
          memory: 256M  # Maximum 256 Mo de RAM
```

## 10.4 Le Script Entrypoint Ollama

**Fichier** : `ollama/entrypoint.sh`

```bash
#!/bin/bash
# Ce script démarre Ollama et télécharge le modèle automatiquement

# Démarre le serveur Ollama en arrière-plan
ollama serve &

# Attend que le serveur soit prêt
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "Ollama est prêt!"
        break
    fi
    echo "Attente... ($i/30)"
    sleep 2
done

# Vérifie si le modèle est déjà téléchargé
if ! ollama list | grep -q "ministral:3b"; then
    echo "Téléchargement du modèle ministral:3b..."
    ollama pull ministral:3b
fi

# Garde le conteneur en vie
wait
```

## 10.5 Configuration Nginx (Reverse Proxy)

### Pourquoi un Reverse Proxy ?

```
Sans Nginx:
- Frontend: http://serveur:5173
- Backend: http://serveur:8000

Problème: Deux ports différents = problèmes de CORS

Avec Nginx:
- Tout passe par: http://serveur:80
- Nginx route /api/* vers le backend
- Nginx sert les fichiers statiques pour le reste
```

**Fichier** : `frontend/nginx.conf`

```nginx
server {
    listen 80;
    
    # Sert les fichiers statiques du frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;  # SPA routing
    }
    
    # Proxy vers le backend pour les API
    location /api/ {
        proxy_pass http://backend:8000/api/;
        
        # En-têtes pour le proxy
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Désactive le buffering pour le streaming
        proxy_buffering off;
    }
}
```

---

# 11. Flux de Données Complet

## 11.1 Scénario : L'utilisateur pose une question SQL

```
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 1: Utilisateur tape "Liste les clients de Paris"         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 2: ChatInput.jsx capture le texte                        │
│                                                                 │
│   const handleSubmit = () => {                                  │
│       onSend({ content: "Liste les clients de Paris" });        │
│   };                                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 3: ChatInterface.jsx gère l'envoi                        │
│                                                                 │
│   1. Ajoute le message utilisateur à l'état                    │
│   2. Affiche "Réflexion en cours..."                           │
│   3. Appelle streamChat() de api.js                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 4: api.js envoie la requête HTTP                         │
│                                                                 │
│   fetch('/api/v1/chat', {                                       │
│       method: 'POST',                                           │
│       body: JSON.stringify({                                    │
│           messages: [...],                                      │
│           mode: "sql"                                           │
│       })                                                        │
│   });                                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 5: Nginx reçoit sur /api/* et transmet au Backend        │
│                                                                 │
│   location /api/ {                                              │
│       proxy_pass http://backend:8000/api/;                      │
│   }                                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 6: Backend FastAPI traite la requête                     │
│                                                                 │
│   @router.post("/chat")                                         │
│   async def chat(request):                                      │
│       # 1. Vérifie le token JWT                                │
│       # 2. Ajoute le prompt système SQL                        │
│       # 3. Limite l'historique à 10 messages                   │
│       # 4. Appelle Ollama                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 7: ollama_client.py communique avec Ollama               │
│                                                                 │
│   POST http://ollama:11434/api/chat                            │
│   {                                                             │
│       "model": "ministral:3b",                                 │
│       "messages": [                                             │
│           {"role": "system", "content": "Tu es un expert..."}   │
│           {"role": "user", "content": "Liste les clients..."}   │
│       ],                                                        │
│       "stream": true                                            │
│   }                                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 8: Ollama génère la réponse token par token              │
│                                                                 │
│   Token 1: "Voici"                                              │
│   Token 2: " la"                                                │
│   Token 3: " requête"                                           │
│   Token 4: " :"                                                 │
│   Token 5: "\n```sql"                                           │
│   Token 6: "\nSELECT"                                           │
│   ...                                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 9: Chaque token remonte la chaîne                        │
│                                                                 │
│   Ollama → Backend → Nginx → Frontend                          │
│                                                                 │
│   (Le streaming permet d'afficher progressivement)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 10: MessageBubble.jsx affiche avec effet machine à écrire│
│                                                                 │
│   Affichage progressif:                                         │
│   "Voici"                                                       │
│   "Voici la"                                                    │
│   "Voici la requête"                                            │
│   "Voici la requête :"                                          │
│   ...                                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ RÉSULTAT FINAL affiché à l'utilisateur:                        │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Voici la requête pour lister les clients de Paris :    │   │
│   │                                                         │   │
│   │ ```sql                                                  │   │
│   │ SELECT c.nom, c.prenom, c.email                         │   │
│   │ FROM clients c                                          │   │
│   │ WHERE c.ville = 'Paris'                                 │   │
│   │ ORDER BY c.nom;                                         │   │
│   │ ```                                                     │   │
│   │                                                         │   │
│   │ Cette requête sélectionne tous les clients...          │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

# 12. Glossaire Technique

| Terme | Définition Simple |
|-------|-------------------|
| **API** | Interface permettant à deux programmes de communiquer (comme un menu de restaurant) |
| **Async/Await** | Façon d'écrire du code qui attend sans bloquer |
| **Backend** | La partie "invisible" qui traite les données |
| **CORS** | Sécurité navigateur qui empêche les sites de communiquer entre eux |
| **Docker** | Outil pour emballer une application avec toutes ses dépendances |
| **Endpoint** | URL spécifique d'une API (ex: `/api/v1/chat`) |
| **Frontend** | La partie visible (interface utilisateur) |
| **Hook (React)** | Fonction spéciale (`useState`, `useEffect`) pour gérer l'état |
| **JWT** | Ticket numérique prouvant l'identité d'un utilisateur |
| **LLM** | Grand modèle de langage (IA qui comprend et génère du texte) |
| **Nginx** | Serveur web ultra-performant, souvent utilisé comme proxy |
| **Prompt** | Instructions données à l'IA pour guider sa réponse |
| **REST** | Convention pour structurer les APIs web |
| **SSE** | Server-Sent Events - technique pour envoyer des données en continu |
| **State** | Données qu'un composant "se souvient" entre les rendus |
| **Streaming** | Envoi de données petit à petit (au lieu de tout d'un coup) |
| **Token (IA)** | Unité de texte (environ 4 caractères) |
| **Token (Auth)** | Identifiant d'authentification |

---

# 13. FAQ - Questions Fréquentes

## Questions Techniques

### Q: "Pourquoi ne pas utiliser directement l'API OpenAI ?"

**R**: Trois raisons principales :
1. **Confidentialité** : Les données sensibles de l'entreprise ne doivent pas quitter nos serveurs
2. **Coût** : L'API OpenAI facture à l'usage, Ollama est gratuit
3. **Contrôle** : On maîtrise entièrement l'infrastructure

### Q: "Pourquoi FastAPI plutôt que Django ?"

**R**: FastAPI est plus adapté car :
- Support natif du streaming (Server-Sent Events)
- Plus léger et rapide
- Documentation automatique
- Django aurait été surdimensionné pour ce projet

### Q: "Comment le modèle IA sait générer du SQL ?"

**R**: Le modèle Ministral a été entraîné sur des milliards de textes, incluant de la documentation SQL, des tutoriels, du code. Il a "appris" les patterns du SQL. Le "system prompt" l'oriente ensuite vers la génération SQL Oracle spécifiquement.

### Q: "Que se passe-t-il si l'IA génère une mauvaise requête ?"

**R**: Plusieurs protections :
1. Le backend valide que c'est bien un SELECT
2. Les mots-clés dangereux (DROP, DELETE) sont bloqués
3. L'utilisateur peut voir et modifier la requête avant exécution
4. Toutes les actions sont loggées pour audit

## Questions Fonctionnelles

### Q: "Combien d'utilisateurs peuvent utiliser l'application simultanément ?"

**R**: Avec la configuration actuelle (8 Go RAM, CPU) :
- ~5-10 utilisateurs simultanés confortablement
- L'IA traite une requête à la fois (les autres attendent)

### Q: "Les conversations sont-elles conservées ?"

**R**: Oui, de deux façons :
1. **LocalStorage** (navigateur) : Sauvegarde côté client
2. **Base SQLite** (serveur) : Sauvegarde côté serveur pour l'historique

### Q: "Peut-on utiliser un autre modèle d'IA ?"

**R**: Oui ! Il suffit de changer la variable `OLLAMA_MODEL` dans le fichier `.env`. Exemples :
- `mistral:7b` : Plus performant mais plus lent
- `llama2:7b` : Alternative à Mistral
- `codellama:7b` : Spécialisé code

---

# 14. Annexes

## A. Commandes Utiles

### Développement Local

```bash
# Démarrer le backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Démarrer le frontend
cd frontend
npm install
npm run dev

# Démarrer Ollama
ollama serve
ollama run ministral:3b
```

### Production Docker

```bash
# Démarrer tout
docker compose -f docker-compose.ionos.yml up -d

# Voir les logs
docker compose -f docker-compose.ionos.yml logs -f

# Redémarrer un service
docker compose -f docker-compose.ionos.yml restart backend

# Arrêter tout
docker compose -f docker-compose.ionos.yml down
```

## B. Endpoints API

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/v1/auth/login` | Connexion utilisateur |
| POST | `/api/v1/auth/register` | Inscription |
| GET | `/api/v1/auth/me` | Profil utilisateur |
| POST | `/api/v1/chat` | Envoyer un message (streaming) |
| POST | `/api/v1/sql/execute` | Exécuter une requête SQL |
| GET | `/api/v1/conversations` | Liste des conversations |
| GET | `/api/v1/audit/logs` | Logs d'audit (admin) |

## C. Variables d'Environnement

| Variable | Obligatoire | Description |
|----------|-------------|-------------|
| `SECRET_KEY` | ✅ | Clé de signature JWT |
| `OLLAMA_MODEL` | ❌ | Modèle à utiliser (défaut: ministral:3b) |
| `MAX_HISTORY_MESSAGES` | ❌ | Limite de contexte (défaut: 10) |
| `ORACLE_DSN` | ❌ | Connexion Oracle |
| `ORACLE_USER` | ❌ | Utilisateur Oracle |
| `ORACLE_PASSWORD` | ❌ | Mot de passe Oracle |

## D. Structure de la Base de Données

### Table `users`

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    disabled INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table `audit_logs`

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    username TEXT,
    action TEXT NOT NULL,
    resource TEXT,
    details TEXT,
    status TEXT,
    ip_address TEXT
);
```

---

## Conclusion

Ce document vous donne une vue complète du projet Pstral. Les points clés à retenir :

1. **Architecture 3-tiers** : Frontend (React) → Backend (FastAPI) → LLM (Ollama)
2. **Sécurité** : JWT pour l'authentification, validation SQL, audit des actions
3. **Streaming** : Réponses en temps réel grâce aux Server-Sent Events
4. **Déploiement** : Docker avec limites de ressources pour serveur 8 Go

Pour toute question supplémentaire, consultez les fichiers source ou demandez à l'équipe technique.

---

*Document généré pour Pack Solutions - Usage interne uniquement*

