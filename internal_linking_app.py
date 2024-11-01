import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

def scrape_opportunity_maillage(keyword, language, country, num_results):
    query = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={query}&hl={language}&gl={country}&num={num_results}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, KHTML, Gecko) Chrome/116.0.5845.96 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Error while fetching results.")

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    # Scraping des résultats
    for g in soup.find_all('div', class_='g')[:num_results]:
        link = g.find('a', href=True)
        title = g.find('h3').get_text() if g.find('h3') else "Title not found"
        snippet = g.find('span', class_='aCOpRe').get_text() if g.find('span', class_='aCOpRe') else "Snippet not found"

        if link:
            results.append({
                'URL': link['href'],
                'Title': title,
                'Snippet': snippet
            })

    return results

# Exemple d'utilisation
keyword = "votre mot-clé"
language = "fr"  # Exemple pour le français
country = "FR"  # Exemple pour la France
num_results = 10  # Nombre de résultats à scraper

try:
    results = scrape_opportunity_maillage(keyword, language, country, num_results)
    df_results = pd.DataFrame(results)
    print(df_results)
except Exception as e:
    print(e)
