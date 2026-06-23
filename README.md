# Système Multi-Agent : Générateur d'Applications Web

Un système basé sur l'architecture LangGraph permettant de concevoir, développer, tester et déployer de petites applications Flask + Vanilla JS entièrement via l'Intelligence Artificielle.

## Architecture

Ce projet repose sur un flux (*StateGraph*) composé de 4 agents spécialisés :
1. **Concepteur** : Analyse la requête de l'utilisateur et génère les spécifications fonctionnelles.
2. **Développeur** : Génère le code source de l'application (backend Python/Flask, frontend HTML/CSS/JS) et l'écrit sur le disque.
3. **Testeur (QA)** : Inspecte le code généré, détecte les bugs et valide ou rejette l'application.
4. **Déployeur** : Génère le fichier de dépendances et déploie le serveur localement.

## Interface Web & Human-in-the-Loop

Ce système intègre une **Interface Web Streamlit** permettant :
- D'interagir avec les agents via un chat conversationnel.
- D'intervenir au milieu du flux d'exécution grâce à la fonctionnalité **Human-in-the-Loop**. 
- Après chaque inspection du Testeur, le graphe se met en pause. Vous pouvez lire le rapport du Testeur et ajouter vos propres instructions manuelles pour forcer le Développeur à modifier certains aspects.

## Guide de Démarrage (Pour les nouveaux utilisateurs)

Si vous venez de cloner ce projet sur votre machine, suivez ces étapes exactes pour lancer l'application :

### 1. Cloner le dépôt et entrer dans le dossier
```bash
git clone https://github.com/TheMMZ/multi-agent-V2.git
cd multi-agent-V2
```

### 2. Créer un environnement virtuel (Recommandé)
Il est fortement conseillé d'utiliser un environnement virtuel pour ne pas polluer votre système :
```bash
python -m venv venv

# Sous Windows :
venv\Scripts\activate
# Sous Mac/Linux :
source venv/bin/activate
```

### 3. Installer les dépendances du système
Le système lui-même a besoin de quelques librairies pour fonctionner (Streamlit, LangGraph, LangChain, etc.) :
```bash
pip install -r requirements-system.txt
```

### 4. Configurer les clés API
Le projet nécessite des clés API pour fonctionner (soit Gemini via Google, soit Ollama en local).
1. Copiez le fichier `.env.example` et renommez-le en `.env` :
   ```bash
   cp .env.example .env
   ```
2. Ouvrez le fichier `.env` avec un éditeur de texte et ajoutez votre clé API Google :
   ```env
   GOOGLE_API_KEY="votre_cle_api_ici"
   ```

### 5. Lancer l'Interface Web
Démarrez le serveur graphique Streamlit :
```bash
streamlit run app_ui.py
```
Une fenêtre de votre navigateur s'ouvrira automatiquement sur `http://localhost:8501`. Vous pourrez alors chatter avec le système Multi-Agent !
