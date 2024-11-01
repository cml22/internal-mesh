import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

def scrape_site_pages(url):
    """Scrape the site pages and return a list of internal links and their titles."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching {url}: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    
    # Find all internal links on the page
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(url):  # Only keep internal links
            title = link.get_text(strip=True) or "No Title"
            links.append((href, title))
    
    return links

def analyze_links(links, keywords):
    """Analyze links to check for keyword optimization and link connections."""
    analysis_results = []

    for keyword in keywords:
        optimized = False
        page_links = [link for link in links if keyword in link[1].lower()]
        internal_links = {link[0]: link[1] for link in links}

        # Check for connections between pages containing the keyword
        for page_link in page_links:
            if keyword.lower() in page_link[1].lower():
                for other_link in page_links:
                    if page_link[0] != other_link[0]:
                        # Check if there is a link between the pages
                        if not any(other_link[0] in l[0] for l in internal_links.items()):
                            analysis_results.append({
                                'Keyword': keyword,
                                'Page': page_link[1],
                                'Link': page_link[0],
                                'Status': 'Add Link'
                            })
                        else:
                            analysis_results.append({
                                'Keyword': keyword,
                                'Page': page_link[1],
                                'Link': page_link[0],
                                'Status': 'Already Linked'
                            })
                # Check if the anchor text is optimized
                if page_link[1].lower() == keyword.lower():
                    optimized = True

        if not optimized:
            analysis_results.append({
                'Keyword': keyword,
                'Page': page_links[0][1] if page_links else 'No Page Found',
                'Link': page_links[0][0] if page_links else 'No Link Found',
                'Status': 'Optimize Anchor'
            })

    return analysis_results

def main():
    # URL de votre site
    site_url = "https://votre-site.com"  # Remplacez par votre URL
    # Liste de mots-clés à analyser
    keywords = ["mot-clé 1", "mot-clé 2", "mot-clé 3"]  # Remplacez par vos mots-clés

    try:
        # Récupérer les pages internes du site
        links = scrape_site_pages(site_url)
        # Analyser les liens par rapport aux mots-clés
        results = analyze_links(links, keywords)

        # Convertir les résultats en DataFrame pour l'affichage
        df_results = pd.DataFrame(results)
        print(df_results)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
