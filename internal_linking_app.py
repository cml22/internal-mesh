import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Streamlit app title
st.title("Internal Linking Opportunities Finder")

# Configuration settings for Google Search
url = "https://www.google.fr/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to load keywords from a file
def load_keywords(file):
    return [line.strip() for line in file]

# Perform a Google search and retrieve results for a specific keyword
def google_search(query, site=None):
    params = {"q": f'{query} site:{site}' if site else query, "num": 10}  # Search top 10 results
    response = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    return [a['href'] for a in soup.select('a[href^="http"]') if site in a['href']]

# Check if the anchor text exactly matches the keyword
def check_anchor(keyword, url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Ensure we process only valid anchor tags and skip if there's an issue
        return any(keyword.lower() in a.get_text(strip=True).lower() for a in soup.find_all('a') if a.get_text(strip=True))
    except Exception as e:
        st.write(f"Error checking anchor for URL {url}: {e}")
        return False

# Main function to find internal linking opportunities
def find_linking_opportunities(keywords, site):
    opportunities = []
    for keyword in keywords:
        st.write(f"Processing keyword: {keyword}")
        time.sleep(2)  # Delay to prevent blocking
        results = google_search(keyword, site=site)
        
        for result_url in results:
            anchor_match = check_anchor(keyword, result_url)
            action = "Ajouter un lien" if not anchor_match else "Optimiser l'ancre"
            opportunities.append({
                'Keyword': keyword,
                'URL': result_url,
                'Action': action
            })

    return pd.DataFrame(opportunities)

# Streamlit sidebar inputs
st.sidebar.header("Configuration")
site = st.sidebar.text_input("Enter your website domain", "yourwebsite.com")

# File uploader for keywords
uploaded_file = st.file_uploader("Upload a text file with keywords (one per line)", type="txt")

# Process the file and display linking opportunities
if uploaded_file and site:
    keywords = load_keywords(uploaded_file)
    df_opportunities = find_linking_opportunities(keywords, site)

    # Display results in Streamlit
    st.subheader("Linking Opportunities")
    st.write(df_opportunities)

    # Button to download results as CSV
    csv = df_opportunities.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='opportunites_maillage.csv',
        mime='text/csv'
    )
