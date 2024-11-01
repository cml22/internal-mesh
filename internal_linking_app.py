import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

# --- Configuration des paramètres (langue et pays) ---
keyword_file = 'motscles.txt'  # Chemin vers votre fichier de mots-clés
site = "webloom.fr"  # Votre site web (changez si besoin)
output_file = 'opportunites_maillage.csv'  # Fichier de sortie pour les opportunités

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                  "AppleWebKit/537.36 (KHTML, like Gecko) " +
                  "Chrome/91.0.4472.124 Safari/537.36"
}
delay_between_requests = 2  # Délai entre les requêtes pour éviter le blocage

# --- Options de langue et de pays selon les hreflangs ---
LOCALES = {
    "fr": ("google.fr", "fr"),
    "en-gb": ("google.co.uk", "en"),
    "en": ("google.com", "en"),
    "en-us": ("google.com", "en"),
    "fr-ca": ("google.ca", "fr"),
    "en-ca": ("google.ca", "en"),
    "fr-ma": ("google.co.ma", "fr"),
    "fr-sn": ("google.sn", "fr"),
    "fr-tn": ("google.com.tn", "fr"),
    "de": ("google.de", "de"),
    "en-ie": ("google.ie", "en"),
    "en-sg": ("google.com.sg", "en"),
    "es-es": ("google.es", "es"),
    "es": ("google.com", "es"),
    "nl": ("google.nl", "nl"),
    "it": ("google.it", "it"),
    "pl": ("google.pl", "pl"),
    "pt": ("google.pt", "pt"),
    "en-in": ("google.co.in", "en"),
    # Ajoutez d'autres entrées si nécessaire
}

# Sélection de la langue et du pays
language_country = st.selectbox("Choisir la langue et le pays", list(LOCALES.keys()))

# Fonction pour générer l'URL de Google en fonction de la langue et du pays
def generate_google_url(locale_code):
    google_domain, lang_code = LOCALES[locale_code]
    return f"https://www.{google_domain}/search?hl={lang_code}"

# Génération de l'URL de Google
url = generate_google_url(language_country)

# Fonction pour charger les mots-clés depuis un fichier
def load_keywords(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Fonction pour effectuer une recherche Google
def google_search(keyword, url):
    search_url = f"{url}&q={keyword}"
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Erreur lors de la recherche pour '{keyword}' : {response.status_code}")
        return None

# Fonction pour détecter les liens de maillage
def detect_maillage(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for link in soup.find_all('a', href=True):
        if site in link['href']:
            results.append((keyword, link['href']))
    return results

# Fonction principale
def main():
    st.title("Outil de détection de maillage SEO")
    keywords = load_keywords(keyword_file)
    all_results = []

    for keyword in keywords:
        html = google_search(keyword, url)
        if html:
            maillage_results = detect_maillage(html, keyword)
            all_results.extend(maillage_results)
            time.sleep(delay_between_requests)

    # Sauvegarder les résultats
    df = pd.DataFrame(all_results, columns=["Mot-clé", "URL trouvée"])
    df.to_csv(output_file, index=False)
    st.success("Recherche terminée et fichier enregistré.")

if __name__ == "__main__":
    main()
