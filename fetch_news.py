import re
import requests
from bs4 import BeautifulSoup

def extract_article(url: str) -> str:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
            tag.decompose()
        text = ' '.join(p.get_text(' ', strip=True) for p in soup.find_all('p'))
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception:
        return ""
