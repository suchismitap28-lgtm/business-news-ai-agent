from duckduckgo_search import DDGS

from bs4 import BeautifulSoup
import requests

def fetch_latest_articles(topic: str, max_results: int = 5):
    """Fetch and expand news content using DuckDuckGo results"""
    from duckduckgo_search import DDGS
    ddg = DDGS()
    results = ddg.news(topic, max_results=max_results)
    articles = []

    for r in results:
        url = r.get("url")
        title = r.get("title")
        source = r.get("source")
        if not url:
            continue
        try:
            page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(page.text, "html.parser")
            paras = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))
            if len(paras) > 300:
                articles.append({
                    "title": title,
                    "url": url,
                    "source": source,
                    "content": paras[:5000]
                })
        except Exception as e:
            print("Error scraping:", url, e)
    return articles

