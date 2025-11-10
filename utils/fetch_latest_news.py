from duckduckgo_search import DDGS

def fetch_latest_articles(topic: str, max_results: int = 5):
    """Fetch recent business news articles related to a topic using DuckDuckGo."""
    try:
        ddg = DDGS()
        results = ddg.news(topic, max_results=max_results)
        articles = []
        for r in results:
            articles.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "source": r.get("source"),
                "date": r.get("date")
            })
        return articles
    except Exception as e:
        print("DuckDuckGo fetch error:", e)
        return []
