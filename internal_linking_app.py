import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(page_title="Opportunité de Maillage", layout="centered")

# But de l'outil
st.write("## Opportunité de Maillage")
st.write("Cet outil vérifie si des domaines spécifiques apparaissent dans les résultats de recherche pour un ou plusieurs mots-clés.")

# Backlink vers le site de Charles Migaud
st.markdown('Outil réalisé avec ❤️ par [Charles Migaud](https://charles-migaud.fr)')

def scrape_serp(keyword, language, country, num_results):
    query = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={query}&hl={language}&gl={country}&num={num_results}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, KHTML, Gecko) Chrome/116.0.5845.96 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error("Erreur lors de la récupération des résultats.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='g')[:num_results]:
        link = g.find('a', href=True)
        if link:
            title = g.find('h3').get_text() if g.find('h3') else "Titre non trouvé"
            results.append((link['href'], title))

    return results

def analyze_opportunities(results, domains):
    opportunities = []
    for url, title in results:
        domain = urllib.parse.urlparse(url).netloc
        if domain in domains:
            opportunities.append((domain, title, url))
    return opportunities

# Interface utilisateur avec Streamlit
st.title("Vérification d'Opportunités de Maillage")
st.markdown("---")

# Champ d'entrée pour le mot-clé
keyword = st.text_input("Entrez le mot-clé:", placeholder="Ex: hébergement web")
language = st.selectbox("Langue:", ["fr", "en", "es", "de", "it", "pt", "pl"])
country = st.selectbox("Pays:", ["FR", "GB", "US", "CA", "ES", "DE", "IT", "PT", "PL", "MA", "SN", "TN"])

# Champ d'entrée pour les domaines
domains_input = st.text_area("Entrez les domaines à vérifier (un par ligne):", placeholder="Ex: ovhcloud.com\nexample.com")
domains = [domain.strip() for domain in domains_input.splitlines() if domain.strip()]

# Slider pour choisir le nombre d'URLs à scraper
num_urls = st.slider("Sélectionnez le nombre d'URLs à scraper (entre 10 et 100):", min_value=10, max_value=100, value=10, step=10)

st.markdown("---")

if st.button("Vérifier les opportunités"):
    if keyword and domains:
        # Scraper les résultats pour le mot-clé
        results = scrape_serp(keyword, language, country, num_urls)

        # Analyser les opportunités de maillage
        opportunities = analyze_opportunities(results, domains)

        # Afficher les résultats
        if opportunities:
            st.success("Des opportunités de maillage ont été trouvées !")
            for domain, title, url in opportunities:
                st.markdown(f"- **{domain}**: [{title}]({url})")
        else:
            st.warning("Aucune opportunité trouvée.")

        st.markdown("---")
        st.subheader("Résultats SERP")

        # Afficher les résultats de recherche
        for rank, (url, title) in enumerate(results, start=1):
            st.markdown(f"{rank}. [{title}]({url})")

    else:
        st.error("Veuillez entrer un mot-clé et au moins un domaine.")
