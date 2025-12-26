from datetime import datetime

VISUAL_MAPPING = {
    "platform": "bold, platform-branded",
    "ads": "performance-focused, data-led",
    "seo": "clean, analytical",
    "privacy": "serious, trust-focused",
    "commerce": "conversion-focused",
    "creator_monetization": "creator-first, minimal"
}


def build_post_payload(pipeline_output):
    if isinstance(pipeline_output, dict) and pipeline_output.get("status") == "no_publish_today":
        return pipeline_output
    
    if not pipeline_output or not isinstance(pipeline_output, dict):
        return {"status": "no_publish_today"}
    
    approved = pipeline_output.get("approved", [])
    
    if not approved:
        return {"status": "no_publish_today"}
    
    items = []
    for item in approved:
        category = item.get("category", "platform")
        items.append({
            "entity": item.get("entity", ""),
            "category": category,
            "headline": item.get("summary", ""),
            "subheadline": item.get("marketer_impact", ""),
            "visual_direction": VISUAL_MAPPING.get(category, VISUAL_MAPPING["platform"]),
            "platform": "instagram"
        })
    
    return {
        "publish_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "items": items
    }
