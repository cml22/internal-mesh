import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Configuration ---
keyword_file = 'mots_cles.txt'  # Chemin vers le fichier de mots-clés
site = "ovhcloud.com"  # Remplacez par votre site
output_file = 'opportunites_maillage.csv'  # Nom du fichier de sortie
url = "https://www.google.fr/search"  # URL de recherche Google pour votre locale
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fonction pour charger les mots-clés depuis un fichier texte
def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

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
   
