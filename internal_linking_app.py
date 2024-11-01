import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

def google_search(keyword, site):
    query = f"{keyword} site:{site}"
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"}
    response = requests.get(url, headers=headers)
    
    # Affiche le contenu brut des résultats pour le débogage
    st.write("Résultats bruts de la recherche Google :", response.text)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        opportunities = []
        
        # Cherche les liens dans les résultats
        for result in soup.find_all('a'):
            result_url = result.get('href')
            if result_url:
                if "url?q=" in result_url:
                    # Extraction de l'URL
                    result_url = result_url.split("url?q=")[1].split("&")[0]
                    opportunities.append(result_url)
                else:
                    st.write(f"URL ignorée : {result_url}")  # Affiche les URLs qui ne correspondent pas

        return opportunities
    else:
        st.error("Erreur lors de la récupération des résultats.")
        return []

def find_linking_opportunities(keywords, site):
    opportunities = []
    for keyword in keywords:
        st.write(f"Traitement du mot-clé : {keyword}")
        result_urls = google_search(keyword, site)
        opportunities.extend(result_urls)
        time.sleep(2)  # Pause pour éviter de surcharger le serveur de Google

    return opportunities

# Titre de l'application
st.title("Opportunités de Maillage Interne")

# Champ de saisie pour les mots-clés
keywords_input = st.text_area("Entrez vos mots-clés (un par ligne) :", height=200)
keywords = keywords_input.splitlines() if keywords_input else []

# Champ pour le site
site = st.text_input("Entrez l'URL de votre site :", "ovhcloud.com")

# Bouton pour lancer la recherche
if st.button("Trouver des opportunités de maillage interne"):
    if keywords:
        results = find_linking_opportunities(keywords, site)
        if results:
            st.write("Opportunités de maillage interne trouvées :")
            for url in results:
                st.write(url)
        else:
            st.write("Aucune opportunité trouvée.")
    else:
        st.warning("Veuillez entrer au moins un mot-clé avant de continuer.")
