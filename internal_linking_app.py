import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

def google_search(keyword, site, lang, country):
    # Forme la requête Google avec les paramètres de langue et pays
    query = f"{keyword} site:{site}"
    url = f"https://www.google.{country}/search?q={query}&hl={lang}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        opportunities = []

        for result in soup.find_all('a'):
            result_url = result.get('href')
            if result_url and "url?q=" in result_url:
                result_url = result_url.split("url?q=")[1].split("&")[0]
                opportunities.append(result_url)

        return opportunities
    else:
        st.error("Erreur lors de la récupération des résultats.")
        return []

def analyze_opportunities(opportunities, keywords):
    # Simule une analyse des opportunités de maillage
    analysis_results = []
    for url in opportunities:
        for keyword in keywords:
            # Simule une condition pour l'exemple
            if keyword.lower() in url.lower():
                analysis_results.append({
                    'url': url,
                    'keyword': keyword,
                    'action': "Ajouter un lien" if "optimized" not in url else "Optimiser l'ancre"
                })
    return analysis_results

def find_linking_opportunities(keywords, site, lang, country):
    opportunities = []
    for keyword in keywords:
        st.write(f"Recherche pour le mot-clé : {keyword}")
        result_urls = google_search(keyword, site, lang, country)
        opportunities.extend(result_urls)
        time.sleep(2)  # Pause pour éviter de surcharger le serveur de Google

    # Analyse des opportunités de maillage
    return analyze_opportunities(opportunities, keywords)

# Titre de l'application
st.title("Opportunités de Maillage Interne")

# Champ de saisie pour les mots-clés
keywords_input = st.text_area("Entrez vos mots-clés (un par ligne) :", height=200)
keywords = keywords_input.splitlines() if keywords_input else []

# Champ pour le site
site = st.text_input("Entrez l'URL de votre site :", "ovhcloud.com")

# Sélection de la langue et du pays
lang = st.selectbox("Choisissez la langue :", ["fr", "en", "es", "de", "it", "pl", "nl"])
country = st.selectbox("Choisissez le pays :", ["com", "fr", "uk", "de", "es", "it", "pl", "nl"])

# Bouton pour lancer la recherche
if st.button("Trouver des opportunités de maillage interne"):
    if keywords:
        results = find_linking_opportunities(keywords, site, lang, country)
        if results:
            st.write("Opportunités de maillage interne trouvées :")
            for result in results:
                st.write(f"**URL :** {result['url']} | **Mot-clé :** {result['keyword']} | **Action :** {result['action']}")
        else:
            st.write("Aucune opportunité trouvée.")
    else:
        st.warning("Veuillez entrer au moins un mot-clé avant de continuer.")
