import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import os

# Fonction pour charger les mots-clés à partir d'un fichier
def load_keywords(filename):
    if not os.path.exists(filename):
        st.error(f"Le fichier '{filename}' est introuvable. Veuillez vérifier le chemin.")
        return []
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Fonction pour récupérer le SERP de Google pour un mot-clé donné
def get_serp(keyword, country_code, language_code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    # URL personnalisée pour le pays et la langue sélectionnés
    url = f"https://www.google.{country_code}/search?q={keyword}&hl={language_code}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('a')
        serp_urls = [result['href'] for result in results if 'url?q=' in result['href']]
        return [url.split('&')[0].replace('/url?q=', '') for url in serp_urls]
    else:
        st.warning(f"Erreur de récupération pour le mot-clé {keyword}. Code de statut : {response.status_code}")
        return []

# Fonction principale de l'application
def main():
    st.title("Analyse de Similarité des SERP")

    # Charger les mots-clés depuis le fichier
    keyword_file = "motscles.txt"
    keywords = load_keywords(keyword_file)
    
    if not keywords:
        st.warning("Le fichier de mots-clés est vide ou introuvable.")
        return

    # Sélection de la langue et du pays pour l'analyse
    st.subheader("Paramètres d'analyse")
    languages = ["fr", "en", "de", "es", "nl", "it", "pl", "pt"]
    countries = ["fr", "gb", "us", "ca", "ma", "sn", "tn", "ie", "sg", "es", "nl", "it", "pl", "pt", "in", "vn", "id", "my", "pk", "th", "hk", "ph", "jp", "bd", "tw", "lk", "kh", "bn", "fj", "kr", "la", "mo", "np", "ws", "tl", "au", "nz"]
    language_code = st.selectbox("Choisissez la langue", languages)
    country_code = st.selectbox("Choisissez le pays", countries)

    # Choisir deux mots-clés pour la comparaison
    keyword1 = st.selectbox("Sélectionnez le premier mot-clé", keywords)
    keyword2 = st.selectbox("Sélectionnez le second mot-clé", keywords)

    if st.button("Lancer l'analyse"):
        st.subheader("Résultats de l'analyse de similarité")
        
        # Récupérer les SERPs pour les deux mots-clés
        serp1 = get_serp(keyword1, country_code, language_code)
        serp2 = get_serp(keyword2, country_code, language_code)
        
        if serp1 and serp2:
            # Calculer la similarité entre les deux SERPs
            common_urls = set(serp1) & set(serp2)
            similarity_score = len(common_urls) / min(len(serp1), len(serp2)) * 100

            # Afficher les résultats
            st.write(f"Score de similarité entre '{keyword1}' et '{keyword2}': {similarity_score:.2f}%")
            st.write("URLs communes :")
            for url in common_urls:
                st.write(url)
        else:
            st.warning("Impossible de récupérer les SERPs pour l'un des mots-clés.")

if __name__ == "__main__":
    main()
