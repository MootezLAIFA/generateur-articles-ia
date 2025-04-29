# import requests
# import json
# import os
# import streamlit as st
# from typing import List, Dict, Any, Optional
# from datetime import datetime, timedelta
#
# def call_openai_api(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 1000) -> Dict[str, Any]:
#     """
#     Envoie une requête à l'API OpenAI et retourne la réponse.
#     """
#     api_key = os.environ.get("OPENAI_API_KEY", "")
#
#     if not api_key:
#         st.error("Clé API OpenAI non trouvée. Veuillez configurer votre clé API.")
#         st.stop()
#
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }
#
#     payload = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}],
#         "max_tokens": max_tokens,
#         "temperature": 0.7,
#     }
#
#     try:
#         response = requests.post(
#             "https://api.openai.com/v1/chat/completions",
#             headers=headers,
#             data=json.dumps(payload)
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.HTTPError as e:
#         st.error(f"Erreur HTTP lors de l'appel à l'API OpenAI: {e}")
#         st.error(f"Détails: {response.text}")
#         st.stop()
#     except Exception as e:
#         st.error(f"Erreur lors de l'appel à l'API OpenAI: {e}")
#         st.stop()
#
#
# def search_recent_articles(query: str, max_age_hours: int = 72, num_results: int = 5) -> List[Dict[str, str]]:
#     """
#     Recherche d'articles récents via NewsAPI.
#
#     Args:
#         query: Termes de recherche
#         max_age_hours: Âge maximum des articles en heures
#         num_results: Nombre de résultats à retourner
#
#     Returns:
#         Liste d'articles au format dictionnaire
#     """
#     # Calculer la date minimale (format YYYY-MM-DD)
#     from_date = (datetime.now() - timedelta(hours=max_age_hours)).strftime("%Y-%m-%d")
#
#     # Récupérer la clé API (d'abord chercher une clé spécifique, sinon utiliser celle fournie)
#     newsapi_key = os.environ.get("NEWSAPI_KEY", "")
#
#     try:
#         # Appel à l'API NewsAPI
#         url = f"https://newsapi.org/v2/everything"
#         params = {
#             "q": query,
#             "from": from_date,
#             "sortBy": "popularity",
#             "apiKey": newsapi_key,
#             "pageSize": num_results,
#             "language": "fr"  # Option pour les articles en français, à ajuster selon vos besoins
#         }
#
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#
#         if data.get("status") == "ok" and "articles" in data:
#             articles = []
#
#             for article in data["articles"][:num_results]:
#                 articles.append({
#                     "title": article.get("title", "Article sans titre"),
#                     "url": article.get("url", "#"),
#                     "summary": article.get("description", "Pas de description disponible."),
#                     "date": article.get("publishedAt", "")[:10]  # Format YYYY-MM-DD
#                 })
#
#             return articles
#         else:
#             st.warning(f"NewsAPI n'a pas retourné d'articles. Génération d'articles simulés.")
#             return simulate_search_with_openai(query, max_age_hours, num_results)
#
#     except Exception as e:
#         st.warning(f"Erreur lors de l'appel à NewsAPI: {e}. Génération d'articles simulés.")
#         return simulate_search_with_openai(query, max_age_hours, num_results)
#
# def search_with_bing(query: str, max_age_hours: int, num_results: int, api_key: str) -> List[Dict[str, str]]:
#     """
#     Recherche d'articles avec l'API Bing Search.
#     """
#     # Calcul de la date minimale
#     min_date = (datetime.now() - timedelta(hours=max_age_hours)).strftime("%Y-%m-%d")
#
#     endpoint = "https://api.bing.microsoft.com/v7.0/search"
#     headers = {"Ocp-Apim-Subscription-Key": api_key}
#     params = {
#         "q": query,
#         "count": num_results * 2,  # On demande plus pour filtrer après
#         "responseFilter": "News",
#         "freshness": f"Last{max_age_hours//24+1}Days"  # Approximation
#     }
#
#     response = requests.get(endpoint, headers=headers, params=params)
#     response.raise_for_status()
#
#     results = response.json().get('value', [])
#
#     articles = []
#     for result in results:
#         pub_date = result.get('datePublished', '').split('T')[0]
#
#         # Vérifier que l'article est assez récent
#         if pub_date >= min_date:
#             articles.append({
#                 "title": result.get('name', 'Article sans titre'),
#                 "url": result.get('url', '#'),
#                 "summary": result.get('description', 'Pas de description disponible.'),
#                 "date": pub_date
#             })
#
#     return articles[:num_results]
#
# def search_with_serpapi(query: str, max_age_hours: int, num_results: int, api_key: str) -> List[Dict[str, str]]:
#     """
#     Recherche d'articles avec SerpAPI.
#     """
#     endpoint = "https://serpapi.com/search.json"
#     params = {
#         "q": query,
#         "api_key": api_key,
#         "engine": "google",
#         "tbm": "nws",  # News search
#         "num": num_results * 2  # On demande plus pour filtrer après
#     }
#
#     response = requests.get(endpoint, params=params)
#     response.raise_for_status()
#
#     news_results = response.json().get('news_results', [])
#
#     articles = []
#     min_date = datetime.now() - timedelta(hours=max_age_hours)
#
#     for result in news_results:
#         # SerpAPI ne donne pas toujours de date précise, on utilise celle qu'on a
#         pub_date_str = result.get('date', '')
#
#         # Si on a une date complète au format ISO
#         if 'T' in pub_date_str:
#             try:
#                 pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
#                 if pub_date < min_date:
#                     continue
#             except:
#                 # Si on ne peut pas parser, on garde l'article
#                 pass
#
#         articles.append({
#             "title": result.get('title', 'Article sans titre'),
#             "url": result.get('link', '#'),
#             "summary": result.get('snippet', 'Pas de description disponible.'),
#             "date": pub_date_str if pub_date_str else datetime.now().strftime('%Y-%m-%d')
#         })
#
#     return articles[:num_results]
#
# def simulate_search_with_openai(query: str, max_age_hours: int, num_results: int) -> List[Dict[str, str]]:
#     """
#     Utilise OpenAI pour simuler une recherche d'articles récents.
#     Utile quand aucune API de recherche web n'est disponible.
#     """
#     prompt = f"""
#     Génère {num_results} articles fictifs récents (moins de {max_age_hours} heures) sur le sujet suivant: {query}.
#
#     Ces articles doivent sembler réels et publiés sur de vrais sites d'information.
#     Pour chaque article, fournir:
#     1. Un titre réaliste et accrocheur
#     2. Une URL fictive mais plausible (domaine réel)
#     3. Un résumé informatif de 3-5
#     4. Une date de publication dans les dernières {max_age_hours} heures
#
#     Format JSON attendu:
#     [
#         {{
#             "title": "Titre de l'article 1",
#             "url": "https://example.com/article1",
#             "summary": "Résumé de l'article en 3-5 lignes",
#             "date": "YYYY-MM-DD"
#         }},
#         ...
#     ]
#     """
#
#     response = call_openai_api(prompt, max_tokens=1500)
#
#     try:
#         articles_text = response["choices"][0]["message"]["content"]
#         # On extrait le JSON des potentiels backticks markdown
#         if "```json" in articles_text:
#             articles_text = articles_text.split("```json")[1].split("```")[0].strip()
#         elif "```" in articles_text:
#             articles_text = articles_text.split("```")[1].split("```")[0].strip()
#
#         articles = json.loads(articles_text)
#         return articles
#     except Exception as e:
#         st.error(f"Erreur lors du parsing des articles simulés: {e}")
#         # En cas d'erreur, on retourne au moins quelques articles fictifs basiques
#         return [
#             {
#                 "title": f"Article récent sur {query} - Partie {i+1}",
#                 "url": f"https://example.com/article-{i+1}",
#                 "summary": f"Cet article traite de {query} et présente des informations récentes sur le sujet.",
#                 "date": datetime.now().strftime('%Y-%m-%d')
#             } for i in range(num_results)
#         ]
#
# # Services de génération de contenu
# def generate_topic_ideas(sector: str, keywords: str, services: str) -> List[str]:
#     """
#     Génère 5 idées de sujets d'articles basés sur les inputs utilisateur.
#     """
#     prompt = f"""
#     En tant qu'expert en marketing de contenu, propose 5 idées de sujets d'articles pour le secteur "{sector}"
#     avec les mots-clés "{keywords}" et les services/produits "{services}".
#
#     Pour chaque idée, fournir:
#     - Un titre accrocheur et SEO-friendly
#     - Une brève description du sujet (1-2 phrases)
#
#     Présente les résultats sous forme de liste numérotée.
#     """
#
#     response = call_openai_api(prompt)
#     ideas_text = response["choices"][0]["message"]["content"]
#
#     # Traitement basique pour extraire les idées
#     ideas = []
#     for line in ideas_text.split("\n"):
#         line = line.strip()
#         if line and (line[0].isdigit() or line.startswith("-")):
#             # Nettoyer la ligne (retirer le numéro/tiret initial)
#             clean_line = line.split(".", 1)[-1].strip() if "." in line else line.strip()
#             clean_line = clean_line[1:].strip() if clean_line.startswith("-") else clean_line
#
#             # Extraire juste le titre si disponible
#             if ":" in clean_line:
#                 title = clean_line.split(":", 1)[0].strip()
#                 ideas.append(title)
#             else:
#                 ideas.append(clean_line)
#
#     # Garantir qu'on a au moins 5 idées
#     if len(ideas) < 5:
#         additional_ideas = ["Sujet " + str(i+1) for i in range(len(ideas), 5)]
#         ideas.extend(additional_ideas)
#
#     return ideas[:5]  # Limiter à 5 idées
#
# def generate_editorial_angles(topic: str, sector: str) -> List[str]:
#     """
#     Génère 5 angles éditoriaux différents pour un sujet donné.
#     """
#     prompt = f"""
#     Pour le sujet d'article "{topic}" dans le secteur "{sector}", propose 5 angles éditoriaux différents.
#     Chaque angle doit être distinct et apporter une perspective unique.
#
#     Exemples d'angles: analytique, émotionnel, didactique, anecdotique, comparatif, etc.
#
#     Pour chaque angle, fournir:
#     - Un nom court et descriptif
#     - Une brève explication de l'approche (1-2 phrases)
#
#     Présente les résultats sous forme de liste numérotée.
#     """
#
#     response = call_openai_api(prompt)
#     angles_text = response["choices"][0]["message"]["content"]
#
#     # Traitement pour extraire les angles
#     angles = []
#     current_angle = ""
#
#     for line in angles_text.split("\n"):
#         line = line.strip()
#         if line and (line[0].isdigit() or line.startswith("-")):
#             # Nouvelle entrée détectée
#             if current_angle and len(current_angle) > 0:
#                 angles.append(current_angle)
#
#             # Nettoyer la ligne
#             clean_line = line.split(".", 1)[-1].strip() if "." in line else line.strip()
#             clean_line = clean_line[1:].strip() if clean_line.startswith("-") else clean_line
#
#             # Extraire juste le nom de l'angle si disponible
#             if ":" in clean_line:
#                 angle_name = clean_line.split(":", 1)[0].strip()
#                 current_angle = angle_name
#             else:
#                 current_angle = clean_line
#         elif line and current_angle:
#             # Ligne supplémentaire pour l'entrée actuelle
#             continue
#
#     # Ajouter le dernier angle s'il existe
#     if current_angle and len(current_angle) > 0:
#         angles.append(current_angle)
#
#     # Garantir qu'on a au moins 5 angles
#     if len(angles) < 5:
#         additional_angles = ["Angle " + str(i+1) for i in range(len(angles), 5)]
#         angles.extend(additional_angles)
#
#     return angles[:5]  # Limiter à 5 angles
#
# def generate_article_outline(topic: str, angle: str, tone: str, length: str, style: str) -> Dict[str, Any]:
#     """
#     Génère un plan d'article structuré.
#     """
#     prompt = f"""
#     Crée un plan détaillé pour un article sur le sujet:
#     "{topic}"
#
#     Avec l'angle éditorial:
#     "{angle}"
#
#     Paramètres de rédaction:
#     - Ton: {tone}
#     - Longueur: {length}
#     - Style: {style}
#
#     Le plan doit inclure:
#     1. Un titre accrocheur
#     2. Une introduction
#     3. 2-4 parties principales avec sous-points
#     4. Une conclusion
#
#     Format JSON attendu:
#     {{
#         "title": "Titre de l'article",
#         "introduction": "Description de l'introduction",
#         "sections": [
#             {{
#                 "title": "Titre section 1",
#                 "subsections": ["Sous-point 1", "Sous-point 2"]
#             }},
#             ...
#         ],
#         "conclusion": "Description de la conclusion"
#     }}
#     """
#
#     response = call_openai_api(prompt, max_tokens=1200)
#     outline_text = response["choices"][0]["message"]["content"]
#
#     # Extraction du JSON du texte
#     try:
#         if "```json" in outline_text:
#             outline_json = outline_text.split("```json")[1].split("```")[0].strip()
#         elif "```" in outline_text:
#             outline_json = outline_text.split("```")[1].split("```")[0].strip()
#         else:
#             outline_json = outline_text.strip()
#
#         outline = json.loads(outline_json)
#         return outline
#     except Exception as e:
#         st.error(f"Erreur lors du parsing du plan: {e}")
#         st.error(f"Texte reçu: {outline_text}")
#
#         # Fournir un plan par défaut en cas d'erreur
#         return {
#             "title": f"Article sur {topic}",
#             "introduction": "Introduction à définir",
#             "sections": [
#                 {"title": "Première partie", "subsections": ["Point 1", "Point 2"]},
#                 {"title": "Deuxième partie", "subsections": ["Point 1", "Point 2"]},
#             ],
#             "conclusion": "Conclusion à définir"
#         }
#
# def generate_article(outline: Dict[str, Any], topic: str, angle: str, tone: str, length: str, style: str) -> str:
#     """
#     Génère l'article complet basé sur le plan et les paramètres.
#     """
#     # Déterminer la longueur approximative en mots
#     word_count = {
#         "Court (~300 mots)": 300,
#         "Moyen (~600 mots)": 600,
#         "Long (~1200 mots)": 1200
#     }.get(length, 600)
#
#     # Création du plan formaté pour le prompt
#     outline_formatted = f"""
#     Titre: {outline['title']}
#
#     Introduction: {outline['introduction']}
#
#     """
#
#     for i, section in enumerate(outline['sections']):
#         outline_formatted += f"Section {i+1}: {section['title']}\n"
#         for j, subsection in enumerate(section['subsections']):
#             outline_formatted += f"- {subsection}\n"
#         outline_formatted += "\n"
#
#     outline_formatted += f"Conclusion: {outline['conclusion']}"
#
#     prompt = f"""
#     Rédige un article complet et professionnel sur le sujet "{topic}" avec l'angle "{angle}"
#     en suivant précisément le plan ci-dessous:
#
#     {outline_formatted}
#
#     Paramètres de rédaction:
#     - Ton: {tone}
#     - Longueur cible: environ {word_count} mots
#     - Style: {style}
#
#     L'article doit être cohérent, engageant, et respecter les meilleures pratiques SEO sans compromettre la qualité éditoriale.
#     Utilise des paragraphes clairs, des sous-titres pertinents, et une structure logique.
#
#     Format: Markdown
#     """
#
#     # Déterminer le nombre de tokens nécessaires (environ 1.5 tokens par mot)
#     needed_tokens = int(word_count * 1.5)
#
#     # Pour les articles longs, utiliser un modèle plus puissant
#     model = "gpt-4o" if word_count > 800 else "gpt-4o-mini"
#
#     response = call_openai_api(prompt, model=model, max_tokens=needed_tokens)
#     article_text = response["choices"][0]["message"]["content"]
#
#     return article_text