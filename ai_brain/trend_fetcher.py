import requests
from datetime import datetime, timedelta
from urllib.parse import quote_plus

from ai_brain.config import SERPAPI_KEY

SERP_ENDPOINT = "https://serpapi.com/search.json"

# Official sources only
ALLOWED_DOMAINS = [
    "instagram.com",
    "about.instagram.com",
    "openai.com",
    "blog.google",
    "developers.google.com",
    "business.facebook.com",
    "ads.tiktok.com",
    "newsroom.tiktok.com",
    "blog.linkedin.com",
    "searchengineland.com"
]

# Announcement-style queries (LOCKED)
SEARCH_QUERIES = [
    # Platforms
    "site:about.instagram.com announces OR launches OR rolls out",
    "site:openai.com announces OR releases",
    "site:blog.google announces OR core update OR algorithm update",
    "site:newsroom.tiktok.com announces OR launches",
    "site:blog.linkedin.com announces OR rolls out",

    # Ads & marketing systems
    "site:business.facebook.com announces ads OR targeting",
    "site:ads.tiktok.com announces OR launches",
    "site:blog.google announces ads OR performance max",

    # SEO & tracking
    "site:developers.google.com announces analytics OR search update",
    "site:searchengineland.com reports google update confirmed",

    # Commerce & monetization
    "site:about.instagram.com announces shopping OR monetization",
    "site:newsroom.tiktok.com announces creator monetization"
]

REJECT_KEYWORDS = [
    "how to", "guide", "tips", "explained",
    "what marketers", "why you should"
]


def _is_recent(date_str: str, days: int = 3) -> bool:
    if not date_str:
        return False
    try:
        published = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return published >= datetime.utcnow() - timedelta(days=days)
    except:
        return True  # SERP date formats vary, don't hard-fail


def _allowed_source(link: str) -> bool:
    return any(domain in link for domain in ALLOWED_DOMAINS)


def _is_fluff(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in REJECT_KEYWORDS)


def fetch_real_news(max_items: int = 15):
    results = []

    for query in SEARCH_QUERIES:
        q = quote_plus(query)

        url = (
            f"{SERP_ENDPOINT}"
            f"?q={q}"
            f"&tbm=nws"
            f"&tbs=qdr:3d"
            f"&api_key={SERPAPI_KEY}"
        )

        response = requests.get(url, timeout=20)
        data = response.json()

        for item in data.get("news_results", []):
            title = item.get("title", "").strip()
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            source = item.get("source", "")
            date = item.get("date", "")

            if not title or not link:
                continue
            if _is_fluff(title):
                continue
            if not _allowed_source(link):
                continue
            if not _is_recent(date):
                continue

            results.append({
                "entity": source.split()[0],
                "title": title,
                "snippet": snippet,
                "source": source,
                "url": link,
                "published_at": date
            })

            if len(results) >= max_items:
                return results

    return results
