# Streamlit-based Internal Linking Opportunity Detector
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urlparse, urljoin
import logging

# Streamlit configuration
st.title("Internal Linking Opportunities Detector")
st.write("Upload your keywords file, configure the settings, and detect linking opportunities.")

# Configuration inputs
keyword_file = st.file_uploader("Upload your keywords file (motscles.txt)", type="txt")
site = st.text_input("Enter your website domain", "webloom.fr")
output_file = 'opportunites_maillage.csv'  # Fixed output file name
url = st.text_input("Enter Google Search URL", "https://www.google.fr/search")
delay_between_requests = st.slider("Delay between requests (seconds)", 1, 10, 2)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                  "AppleWebKit/537.36 (KHTML, like Gecko) " +
                  "Chrome/91.0.4472.124 Safari/537.36"
}

# Setup logging
logging.basicConfig(
    filename='maillage_debug.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load keywords from uploaded file
def load_keywords(file):
    try:
        keywords = [line.decode("utf-8").strip() for line in file if line.strip()]
        logging.info(f"Loaded {len(keywords)} keywords from uploaded file")
        return keywords
    except Exception as e:
        logging.error(f"Error loading keywords: {e}")
        st.error("Error loading keywords.")
        raise

# Perform a Google search for a specific keyword
def google_search(query, site=None, num_results=10):
    try:
        search_query = f'{query} site:{site}' if site else query
        params = {"q": search_query, "num": num_results}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for g in soup.find_all('div', class_='tF2Cxc'):
            a_tag = g.find('a', href=True)
            if a_tag:
                links.append(a_tag['href'])
        logging.info(f"Google search for '{search_query}' returned {len(links)} links")
        return links
    except requests.RequestException as e:
        logging.error(f"HTTP error during Google search for '{query}': {e}")
        return []

# Check if a link exists with optimized anchor text
def check_existing_link(source_url, target_url, keyword):
    try:
        response = requests.get(source_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        target_path = urlparse(target_url).path.lower()
        keyword_lower = keyword.lower()

        for a_tag in soup.find_all('a', href=True):
            normalized_href = urljoin(source_url, a_tag['href'])
            parsed_href = urlparse(normalized_href)
            if parsed_href.path.lower() == target_path:
                anchor_text = a_tag.get_text().strip().lower()
                return (True, 'Oui' if anchor_text == keyword_lower else 'Non')
        return (False, 'Non')
    except requests.RequestException as e:
        logging.warning(f"HTTP error accessing '{source_url}': {e}")
        return (False, 'Non')

# Detect linking opportunities
def detect_maillage(keywords, site):
    maillage_opportunities = []
    for idx, keyword in enumerate(keywords, start=1):
        st.write(f"[{idx}/{len(keywords)}] Recherche pour le mot-clé : {keyword}")
        links = google_search(keyword, site)

        if links:
            top_link = links[0]
            for link in links[1:]:
                exists, anchor_optimized = check_existing_link(link, top_link, keyword)
                if not exists:
                    maillage_opportunities.append([keyword, link, top_link, "Ajouter un lien", 'Non Applicable'])
                elif anchor_optimized == 'Non':
                    maillage_opportunities.append([keyword, link, top_link, "Optimiser l'ancre", 'Non'])
        time.sleep(delay_between_requests)
    return maillage_opportunities

# Export results
def export_to_csv(maillage_opportunities, output_file):
    df = pd.DataFrame(maillage_opportunities, columns=["Mot-Clé", "Page Source", "Page Cible", "Action Requise", "Anchor Optimisé"])
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    st.write(f"Opportunités de maillage interne exportées dans : {output_file}")

# Main app logic
if st.button("Start Process"):
    if keyword_file:
        keywords = load_keywords(keyword_file)
        if keywords:
            maillage_opportunities = detect_maillage(keywords, site)
            if maillage_opportunities:
                export_to_csv(maillage_opportunities, output_file)
                st.download_button("Download CSV", data=pd.read_csv(output_file).to_csv(), file_name=output_file)
            else:
                st.write("No linking opportunities found.")
    else:
        st.error("Please upload a keywords file.")
