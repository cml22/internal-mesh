import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Configuration --- 
url = "https://www.google.fr/search"  # URL de recherche Google pour votre locale
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fonction pour charger les mots-clés depuis un fichier texte
def load_keywords(file):
    return [line.strip() for line in file.readlines()]

# Fonction pour effectuer une recherche Google et récupérer les résultats pour un mot-clé spécifique
def google_search(query, site=None):
    params = {"q": f"{query} site:{site}" if site else query, "num": 10}  # Recherche les 10 premiers résultats
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Erreur lors de la recherche pour le mot-clé '{query}': Statut {response.status_code}")
        return None

# Fonction pour vérifier si un mot-clé est présent dans les ancres des liens de la page
def check_anchor(keyword, page_url):
    try:
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return any(keyword.lower() in a.get_text(strip=True).lower() for a in soup.find_all('a'))
        else:
            st.error(f"Erreur d'accès à l'URL {page_url}: Statut {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Erreur lors de la vérification de l'ancre pour l'URL {page_url}: {e}")
        return False

# Fonction principale pour trouver des opportunités de maillage interne
def find_linking_opportunities(keywords, site):
    opportunities = []
    for keyword in keywords:
        st.write(f"Traitement du mot-clé : {keyword}")
        search_results = google_search(keyword, site)
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
        time.sleep(2)  # Délai pour éviter de surcharger Google
    return pd.DataFrame(opportunities)

# Interface Streamlit
st.title("Opportunités de Maillage Interne")
st.write("Téléchargez votre fichier de mots-clés (.txt)")

# Champ de téléchargement de fichier
uploaded_file = st.file_uploader("Drag and drop file here", type='txt')

# Champ de saisie pour le site
site = st.text_input("Entrez l'URL de votre site (sans https://) :")

# Sélecteur de langue
langue = st.selectbox("Choisissez la langue :", ["fr", "en", "es", "de"])

# Sélecteur de pays
pays = st.selectbox("Choisissez le pays :", ["fr", "us", "es", "de"])

if uploaded_file and site:
    keywords = load_keywords(uploaded_file)
    df_opportunities = find_linking_opportunities(keywords, site)
    if not df_opportunities.empty:
        st.write("Voici les opportunités de maillage détectées :")
        st.write(df_opportunities)
        output_file = 'opportunites_maillage.csv'
        df_opportunities.to_csv(output_file, index=False)
        st.success(f"Les résultats ont été exportés dans '{output_file}'.")
    else:
        st.write("Aucune opportunité de maillage détectée.")
else:
    st.warning("Veuillez télécharger un fichier de mots-clés et entrer l'URL de votre site avant de continuer.")
