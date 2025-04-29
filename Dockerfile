FROM python:3.10-slim

WORKDIR /app

# Installer pipenv
RUN pip install --no-cache-dir pipenv

# Copier les fichiers Pipenv
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
# --system permet d'installer les paquets globalement et non dans un environnement virtuel
RUN pipenv install --deploy --system

# Copier le reste du code
COPY . .

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande d'entrée
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]