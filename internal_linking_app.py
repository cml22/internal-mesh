import streamlit as st
import requests
from bs4 import BeautifulSoup

# Fonction pour effectuer une recherche Google
def google_search(keyword, site, lang, country):
    query = f"{keyword} site:{site}"
    url = f"https://www.google.{country}/search?q={query}&hl={lang}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        opportunities = []

        # Recherche tous les résultats de liens
        for result in soup.select('a'):
            result_url = result.get('href')
            if result_url and "url?q=" in result_url:
                result_url = result_url.split("url?q=")[1].split("&")[0]
                opportunities.append(result_url)

        return opportunities
    else:
        st.error("Erreur lors de la récupération des résultats.")
        return []

# Fonction pour analyser les opportunités trouvées
def analyze_opportunities(opportunities, keywords):
    analysis_results = []
    for url in opportunities:
        for keyword in keywords:
            if keyword.lower() in url.lower():  # Vérifie si le mot-clé est présent dans l'URL
                analysis_results.append({
                    'url': url,
                    'keyword': keyword,
                    'action': "Ajouter un lien" if "optimized" not in url else "Optimiser l'ancre"
                })
                break  # Pas besoin de vérifier d'autres mots-clés si un match a été trouvé
    return analysis_results

# Configuration de l'application Streamlit
st.title("Analyse des Opportunités de Maillage Interne")
st.write("Indiquez vos mots-clés en ligne, séparés par des virgules.")

# Champs d'entrée pour les mots-clés, le site, la langue et le pays
keywords_input = st.text_area("Mots-clés (séparés par des virgules) :")
site = st.text_input("Site à analyser :")
lang = st.selectbox("Langue :", ["fr", "en", "es", "de", "it", "nl", "pl", "pt", "ru", "ja"])
country = st.selectbox("Pays :", ["fr", "us", "de", "es", "it", "nl", "pl", "pt", "ru", "jp"])

# Bouton pour lancer l'analyse
if st.button("Analyser"):
    if keywords_input and site:
        keywords = [kw.strip() for kw in keywords_input.split(",")]

        # Recherche et analyse
        opportunities = []
        for keyword in keywords:
            st.write(f"Recherche pour le mot-clé : {keyword}")
            opportunities += google_search(keyword, site, lang, country)

        if opportunities:
            analysis_results = analyze_opportunities(opportunities, keywords)
            if analysis_results:
                st.write("### Opportunités de maillage interne trouvées :")
                for result in analysis_results:
                    st.write(f"**URL :** {result['url']} - **Mot-clé :** {result['keyword']} - **Action :** {result['action']}")
            else:
                st.write("Aucune opportunité trouvée.")
        else:
            st.write("Aucune opportunité trouvée.")
    else:
        st.error("Veuillez entrer des mots-clés et un site.")
