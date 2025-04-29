import streamlit as st
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import requests
from bs4 import BeautifulSoup
import trafilatura
import json
import time

# Configuration de la page
st.set_page_config(
    page_title="Générateur d'Articles IA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4A4A4A;
        margin-bottom: 1rem;
    }

    .subtitle {
        font-size: 1.8rem;
        font-weight: 500;
        color: #6B6B6B;
        margin-bottom: 1.5rem;
    }

    .card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1.5rem;
    }

    .btn-primary {
        background-color: #4A7AFF;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
    }

    .btn-primary:hover {
        background-color: #3A6AEF;
    }
</style>
""", unsafe_allow_html=True)


# Fonction pour appeler l'API OpenAI
def call_openai_api(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 1000) -> Dict[str, Any]:
    """
    Envoie une requête à l'API OpenAI et retourne la réponse.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        st.error("Clé API OpenAI non trouvée. Veuillez configurer votre clé API.")
        st.stop()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur HTTP lors de l'appel à l'API OpenAI: {e}")
        st.error(f"Détails: {response.text}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API OpenAI: {e}")
        st.stop()


def extract_keywords(title: str, max_keywords: int = 3) -> List[str]:
    """
    Extrait les mots-clés pertinents d'un titre.

    Args:
        title (str): Titre de l'article
        max_keywords (int): Nombre maximum de mots-clés à extraire

    Returns:
        List[str]: Liste des mots-clés extraits
    """
    # Charger les stopwords français
    stop_words = set([
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'à', 'en', 'et',
            'dans', 'pour', 'par', 'sur', 'qui', 'que', 'quoi', 'dont', 'comment'
        ])

    # Nettoyer et tokenizer le titre
    words = title.lower().split()

    # Filtrer les stopwords et garder uniquement les mots significatifs
    keywords = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    # Limiter le nombre de mots-clés
    return keywords[:max_keywords]


def search_recent_articles(selected_topic: str, sector: str, keywords: str, max_age_hours: int = 72,
                           num_results: int = 5) -> List[Dict[str, str]]:
    """
    Recherche d'articles récents basée sur le titre, le secteur et les mots-clés.

    Args:
        selected_topic (str): Titre de l'article choisi
        sector (str): Secteur d'activité
        keywords (str): Mots-clés initiaux
        max_age_hours (int): Âge maximum des articles
        num_results (int): Nombre de résultats

    Returns:
        List[Dict[str, str]]: Liste des articles trouvés
    """
    # Extraire les mots-clés du titre
    title_keywords = extract_keywords(selected_topic)

    # Combiner les mots-clés du titre, du secteur et initiaux
    search_terms = (
            title_keywords +
            [sector] +
            [kw.strip() for kw in keywords.split(',') if kw.strip()]
    )

    # Construire la requête de recherche
    query = ' '.join(set(search_terms))

    # Calculer la date minimale
    from_date = (datetime.now() - timedelta(hours=max_age_hours)).strftime("%Y-%m-%d")

    # Récupérer la clé API NewsAPI
    newsapi_key = os.environ.get("NEWSAPI_KEY", "")

    try:
        # Appel à l'API NewsAPI
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,  # Requête de recherche enrichie
            "from": from_date,  # Date minimale
            "sortBy": "relevancy",  # Trier par pertinence
            "apiKey": newsapi_key,
            "pageSize": num_results * 2,  # Demander plus pour filtrer
            "language": "fr"  # Articles en français
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Traitement des résultats
        if data.get("status") == "ok" and "articles" in data:
            articles = []
            for article in data["articles"]:
                # Vérifier la pertinence de l'article
                article_text = (
                    f"{article.get('title', '')} {article.get('description', '')}"
                ).lower()

                # Vérifier si les mots-clés sont présents
                if all(kw.lower() in article_text for kw in search_terms):
                    articles.append({
                        "title": article.get("title", "Article sans titre"),
                        "url": article.get("url", "#"),
                        "summary": article.get("description", "Pas de description disponible."),
                        "date": article.get("publishedAt", "")[:10]  # Format YYYY-MM-DD
                    })

                    # Stopper si on a assez d'articles
                    if len(articles) >= num_results:
                        break

            # Si pas assez d'articles, compléter avec la simulation
            if len(articles) < num_results:
                articles.extend(
                    simulate_search_with_openai(query, num_results - len(articles))
                )

            return articles

        # Basculement vers la simulation si pas de résultats
        return simulate_search_with_openai(query, num_results)

    except Exception as e:
        # En cas d'erreur, utilisation de la simulation
        return simulate_search_with_openai(query, num_results)


