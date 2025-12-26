INSIGHT_TEMPLATES = {
    "privacy": {
        "entity": "Market Insight",
        "category": "privacy",
        "summary": "Privacy Tightening Is Now the Default",
        "marketer_impact": "Ongoing youth safety and data controls continue to reduce targeting flexibility, pushing brands toward contextual and creative-led strategies.",
        "confidence": "confirmed"
    },
    "platform": {
        "entity": "Market Insight",
        "category": "platform",
        "summary": "Platforms Are Expanding Capabilities, Not Reach",
        "marketer_impact": "Recent updates show platforms focusing on tooling and control rather than distribution growth, favoring brands that optimize workflows.",
        "confidence": "confirmed"
    },
    "ads": {
        "entity": "Market Insight",
        "category": "ads",
        "summary": "Ad Platforms Are Prioritizing Automation",
        "marketer_impact": "Increased automation signals a shift toward algorithm-led optimization, making input quality more important than manual tuning.",
        "confidence": "confirmed"
    },
    "seo": {
        "entity": "Market Insight",
        "category": "seo",
        "summary": "Search Is Moving Toward System-Level Updates",
        "marketer_impact": "Recent changes emphasize core system updates over tactical SEO, rewarding long-term site quality.",
        "confidence": "confirmed"
    },
    "commerce": {
        "entity": "Market Insight",
        "category": "commerce",
        "summary": "Platforms Are Closing the Conversion Loop",
        "marketer_impact": "Commerce updates signal a push toward native checkout and reduced reliance on external funnels.",
        "confidence": "confirmed"
    },
    "creator_monetization": {
        "entity": "Market Insight",
        "category": "creator_monetization",
        "summary": "Creator Monetization Is Becoming Platform-Controlled",
        "marketer_impact": "Platforms are tightening monetization rules, impacting brand collaborations and influencer pricing dynamics.",
        "confidence": "confirmed"
    }
}


def generate_insight_items(existing_items, needed_count):
    """
    Generate deterministic insight items based on categories of existing news.
    
    Input:
    - existing_items: list of approved news items
    - needed_count: how many insight items to generate
    
    Output:
    - list of insight items (max = needed_count)
    """
    if needed_count <= 0:
        return []
    
    categories = [item.get("category", "platform") for item in existing_items]
    
    if not categories:
        categories = ["platform"]
    
    insights = []
    for category in categories:
        if category in INSIGHT_TEMPLATES:
            insights.append(INSIGHT_TEMPLATES[category].copy())
            if len(insights) >= needed_count:
                break
    
    while len(insights) < needed_count and "platform" in INSIGHT_TEMPLATES:
        insights.append(INSIGHT_TEMPLATES["platform"].copy())
    
    return insights[:needed_count]
