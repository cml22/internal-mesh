import streamlit as st
import requests
from bs4 import BeautifulSoup

# Fonction pour extraire les hreflangs d'une URL
def extract_hreflangs(url):
    hreflangs = {}
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouver toutes les balises <link> avec rel="alternate" et hreflang
        for link in soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True}):
            hreflang = link['hreflang']
            href = link['href']
            hreflangs[hreflang] = href
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des hreflangs : {e}")

    return hreflangs

# Fonction principale
def main():
    st.title("Analyse de Similarité des SERP")

    # Champ pour l'URL à analyser
    url = st.text_input("Entrez l'URL à analyser")

    # Choix de la langue
    languages = {
        "fr": "Français",
        "en": "Anglais",
        "de": "Allemand",
        "es": "Espagnol",
        "it": "Italien",
        "pt": "Portugais",
        "nl": "Néerlandais",
        "pl": "Polonais",
        "ro": "Roumain",
        "tr": "Turc",
        # Ajoutez d'autres langues ici
    }
    selected_language = st.selectbox("Choisissez la langue", list(languages.keys()), format_func=lambda x: languages[x])

    # Choix du pays
    countries = {
        "fr": "France",
        "us": "États-Unis",
        "gb": "Royaume-Uni",
        "ca": "Canada",
        "de": "Allemagne",
        "es": "Espagne",
        # Ajoutez d'autres pays ici
    }
    selected_country = st.selectbox("Choisissez le pays", list(countries.keys()), format_func=lambda x: countries[x])

    # Bouton pour lancer l'analyse
    if st.button("Analyser"):
        if url:
            hreflangs = extract_hreflangs(url)
            if hreflangs:
                st.success("Hreflangs extraits avec succès !")
                st.write(hreflangs)
            else:
                st.warning("Aucun hreflang trouvé.")
        else:
            st.error("Veuillez entrer une URL valide.")

if __name__ == "__main__":
    main()
