import os
import requests
from ai_brain.config import SERPAPI_KEY

def fetch_trending_topics(query="digital marketing trends", num_results=5):
    """
    Fetch trending topics from Google News via SerpAPI.
    Returns a list of trending headlines or topics.
    """
    if not SERPAPI_KEY:
        print("⚠️ No SerpAPI key found, using fallback topics.")
        return [
            "AI-driven marketing campaigns",
            "SEO automation trends",
            "Influencer marketing in 2025",
            "Data-driven personalization",
            "Future of digital advertising"
        ]

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
        "hl": "en"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        headlines = [item["title"] for item in data.get("news_results", [])[:num_results]]
        return headlines or ["No trends found."]

    except Exception as e:
        print("⚠️ Error fetching trends:", e)
        return [
            "Digital marketing innovation",
            "AI in customer engagement",
            "Automation for small businesses"
        ]
