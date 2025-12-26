def build_leonardo_payload(post_payload):
    if isinstance(post_payload, dict) and post_payload.get("status") == "no_publish_today":
        return post_payload
    
    if not post_payload or not isinstance(post_payload, dict):
        return {"status": "no_publish_today"}
    
    items = post_payload.get("items", [])
    
    if not items:
        return {"status": "no_publish_today"}
    
    slides = []
    for idx, item in enumerate(items, start=1):
        slides.append({
            "slide_index": idx,
            "text_blocks": {
                "headline": item.get("headline", ""),
                "subheadline": item.get("subheadline", "")
            },
            "style_hint": item.get("visual_direction", "")
        })
    
    return {
        "image_ratio": "4:5",
        "slides": slides
    }
