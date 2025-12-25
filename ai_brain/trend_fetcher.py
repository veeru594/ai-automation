import requests
from ai_brain.config import SERPAPI_KEY

def fetch_real_news():
    API_KEY = SERPAPI_KEY
    search_queries = [
        "digital marketing news 2026",
        "AI marketing updates",
        "social media platform updates",
    ]

    results = []

    for q in search_queries:
        url = f"https://serpapi.com/search.json?q={q}&tbm=nws&api_key={API_KEY}"
        res = requests.get(url).json()

        if "news_results" in res and len(res["news_results"]) > 0:
            top_item = res["news_results"][0]
            results.append({
                "title": top_item.get("title", "").strip(),
                "snippet": top_item.get("snippet", "").strip()
            })

        if len(results) == 3:
            break

    return results
