import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Configuration ---
keyword_file = 'mots_cles.txt'  # Chemin vers le fichier de mots-clés
output_file = 'opportunites_maillage.csv'  # Nom du fichier de sortie
base_url = "https://www.google.com/search"  # URL de recherche Google
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fonction pour charger les mots-clés depuis un fichier texte
def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

# Fonction pour effectuer une recherche Google et récupérer les résultats pour un mot-clé spécifique
def google_search(query, site=None, lang='fr', country='FR'):
    params = {
        "q": f"{query} site:{site}" if site else query,
        "num": 10,
        "hl": lang,  # Langue
        "gl": country  # Pays
    }
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Erreur lors de la recherche pour le mot-clé '{query}': Statut {response.status_code}")
        return None

# Fonction pour vérifier si un mot-clé est présent dans les ancres des liens de la page
def check_anchor(keyword, page_url):
    try:
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return any(keyword.lower() in a.get_text(strip=True).lower() for a in soup.find_all('a'))
        else:
            print(f"Erreur d'accès à l'URL {page_url}: Statut {response.status_code}")
            return False
    except Exception as e:
        print(f"Erreur lors de la vérification de l'ancre pour l'URL {page_url}: {e}")
        return False

# Fonction principale pour trouver des opportunités de maillage interne
def find_linking_opportunities(keywords, site, lang, country):
    opportunities = []
    for keyword in keywords:
        print(f"Traitement du mot-clé : {keyword}")
        search_results = google_search(keyword, site, lang, country)
        if search_results:
            soup = BeautifulSoup(search_results, 'html.parser')
            for result in soup.find_all('a'):
                result_url = result.get('href')
                if "url?q=" in result_url:
                    result_url = result_url.split("url?q=")[1].split("&")[0]
                    anchor_match = check_anchor(keyword, result_url)
                    if anchor_match:
                        action = "Optimiser l'ancre"
                    else:
                        action = "Ajouter un lien"
                    opportunities.append({"Mot-clé": keyword, "URL": result_url, "Action": action})
    return pd.DataFrame(opportunities)

# Interface utilisateur Streamlit
st.title("Opportunités de Maillage Interne")

# Saisie du site
site = st.text_input("Entrez le site à analyser (par exemple, exemple.com) :")

# Choix de la langue
lang = st.selectbox("Choisissez la langue :", ["fr", "en", "es", "de"])  # Ajoutez d'autres langues si nécessaire

# Choix du pays
country = st.selectbox("Choisissez le pays :", ["FR", "US", "ES", "DE"])  # Ajoutez d'autres pays si nécessaire

# Chargement des mots-clés
keywords = load_keywords(keyword_file)

# Bouton pour lancer la recherche
if st.button("Trouver des opportunités de maillage"):
    if not site:
        st.warning("Veuillez entrer un site à analyser.")
    else:
        # Recherche des opportunités de maillage interne
        df_opportunities = find_linking_opportunities(keywords, site, lang, country)

        # Exportation des résultats dans un fichier CSV
        df_opportunities.to_csv(output_file, index=False)

        # Affichage des résultats
        st.write("Voici les opportunités de maillage détectées :")
        st.write(df_opportunities)
