import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urlparse, urljoin
import logging

# --- Configuration settings (what to change) ---
keyword_file = 'keywords.txt'                     # Path to your keywords file
site = "yourwebsite.com"                            # Your website (change as needed)
output_file = 'link_opportunities.csv'            # Output file for opportunities
url = "https://www.google.com/search"              # Google search URL (change for your locale)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                  "AppleWebKit/537.36 (KHTML, like Gecko) " +
                  "Chrome/91.0.4472.124 Safari/537.36"
}
delay_between_requests = 2  # seconds

# Setup logging
logging.basicConfig(
    filename='link_debug.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load keywords from a text file (one keyword per line)
def load_keywords(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(keywords)} keywords from {file_path}")
        return keywords
    except FileNotFoundError:
        logging.error(f"Keyword file not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading keywords: {e}")
        raise

# Perform a Google search and retrieve results for a specific keyword
def google_search(query, site=None, num_results=10):
    try:
        search_query = f'{query} site:{site}' if site else query
        params = {"q": search_query, "num": num_results}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for g in soup.find_all('div', class_='tF2Cxc'):
            a_tag = g.find('a', href=True)
            if a_tag:
                link = a_tag['href']
                links.append(link)
        logging.info(f"Google search for '{search_query}' returned {len(links)} links")
        return links
    except requests.RequestException as e:
        logging.error(f"HTTP error during Google search for '{query}': {e}")
        return []
    except Exception as e:
        logging.error(f"Error during Google search for '{query}': {e}")
        return []

# Function to check if a source page links to the target page and if the anchor is optimized
def check_existing_link(source_url, target_url, keyword):
    try:
        response = requests.get(source_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        target_path = urlparse(target_url).path.lower()
        keyword_lower = keyword.lower()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Normalize href
            normalized_href = urljoin(source_url, href)
            parsed_href = urlparse(normalized_href)
            if parsed_href.path.lower() == target_path:
                # Found a link to the target page
                anchor_text = a_tag.get_text().strip().lower()
                if anchor_text == keyword_lower:
                    return (True, 'Yes')  # Link exists and anchor is optimized
                else:
                    return (True, 'No')  # Link exists but anchor is not optimized
        return (False, 'No')  # Link does not exist
    except requests.RequestException as e:
        logging.warning(f"HTTP error accessing '{source_url}': {e}")
        return (False, 'No')
    except Exception as e:
        logging.warning(f"Error parsing '{source_url}': {e}")
        return (False, 'No')

# Detect linking opportunities by linking all pages to the top 1 result
def detect_link_opportunities(keywords, site):
    link_opportunities = []

    for idx, keyword in enumerate(keywords, start=1):
        print(f"[{idx}/{len(keywords)}] Searching for keyword: {keyword}")
        logging.info(f"Processing keyword {idx}/{len(keywords)}: '{keyword}'")
        links = google_search(keyword, site)

        if len(links) > 0:
            top_link = links[0]  # The top 1 link
            for link in links[1:]:
                exists, anchor_optimized = check_existing_link(link, top_link, keyword)
                if not exists:
                    action = "Add a link"
                    link_opportunities.append([keyword, link, top_link, action, 'Not Applicable'])
                    logging.info(f"Link opportunity: '{link}' → '{top_link}' for keyword '{keyword}' (Add Link)")
                else:
                    if anchor_optimized == 'No':
                        action = "Optimize anchor"
                        link_opportunities.append([keyword, link, top_link, action, 'No'])
                        logging.info(f"Anchor optimization needed: '{link}' already links to '{top_link}' with non-optimized anchor for keyword '{keyword}'")
                    else:
                        logging.info(f"Existing optimized link found: '{link}' already links to '{top_link}' with optimized anchor for keyword '{keyword}'")
        else:
            logging.info(f"No links found for keyword '{keyword}'.")

        time.sleep(delay_between_requests)  # Pause to avoid being blocked

    return link_opportunities

# Export results to a CSV file
def export_to_csv(link_opportunities, output_file):
    try:
        df = pd.DataFrame(link_opportunities, columns=["Keyword", "Source Page", "Target Page", "Required Action", "Optimized Anchor"])
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Link opportunities exported to: {output_file}")
        logging.info(f"Exported {len(link_opportunities)} opportunities to '{output_file}'")
    except Exception as e:
        logging.error(f"Error exporting to CSV: {e}")
        raise

# Load keywords and start the process
def main():
    try:
        # Load keywords
        keywords = load_keywords(keyword_file)

        if not keywords:
            print(f"No keywords found in {keyword_file}.")
            logging.warning(f"No keywords found in '{keyword_file}'. Exiting.")
            return

        # Detect internal linking opportunities
        link_opportunities = detect_link_opportunities(keywords, site)

        if link_opportunities:
            # Export results to a CSV file
            export_to_csv(link_opportunities, output_file)
        else:
            print("No internal linking opportunities found.")
            logging.info("No linking opportunities found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.critical(f"Critical error in main: {e}")

if __name__ == "__main__":
    main()
