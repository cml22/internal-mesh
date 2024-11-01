import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Configuration ---
keyword_file = 'mots_cles.txt'  # Chemin vers le fichier de mots-clés
site = ""  # Laissez vide pour permettre à l'utilisateur de le remplir via Streamlit
output_file = 'opportunites_maillage.csv'  # Nom du fichier de sortie
url = "https://www.google.fr/search"  # URL de recherche Google pour votre locale
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fonction pour charger les mots-clés depuis un fichier texte
def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]  # Ignore les lignes vides

# Fonction pour effectuer une recherche Google et récupérer les résultats pour un mot-clé spécifique
def google_search(query, site=None):
    params = {"q": f"{query} site:{site}" if site else query, "num": 10}  # Recherche les 10 premiers résultats
    response = requests.get(url, headers=headers, params=params)
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
def find_linking_opportunities(keywords, site):
    opportunities = []
    for keyword in keywords:
        print(f"Traitement du mot-clé : {keyword}")
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
    return pd.DataFrame(opportunities)

# Chargement des mots-clés
keywords = load_keywords(keyword_file)

# Vérifiez si des mots-clés ont été chargés
if not keywords:
    print("Aucun mot-clé trouvé dans le fichier. Veuillez vérifier le contenu du fichier.")
else:
    # Recherche des opportunités de maillage interne
    df_opportunities = find_linking_opportunities(keywords, site)

    # Vérifiez si des opportunités ont été trouvées
    if df_opportunities.empty:
        print("Aucune opportunité de maillage interne trouvée.")
    else:
        # Exportation des résultats dans un fichier CSV
        df_opportunities.to_csv(output_file, index=False)
        print("Les opportunités de maillage ont été enregistrées dans 'opportunites_maillage.csv'.")
