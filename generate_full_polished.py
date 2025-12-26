import os
import sys
import time
import json

from ai_brain.config import OUTPUT_DIR
from ai_brain.daily_pipeline import run_daily_pipeline
from ai_brain.post_payload_builder import build_post_payload
from ai_brain.yoi_templates import build_slide_1_cover, build_news_slide, build_slide_5_cta


def generate_interactive_carousel():
    print("🚀 Starting Static Carousel Generation...")
    print("⚠️  Leonardo disabled — using static backgrounds only")
    
    # 1. Run daily pipeline
    print("\n[1/3] Running daily pipeline...")
    pipeline_result = run_daily_pipeline()
    
    if pipeline_result.get("status") == "no_publish_today":
        print("❌ ERROR: No approved content for today.")
        sys.exit(1)
    
    approved_count = len(pipeline_result.get("approved", []))
    print(f"✅ Pipeline approved: {approved_count} items")
    
    # 2. Build post payload
    print("\n[2/3] Building post payload...")
    post_payload = build_post_payload(pipeline_result)
    
    if post_payload.get("status") == "no_publish_today":
        print("❌ ERROR: Post payload build failed.")
        sys.exit(1)
    
    # 3. Build slides with static backgrounds
    print("\n[3/3] Building slides with static backgrounds...")
    
    carousel_dir = os.path.join(OUTPUT_DIR, f"static_run_{int(time.time())}")
    os.makedirs(carousel_dir, exist_ok=True)
    
    items = post_payload.get("items", [])
    
    if len(items) < 3:
        print(f"❌ ERROR: Expected 3 items, got {len(items)}")
        sys.exit(1)
    
    # Cover slide
    print("\n  Building cover slide...")
    build_slide_1_cover(carousel_dir)
    print("    ✅ Cover complete")
    
    # News/Insight slides - UNIQUE ITEMS ONLY
    for idx in range(3):
        item = items[idx]
        slide_num = idx + 2
        
        category = item.get("category", "platform")
        headline = item.get("headline", "")
        subheadline = item.get("subheadline", "")
        entity = item.get("entity", "")
        
        # Determine slide type
        slide_type = "insight" if entity == "Market Insight" else "news"
        
        print(f"\n  Building slide {slide_num} ({slide_type})...")
        print(f"    Headline: {headline[:50]}...")
        build_news_slide(carousel_dir, slide_num, headline, subheadline)
        print(f"    ✅ Slide {slide_num} complete")
    
    # CTA slide
    print("\n  Building CTA slide...")
    build_slide_5_cta(carousel_dir)
    print("    ✅ CTA complete")
    
    print(f"\n✨ Generation Complete! Output: {carousel_dir}")
    
    # JSON for n8n
    result = {
        "status": "success",
        "output_dir": carousel_dir,
        "files": [f for f in os.listdir(carousel_dir) if f.endswith(".png")],
        "pipeline_summary": {
            "approved_count": approved_count,
            "slides_generated": len(items) + 2,
            "background_mode": "static_only"
        }
    }
    print("---JSON_START---")
    print(json.dumps(result))
    print("---JSON_END---")


if __name__ == "__main__":
    generate_interactive_carousel()
