# Guide d'utilisation - Générateur d'articles IA

Ce guide détaille l'utilisation de l'Assistant de génération d'articles IA personnalisé.

## 1. Démarrage rapide

Pour générer un article rapidement :

1. **Installez** l'application avec Pipenv : `pipenv install`
2. **Configurez** votre clé API OpenAI dans un fichier `.env`
3. **Lancez** l'application : `pipenv run app`
4. **Suivez** le workflow étape par étape dans l'interface

## 2. Workflow détaillé

### Étape 1 : Données initiales

Renseignez les informations de base pour votre article :
- **Secteur d'activité** : domaine principal (ex : "technologie", "santé", "immobilier")
- **Mots-clés** : termes principaux séparés par des virgules
- **Services/Produits** : offres spécifiques liées au sujet

Ces informations serviront de base pour générer des idées de sujets pertinentes.

### Étape 2 : Choix du sujet

L'IA vous propose 5 idées de sujets basées sur vos données initiales. Vous pouvez :
- Sélectionner une des idées générées
- Proposer votre propre sujet personnalisé

### Étape 3 : Articles inspirants

L'application recherche et affiche 5 articles récents liés à votre sujet pour vous inspirer. Ces articles comprennent :
- Un titre accrocheur
- Un lien vers la source (simulé en mode démo)
- Un résumé de 3-5 lignes
- Une date de publication (moins de 72h)

### Étape 4 : Angles éditoriaux

Choisissez parmi 5 angles éditoriaux proposés pour aborder votre sujet. Chaque angle offre une perspective unique, par exemple :
- Point de vue expert
- Approche didactique
- Perspective émotionnelle
- Analyse comparative
- Vision prospective

### Étape 5 : Paramètres de rédaction

Personnalisez votre article selon vos préférences :
- **Ton** : professionnel, dynamique, bienveillant, humoristique...
- **Longueur** : court (~300 mots), moyen (~600 mots), long (~1200 mots)
- **Style** : blog, article LinkedIn, post inspirant, tutoriel...

### Étape 6 : Plan de l'article

L'IA génère un plan structuré comprenant :
- Un titre accrocheur
- Une introduction
- 2 à 4 parties principales avec sous-points
- Une conclusion

Vous pouvez valider ce plan ou demander une nouvelle proposition.

### Étape 7 : Article final

L'article complet est généré selon vos paramètres. Vous pouvez :
- Lire l'article directement dans l'interface
- Copier le texte dans le presse-papier
- Télécharger l'article en format Markdown
- Regénérer l'article si nécessaire

## 3. Astuces pour de meilleurs résultats

- **Soyez précis** dans vos mots-clés pour obtenir des suggestions plus pertinentes
- **Variez les angles** pour trouver la perspective la plus intéressante
- **Ajustez la longueur** selon votre canal de diffusion (les articles LinkedIn performent mieux avec ~600 mots)
- Pour un **contenu SEO**, optez pour le ton "Informatif" et le style "Blog"
- Les articles à **angle émotionnel** fonctionnent mieux avec un ton "Bienveillant" ou "Dynamique"
- Pour des **tutoriels**, privilégiez un style "Didactique" et une longueur "Long"

## 4. Résolution des problèmes courants

| Problème | Solution |
|----------|----------|
| Message d'erreur API | Vérifiez que votre clé API OpenAI est correctement configurée dans le fichier `.env` |
| Lenteur de génération | Les articles longs utilisent GPT-4o et peuvent prendre plus de temps |
| Pas d'articles récents | Sans API de recherche, l'application simule des résultats avec GPT |
| Plan inadapté | Utilisez le bouton "Regénérer le plan" pour obtenir une nouvelle proposition |
| Contenu trop générique | Enrichissez vos mots-clés et soyez plus spécifique dans votre description de secteur |

## 5. Protection des données

Les données que vous saisissez sont envoyées à l'API OpenAI pour générer le contenu. Si vous travaillez avec des informations sensibles :
- Évitez les données confidentielles
- Vérifiez les articles générés avant de les publier
- Modifiez manuellement les passages contenant des informations inexactes

---

Pour toute question ou assistance technique supplémentaire, consultez le fichier README.md ou contactez l'équipe de développement.