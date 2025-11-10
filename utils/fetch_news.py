import re
import requests
from bs4 import BeautifulSoup

def extract_article(url: str) -> str:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Remove unwanted tags
        for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
            tag.decompose()

        # Try multiple tag types
        text_blocks = soup.find_all(['p', 'div', 'article'])
        text = ' '.join(t.get_text(' ', strip=True) for t in text_blocks)
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    except Exception:
        return ""


