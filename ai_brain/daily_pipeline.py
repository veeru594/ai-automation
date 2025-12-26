from ai_brain.trend_fetcher import fetch_real_news
from ai_brain.editorial_gate import evaluate_news
from ai_brain.dedup_memory import load_posted_titles, save_posted_title
from ai_brain.insight_filler import generate_insight_items


def _deduplicate_entities(approved_items):
    """
    Spam guard: keep only first occurrence of each entity.
    """
    seen = set()
    filtered = []
    
    for item in approved_items:
        entity = item.get("entity", "").lower()
        if entity not in seen:
            seen.add(entity)
            filtered.append(item)
    
    return filtered


def run_daily_pipeline():
    """
    Daily pipeline: fetch → evaluate → deduplicate → fill to 3.
    
    Returns:
    {
        "approved": [...],  # Always 3 items if any real news exists
        "rejected": [...]
    }
    
    OR:
    {
        "status": "no_publish_today"
    }
    """
    
    news_signals = fetch_real_news()
    
    if not news_signals:
        return {"status": "no_publish_today"}
    
    posted_titles = load_posted_titles()
    
    editorial_result = evaluate_news(news_signals, posted_titles)
    
    if "error" in editorial_result:
        return {"status": "no_publish_today"}
    
    approved = editorial_result.get("approved", [])
    
    approved = _deduplicate_entities(approved)
    
    if not approved:
        return {"status": "no_publish_today"}
    
    if len(approved) >= 3:
        approved = approved[:3]
    else:
        needed = 3 - len(approved)
        insights = generate_insight_items(approved, needed)
        approved.extend(insights)
    
    for item in approved:
        if item.get("entity") != "Market Insight":
            save_posted_title(item.get("summary", ""))
    
    return {
        "approved": approved,
        "rejected": editorial_result.get("rejected", [])
    }
