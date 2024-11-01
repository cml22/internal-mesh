import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# Fonction pour effectuer une recherche Google
def google_search(keyword, site, lang, country):
    query = f"{keyword} site:{site}"
    url = f"https://www.google.{country}/search?q={query}&hl={lang}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    
    try:
        # Faire une requête HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Vérifie si la requête a échoué

        soup = BeautifulSoup(response.text, "html.parser")
        opportunities = []
        serp_results = []

        # Recherche tous les résultats de liens
        for result in soup.find_all('a'):
            href = result.get('href')
            if href and "url?q=" in href:
                # Extraire l'URL
                result_url = href.split("url?q=")[1].split("&")[0]
                serp_results.append(result_url)  # Ajoute à la liste des résultats de SERP
                opportunities.append(result_url)

        return opportunities, serp_results
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur HTTP : {e}")
        return [], []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des résultats : {e}")
        return [], []

# Fonction pour analyser les opportunités trouvées
def analyze_opportunities(opportunities, keywords):
    analysis_results = []
    for url in opportunities:
        for keyword in keywords:
            # Vérifie si le mot-clé est présent dans l'URL
            if keyword.lower() in url.lower():
                # Ici, on pourrait ajouter une vérification pour déterminer si l'ancre est optimisée
                action = "Optimiser l'ancre" if "optimized" in url else "Ajouter un lien"
                analysis_results.append({
                    'url': url,
                    'keyword': keyword,
                    'action': action
                })
                break  # Pas besoin de vérifier d'autres mots-clés si un match a été trouvé
    return analysis_results

# Configuration de l'application Streamlit
st.title("Analyse des Opportunités de Maillage Interne")
st.write("Indiquez vos mots-clés, un par ligne.")

# Champs d'entrée pour les mots-clés, le site, la langue et le pays
keywords_input = st.text_area("Mots-clés (un par ligne) :")
site = st.text_input("Site à analyser :")
lang = st.selectbox("Langue :", ["fr", "en", "es", "de", "it", "nl", "pl", "pt", "ru", "ja"])
country = st.selectbox("Pays :", ["fr", "us", "de", "es", "it", "nl", "pl", "pt", "ru", "jp"])

# Bouton pour lancer l'analyse
if st.button("Analyser"):
    if keywords_input and site:
        keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]  # Sépare les mots-clés par ligne et enlève les espaces

        # Recherche et analyse
        opportunities = []
        all_serp_results = []
        for keyword in keywords:
            st.write(f"Recherche pour le mot-clé : {keyword}")
            opportun, serp_results = google_search(keyword, site, lang, country)
            opportunities += opportun
            all_serp_results += serp_results
            time.sleep(2)  # Attente pour éviter d'être bloqué par Google

        # Affichage des résultats
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

        # Vérification des SERP
        st.write("### Résultats de la recherche :")
        for serp_url in all_serp_results:
            st.write(f"**URL trouvée :** {serp_url}")

    else:
        st.error("Veuillez entrer des mots-clés et un site.")