def simulate_search_with_openai(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Utilise OpenAI pour simuler une recherche d'articles récents.
    """
    prompt = f"""
    Génère {num_results} articles fictifs récents (moins de 72 heures) sur le sujet suivant: {query}.
    Pour chaque article, fournir:
    1. Un titre réaliste
    2. Une URL fictive mais plausible
    3. Un résumé de 3-5 lignes
    4. Une date de publication dans les dernières 72h

    Format JSON attendu:
    [
        {{
            "title": "Titre de l'article 1",
            "url": "https://example.com/article1",
            "summary": "Résumé de l'article en 3-5 lignes",
            "date": "YYYY-MM-DD"
        }},
        ...
    ]
    """

    response = call_openai_api(prompt, max_tokens=1500)

    try:
        articles_text = response["choices"][0]["message"]["content"]
        # On extrait le JSON des potentiels backticks markdown
        if "```json" in articles_text:
            articles_text = articles_text.split("```json")[1].split("```")[0].strip()
        elif "```" in articles_text:
            articles_text = articles_text.split("```")[1].split("```")[0].strip()

        articles = json.loads(articles_text)
        return articles
    except Exception as e:
        st.error(f"Erreur lors du parsing des articles simulés: {e}")
        return []


# Fonctions pour les différentes étapes du processus
def generate_topic_ideas(sector: str, keywords: str, services: str) -> List[str]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    st.write(f"Utilisation de la clé API: {api_key[:5]}...{api_key[-5:] if api_key else 'Non trouvée'}")

    if not api_key:
        st.error("Clé API OpenAI non trouvée. Veuillez configurer votre clé API.")
        st.stop()
    """
    Génère 5 idées de sujets d'articles basés sur les inputs utilisateur.
    """
    prompt = f"""
    En tant qu'expert en marketing de contenu, propose 5 idées de sujets d'articles pour le secteur "{sector}" 
    avec les mots-clés "{keywords}" et les services/produits "{services}".

    Pour chaque idée, fournir:
    - Un titre accrocheur et SEO-friendly
    - Une brève description du sujet (1-2 phrases)

    Présente les résultats sous forme de liste numérotée.
    """

    response = call_openai_api(prompt)

    # Afficher la réponse brute pour débogage
    st.write("Réponse brute de l'API:")
    st.write(response)

    ideas_text = response["choices"][0]["message"]["content"]
    st.write("Contenu du message:")
    st.write(ideas_text)

    # Approche simplifiée pour extraire les idées
    ideas = []
    for line in ideas_text.split("\n"):
        line = line.strip()
        if line and (line.startswith("1.") or line.startswith("2.") or
                     line.startswith("3.") or line.startswith("4.") or
                     line.startswith("5.")):
            # Extraire tout ce qui suit le numéro et le point
            parts = line.split(".", 1)
            if len(parts) > 1:
                ideas.append(parts[1].strip())

    # Si moins de 5 idées, générer des idées par défaut
    while len(ideas) < 5:
        ideas.append(f"Sujet sur {sector} et {keywords}")

    return ideas[:5]


def generate_editorial_angles(topic: str, sector: str) -> List[str]:
    """
    Génère 5 angles éditoriaux différents pour un sujet donné.
    """
    prompt = f"""
    Pour le sujet d'article "{topic}" dans le secteur "{sector}", propose 5 angles éditoriaux différents.
    Chaque angle doit être distinct et apporter une perspective unique.

    Exemples d'angles: analytique, émotionnel, didactique, anecdotique, comparatif, etc.

    Pour chaque angle, fournir:
    - Un nom court et descriptif
    - Une brève explication de l'approche (1-2 phrases)

    Présente les résultats sous forme de liste numérotée.
    """

    response = call_openai_api(prompt)
    angles_text = response["choices"][0]["message"]["content"]

    # Traitement pour extraire les angles
    angles = []
    current_angle = ""

    for line in angles_text.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            # Nouvelle entrée détectée
            if current_angle and len(current_angle) > 0:
                angles.append(current_angle)

            # Nettoyer la ligne
            clean_line = line.split(".", 1)[-1].strip() if "." in line else line.strip()
            clean_line = clean_line[1:].strip() if clean_line.startswith("-") else clean_line

            # Extraire juste le nom de l'angle si disponible
            if ":" in clean_line:
                angle_name = clean_line.split(":", 1)[0].strip()
                current_angle = angle_name
            else:
                current_angle = clean_line
        elif line and current_angle:
            # Ligne supplémentaire pour l'entrée actuelle
            continue

    # Ajouter le dernier angle s'il existe
    if current_angle and len(current_angle) > 0:
        angles.append(current_angle)

    # Garantir qu'on a au moins 5 angles
    if len(angles) < 5:
        additional_angles = ["Angle " + str(i + 1) for i in range(len(angles), 5)]
        angles.extend(additional_angles)

    return angles[:5]  # Limiter à 5 angles


def generate_article_outline(topic: str, angle: str, tone: str, length: str, style: str) -> Dict[str, Any]:
    """
    Génère un plan d'article structuré.
    """
    prompt = f"""
    Crée un plan détaillé pour un article sur le sujet:
    "{topic}" 

    Avec l'angle éditorial:
    "{angle}"

    Paramètres de rédaction:
    - Ton: {tone}
    - Longueur: {length}
    - Style: {style}

    Le plan doit inclure:
    1. Un titre accrocheur
    2. Une introduction
    3. 2-4 parties principales avec sous-points
    4. Une conclusion

    Format JSON attendu:
    {{
        "title": "Titre de l'article",
        "introduction": "Description de l'introduction",
        "sections": [
            {{
                "title": "Titre section 1",
                "subsections": ["Sous-point 1", "Sous-point 2"]
            }},
            ...
        ],
        "conclusion": "Description de la conclusion"
    }}
    """

    response = call_openai_api(prompt, max_tokens=1200)
    outline_text = response["choices"][0]["message"]["content"]

    # Extraction du JSON du texte
    try:
        if "```json" in outline_text:
            outline_json = outline_text.split("```json")[1].split("```")[0].strip()
        elif "```" in outline_text:
            outline_json = outline_text.split("```")[1].split("```")[0].strip()
        else:
            outline_json = outline_text.strip()

        outline = json.loads(outline_json)
        return outline
    except Exception as e:
        st.error(f"Erreur lors du parsing du plan: {e}")
        st.error(f"Texte reçu: {outline_text}")

        # Fournir un plan par défaut en cas d'erreur
        return {
            "title": f"Article sur {topic}",
            "introduction": "Introduction à définir",
            "sections": [
                {"title": "Première partie", "subsections": ["Point 1", "Point 2"]},
                {"title": "Deuxième partie", "subsections": ["Point 1", "Point 2"]},
            ],
            "conclusion": "Conclusion à définir"
        }


def scrape_and_summarize_article(url: str) -> Dict[str, str]:
    """
    Scrape et résume un article à partir de son URL

    Args:
        url (str): URL de l'article

    Returns:
        Dict contenant le contenu scrapé et résumé
    """
    try:
        # Utilisation de trafilatura pour extraction de contenu
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(downloaded)

        if not content:
            return None

        # Génération de résumé avec GPT
        summary_prompt = f"""
        Résume professionnellement le contenu suivant en mettant en avant 
        les points clés et les insights principaux. 

        Contenu de l'article:
        {content[:4000]}  # Limiter la longueur

        Consignes:
        - Résumé concis (150-250 mots)
        - Style professionnel
        - Mettre en évidence les informations essentielles
        - Structure claire
        """

        # Appel à l'API OpenAI pour le résumé
        summary_response = call_openai_api(
            summary_prompt,
            model="gpt-4o-mini",
            max_tokens=300
        )

        summary = summary_response["choices"][0]["message"]["content"]

        return {
            "original_content": content,
            "summary": summary
        }

    except Exception as e:
        print(f"Erreur de scrapping : {e}")
        return None


def process_articles_for_generation(recent_articles: List[Dict], max_articles: int = 3) -> List[Dict]:
    """
    Traite les articles pour la génération

    Args:
        recent_articles (List[Dict]): Articles à traiter
        max_articles (int): Nombre max d'articles à traiter

    Returns:
        Liste d'articles scrapés et résumés
    """
    processed_articles = []

    for article in recent_articles[:max_articles]:
        scraped_article = scrape_and_summarize_article(article['url'])

        if scraped_article:
            processed_articles.append({
                **article,
                **scraped_article
            })

    return processed_articles


def generate_article_with_context(
        topic: str,
        angle: str,
        processed_articles: List[Dict]
) -> str:
    """
    Génère un article avec contexte des articles scrapés

    Args:
        topic (str): Sujet de l'article
        angle (str): Angle éditorial
        processed_articles (List[Dict]): Articles traités

    Returns:
        Article généré
    """
    # Construire le contexte
    context = "\n\n".join([
        f"Article {i + 1} Résumé:\n{article['summary']}"
        for i, article in enumerate(processed_articles)
    ])

    generation_prompt = f"""
    Génère un article sur le sujet "{topic}" avec l'angle "{angle}".

    Contexte des articles récents:
    {context}

    Consignes:
    - Intègre les insights des articles scrapés
    - Apporte une perspective unique
    - Utilise les informations contextuelles
    - Maintiens une structure claire et professionnelle
    """

    response = call_openai_api(
        generation_prompt,
        model="gpt-4o-mini",
        max_tokens=1500
    )

    return response["choices"][0]["message"]["content"]


def generate_article(outline: Dict[str, Any], topic: str, angle: str, tone: str, length: str, style: str) -> str:
    """
    Génère l'article complet basé sur le plan, lss articles processesd et les paramètres.
    """
    processed_articles = process_articles_for_generation(
        st.session_state.recent_articles
    )

    # Déterminer la longueur approximative en mots
    word_count = {
        "Court (~300 mots)": 300,
        "Moyen (~600 mots)": 600,
        "Long (~1200 mots)": 1200
    }.get(length, 600)

    # Création du plan formaté pour le prompt
    outline_formatted = f"""
    Titre: {outline['title']}

    Introduction: {outline['introduction']}

    """

    for i, section in enumerate(outline['sections']):
        outline_formatted += f"Section {i + 1}: {section['title']}\n"
        for j, subsection in enumerate(section['subsections']):
            outline_formatted += f"- {subsection}\n"
        outline_formatted += "\n"

    outline_formatted += f"Conclusion: {outline['conclusion']}"

    prompt = f"""
    Rédige un article complet et professionnel sur le sujet "{topic}" avec l'angle "{angle}" 
    en suivant précisément le plan ci-dessous:

    {outline_formatted}

    Les articles réel pour inspiration : 
    {processed_articles}
    
    Paramètres de rédaction:
    - Ton: {tone}
    - Longueur cible: environ {word_count} mots
    - Style: {style}

    L'article doit être cohérent, engageant, et respecter les meilleures pratiques SEO sans compromettre la qualité éditoriale.
    Utilise des paragraphes clairs, des sous-titres pertinents, et une structure logique.
    """

    response = call_openai_api(prompt, max_tokens=2000)
    article_text = response["choices"][0]["message"]["content"]

    return article_text


# Initialisation des variables de session
if 'stage' not in st.session_state:
    st.session_state.stage = 1

if 'sector' not in st.session_state:
    st.session_state.sector = ""

if 'keywords' not in st.session_state:
    st.session_state.keywords = ""

if 'services' not in st.session_state:
    st.session_state.services = ""

if 'topic_ideas' not in st.session_state:
    st.session_state.topic_ideas = []

if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = ""

if 'recent_articles' not in st.session_state:
    st.session_state.recent_articles = []

if 'editorial_angles' not in st.session_state:
    st.session_state.editorial_angles = []

if 'selected_angle' not in st.session_state:
    st.session_state.selected_angle = ""

if 'selected_tone' not in st.session_state:
    st.session_state.selected_tone = ""

if 'selected_length' not in st.session_state:
    st.session_state.selected_length = ""

if 'selected_style' not in st.session_state:
    st.session_state.selected_style = ""

if 'article_outline' not in st.session_state:
    st.session_state.article_outline = {}

if 'final_article' not in st.session_state:
    st.session_state.final_article = ""


# Fonctions de navigation
def go_to_stage(stage):
    st.session_state.stage = stage


def next_stage():
    st.session_state.stage += 1


def prev_stage():
    if st.session_state.stage > 1:
        st.session_state.stage -= 1


# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=AI+Writer", width=150)
    st.markdown("### Étapes du processus")

    stages = [
        "1️⃣ Données initiales",
        "2️⃣ Choix du sujet",
        "3️⃣ Articles inspirants",
        "4️⃣ Angles éditoriaux",
        "5️⃣ Paramètres de rédaction",
        "6️⃣ Plan de l'article",
        "7️⃣ Article final"
    ]

    for i, stage in enumerate(stages):
        if i + 1 < st.session_state.stage:
            st.success(stage)
        elif i + 1 == st.session_state.stage:
            st.info(stage)
        else:
            st.markdown(stage)

    st.markdown("---")

    # Bouton pour recommencer
    if st.button("🔄 Recommencer"):
        for key in st.session_state.keys():
            if key != 'stage':
                del st.session_state[key]
        st.session_state.stage = 1
        st.rerun()

# Affichage principal selon l'étape
st.markdown("<h1 class='main-title'>🚀 Assistant de génération d'articles IA</h1>", unsafe_allow_html=True)

# Étape 1: Données initiales
if st.session_state.stage == 1:
    st.markdown("<h2 class='subtitle'>📝 Étape 1: Données initiales</h2>", unsafe_allow_html=True)

    with st.form("initial_data_form"):
        st.session_state.sector = st.text_input("Secteur d'activité", value=st.session_state.sector)
        st.session_state.keywords = st.text_input("Mots-clés (séparés par des virgules)",
                                                  value=st.session_state.keywords)
        st.session_state.services = st.text_input("Services/Produits associés", value=st.session_state.services)

        submit_button = st.form_submit_button("Générer des idées de sujets")

        if submit_button:
            if not st.session_state.sector or not st.session_state.keywords:
                st.error("Veuillez remplir au moins le secteur et les mots-clés.")
            else:
                with st.spinner("Génération d'idées en cours..."):
                    st.session_state.topic_ideas = generate_topic_ideas(
                        st.session_state.sector,
                        st.session_state.keywords,
                        st.session_state.services
                    )
                next_stage()
                st.rerun()

# Étape 2: Choix du sujet
elif st.session_state.stage == 2:
    st.markdown("<h2 class='subtitle'>🎯 Étape 2: Choix du sujet</h2>", unsafe_allow_html=True)

    # Idées générées
    st.markdown("### Idées de sujets générées:")
    for i, idea in enumerate(st.session_state.topic_ideas):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{i + 1}. {idea}**")
        with col2:
            if st.button("Choisir", key=f"choose_topic_{i}"):
                st.session_state.selected_topic = idea
                next_stage()
                st.rerun()

    # Option pour saisir un sujet personnalisé
    st.markdown("---")
    st.markdown("### Ou proposez votre propre sujet:")
    with st.form("custom_topic_form"):
        # Utilisez une clé unique pour l'input
        custom_topic = st.text_input("Sujet personnalisé", key="custom_topic_input")

        # Bouton de soumission
        submit_custom = st.form_submit_button("Utiliser ce sujet")

        # Traitement du sujet personnalisé
        if submit_custom and custom_topic:
            # Mettre à jour la variable de session
            st.session_state.selected_topic = custom_topic

            # Passer à l'étape suivante
            next_stage()
            st.rerun()

    # Navigation de retour
    if st.button("← Retour"):
        prev_stage()
        st.rerun()

# Étape 3: Articles inspirants
elif st.session_state.stage == 3:
    st.markdown("<h2 class='subtitle'>📚 Étape 3: Articles inspirants</h2>", unsafe_allow_html=True)

    # Afficher le sujet choisi
    st.markdown(f"### Sujet choisi: **{st.session_state.selected_topic}**")

    # Si les articles n'ont pas encore été recherchés
    if not st.session_state.recent_articles:
        with st.spinner("Recherche d'articles récents..."):
            # Utiliser les variables de session pour la recherche
            search_query = st.session_state.selected_topic

            # Appel avec tous les paramètres requis
            st.session_state.recent_articles = search_recent_articles(
                selected_topic=search_query,
                sector=st.session_state.sector,
                keywords=st.session_state.keywords
            )

    # Afficher les articles trouvés
    if st.session_state.recent_articles:
        st.markdown("### Articles récents pour inspiration:")

        for i, article in enumerate(st.session_state.recent_articles):
            with st.expander(f"{i + 1}. {article['title']}"):
                st.write(f"**Date:** {article['date']}")
                st.write(f"**URL:** {article['url']}")
                st.write(f"**Résumé:**")
                st.write(article['summary'])
    else:
        st.warning("Aucun article récent trouvé. Vous pouvez continuer sans inspiration externe.")

    # Navigation
    col1, col2 = st.columns(2)

    with col1:
        if st.button("← Retour"):
            prev_stage()
            st.rerun()

    with col2:
        if st.button("Continuer →"):
            next_stage()
            st.rerun()

# Étape 4: Angles éditoriaux
elif st.session_state.stage == 4:
    st.markdown("<h2 class='subtitle'>📐 Étape 4: Angles éditoriaux</h2>", unsafe_allow_html=True)

    # Afficher le sujet choisi
    st.markdown(f"### Sujet choisi: **{st.session_state.selected_topic}**")

    # Si les angles n'ont pas encore été générés
    if not st.session_state.editorial_angles:
        with st.spinner("Génération d'angles éditoriaux..."):
            st.session_state.editorial_angles = generate_editorial_angles(
                st.session_state.selected_topic,
                st.session_state.sector
            )

    # Afficher les angles proposés
    st.markdown("### Angles éditoriaux proposés:")

    for i, angle in enumerate(st.session_state.editorial_angles):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{i + 1}. {angle}**")
        with col2:
            if st.button("Choisir", key=f"choose_angle_{i}"):
                st.session_state.selected_angle = angle
                next_stage()
                st.rerun()

    # Option pour saisir un angle personnalisé
    st.markdown("---")
    st.markdown("### Ou proposez votre propre angle:")

    with st.form("custom_angle_form"):
        custom_angle = st.text_input("Angle personnalisé")
        submit_custom = st.form_submit_button("Utiliser cet angle")

        if submit_custom and custom_angle:
            st.session_state.selected_angle = custom_angle
            next_stage()
            st.rerun()

    # Navigation
    if st.button("← Retour"):
        prev_stage()
        st.rerun()

# Étape 5: Paramètres de rédaction
elif st.session_state.stage == 5:
    st.markdown("<h2 class='subtitle'>⚙️ Étape 5: Paramètres de rédaction</h2>", unsafe_allow_html=True)

    # Afficher le sujet et l'angle choisis
    st.markdown(f"### Sujet: **{st.session_state.selected_topic}**")
    st.markdown(f"### Angle: **{st.session_state.selected_angle}**")

    # Formulaire pour les paramètres
    with st.form("writing_params_form"):
        tone_options = [
            "Professionnel", "Dynamique", "Bienveillant", "Humoristique",
            "Formel", "Informatif", "Conversationnel", "Persuasif"
        ]
        st.session_state.selected_tone = st.selectbox(
            "Ton de l'article",
            options=tone_options,
            index=0 if not st.session_state.selected_tone else tone_options.index(st.session_state.selected_tone)
        )

        length_options = ["Court (~300 mots)", "Moyen (~600 mots)", "Long (~1200 mots)"]
        st.session_state.selected_length = st.selectbox(
            "Longueur de l'article",
            options=length_options,
            index=1 if not st.session_state.selected_length else length_options.index(st.session_state.selected_length)
        )

        style_options = ["Blog", "Article LinkedIn", "Post inspirant", "Tutoriel", "Analyse de marché", "Étude de cas"]
        st.session_state.selected_style = st.selectbox(
            "Style de l'article",
            options=style_options,
            index=0 if not st.session_state.selected_style else style_options.index(st.session_state.selected_style)
        )

        submit_params = st.form_submit_button("Générer le plan")

        if submit_params:
            next_stage()
            st.rerun()

    # Navigation
    if st.button("← Retour"):
        prev_stage()
        st.rerun()

# Étape 6 : Plan de l'article
elif st.session_state.stage == 6:
    st.markdown("<h2 class='subtitle'>📋 Étape 6: Plan de l'article</h2>", unsafe_allow_html=True)

    # Résumé des paramètres choisis
    st.markdown("### Paramètres sélectionnés:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Sujet:** {st.session_state.selected_topic}")
        st.markdown(f"**Angle:** {st.session_state.selected_angle}")
        st.markdown(f"**Ton:** {st.session_state.selected_tone}")
    with col2:
        st.markdown(f"**Longueur:** {st.session_state.selected_length}")
        st.markdown(f"**Style:** {st.session_state.selected_style}")

    # Générer le plan si nécessaire
    if not st.session_state.article_outline:
        with st.spinner("Génération du plan en cours..."):
            st.session_state.article_outline = generate_article_outline(
                st.session_state.selected_topic,
                st.session_state.selected_angle,
                st.session_state.selected_tone,
                st.session_state.selected_length,
                st.session_state.selected_style
            )

    # Afficher le plan
    st.markdown("### Plan proposé:")

    outline = st.session_state.article_outline

    st.markdown(f"**Titre:** {outline['title']}")
    st.markdown(f"**Introduction:** {outline['introduction']}")

    st.markdown("**Corps de l'article:**")
    for i, section in enumerate(outline['sections']):
        st.markdown(f"**{i + 1}. {section['title']}**")
        for subsection in section['subsections']:
            st.markdown(f"   - {subsection}")

    st.markdown(f"**Conclusion:** {outline['conclusion']}")

    # Options pour l'utilisateur
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("← Retour"):
            prev_stage()
            st.rerun()

    with col2:
        if st.button("🔄 Regénérer le plan"):
            st.session_state.article_outline = {}
            st.rerun()

    with col3:
        if st.button("✅ Valider le plan"):
            next_stage()
            st.rerun()

 # Étape 7: Article final
elif st.session_state.stage == 7:
    st.markdown("<h2 class='subtitle'>📝 Étape 7: Article final</h2>", unsafe_allow_html=True)

    # Vérifier que tous les paramètres nécessaires sont présents
    if (not st.session_state.selected_topic or
            not st.session_state.selected_angle or
            not st.session_state.selected_tone or
            not st.session_state.selected_length or
            not st.session_state.selected_style):
        st.error("Veuillez compléter toutes les étapes précédentes.")
        if st.button("← Retour aux paramètres"):
            st.session_state.stage = 5
            st.rerun()
    else:
        # Générer l'article si nécessaire
        if not st.session_state.final_article:
            with st.spinner("Génération de l'article en cours... Cela peut prendre quelques instants."):
                st.session_state.final_article = generate_article(
                    st.session_state.article_outline,  # Plan de l'article
                    st.session_state.selected_topic,  # Sujet choisi
                    st.session_state.selected_angle,  # Angle éditorial
                    st.session_state.selected_tone,  # Ton de l'article
                    st.session_state.selected_length,  # Longueur
                    st.session_state.selected_style  # Style
                )

        # Afficher l'article
        st.markdown("### Article généré:")
        st.markdown(st.session_state.final_article)

        # Options d'export
        st.markdown("---")
        st.markdown("### Options d'export")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copier dans le presse-papier"):
                # Utilisation de json.dumps pour éviter les problèmes d'échappement
                import json

                js_code = """
                        <script>
                        function copyToClipboard() {
                            const text = %s;
                            navigator.clipboard.writeText(text);
                            alert('Article copié dans le presse-papier!');
                        }
                        copyToClipboard();
                        </script>
                        """
                # Encodage sécurisé du texte pour JavaScript
                js_text = json.dumps(st.session_state.final_article)
                final_js = js_code % js_text
                st.components.v1.html(final_js, height=0)
                st.success("Article copié dans le presse-papier!")

        with col2:
            st.download_button(
                label="💾 Télécharger en format Markdown",
                data=st.session_state.final_article,
                file_name=f"article_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )

        # Option pour regénérer l'article
        if st.button("🔄 Regénérer l'article"):
            st.session_state.final_article = ""
            st.rerun()

        # Navigation
        if st.button("← Retour au plan"):
            st.session_state.stage = 6
            st.rerun()

# Pied de page
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        Assistant de génération d'articles IA personnalisé v1.0
    </div>
    """,
    unsafe_allow_html=True
)