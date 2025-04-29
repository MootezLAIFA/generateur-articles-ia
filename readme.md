# Assistant de génération d'articles IA personnalisé

Application Streamlit permettant de générer des articles professionnels avec l'assistance de GPT-4o-mini/GPT-4o.

## Fonctionnalités

- Génération d'idées de sujets à partir d'un secteur, de mots-clés et de services
- Recherche d'articles récents pour inspiration (moins de 72h)
- Proposition d'angles éditoriaux variés
- Personnalisation du ton, de la longueur et du style de l'article
- Génération automatique d'un plan d'article structuré
- Génération de l'article complet en markdown
- Possibilité d'exporter l'article final

## Prérequis

- Python 3.8+
- Compte OpenAI avec clé API
- Optionnel: Clé API pour Bing Search ou SerpAPI (pour la recherche d'articles récents)

## Installation

1. Cloner le dépôt:
```bash
git clone https://github.com/votreorganisation/assistant-articles-ia.git
cd assistant-articles-ia
```

2. Installer les dépendances avec Pipenv:
```bash
# Installer Pipenv si nécessaire
pip install pipenv

# Installer les dépendances du projet
pipenv install

# Installer aussi les dépendances de développement (optionnel)
pipenv install --dev
```

3. Créer un fichier `.env` à la racine du projet avec vos clés API:
```
OPENAI_API_KEY=votre_clé_openai
BING_API_KEY=votre_clé_bing_optionnelle
SERPAPI_KEY=votre_clé_serpapi_optionnelle
```

## Utilisation

### Lancement local

```bash
# Avec Pipenv
pipenv run app

# Ou directement
pipenv run streamlit run app.py
```

L'application sera alors accessible à l'adresse [http://localhost:8501](http://localhost:8501).

### Déploiement sur Streamlit Cloud

1. Connectez-vous à [Streamlit Cloud](https://streamlit.io/cloud)
2. Créez une nouvelle application en pointant vers votre dépôt GitHub
3. Configurez les variables d'environnement (clés API) dans les paramètres de l'application
4. Déployez l'application

## Structure du projet

- `app.py`: Application Streamlit principale
- `api.py`: Module d'API pour OpenAI et la recherche d'articles
- `requirements.txt`: Dépendances du projet
- `.env`: Fichier de configuration local pour les clés API (non commité)

## Points techniques

- L'application utilise les requêtes HTTP directes à l'API OpenAI plutôt que le SDK
- Le coût est optimisé en utilisant GPT-4o-mini par défaut et en passant à GPT-4o uniquement pour les articles longs
- L'interface est responsive et optimisée pour une utilisation fluide
- La recherche d'articles est simulée par GPT si aucune API de recherche n'est configurée

## Personnalisation

### Modèles d'IA
Vous pouvez modifier les modèles utilisés dans le fichier `api.py`:
- Pour réduire les coûts: utiliser uniquement `gpt-4o-mini` partout
- Pour améliorer la qualité: utiliser `gpt-4o` pour toutes les étapes

### Paramètres de recherche d'articles
Dans `api.py`, vous pouvez ajuster:
- La fraîcheur des articles (actuellement 72h)
- Le nombre d'articles retournés
- Les API de recherche utilisées

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.