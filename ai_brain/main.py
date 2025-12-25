import json
import os
from ai_brain.groq_generator import generate_three_news_prompts
from ai_brain.trend_fetcher import fetch_real_news
from ai_brain.carousel_generator import make_dir, generate_leonardo_slide
from ai_brain.yoi_templates import (
    build_slide_1_cover,
    # build_news_slide, # Moving to AI for news
    build_slide_5_cta
)


def main():
    print("\n🚀 YOI Carousel Automation Starting...\n")

    # STEP 1: Fetch real SERP news
    raw_news = fetch_real_news()
    print("📌 Raw SERP news items:", raw_news)

    # STEP 2: Convert to slide-friendly structure
    slides_data = generate_three_news_prompts(raw_news)
    print("\n📝 Groq Output:")
    print(json.dumps(slides_data, indent=2))

    out_dir = make_dir("yoi_carousel")

    manifest = {
        "run_id": out_dir,
        "raw_news": raw_news,
        "slides": []
    }

    print("\n" + "="*60)
    print("🎨 Generating YOI Marketing News Carousel")
    print("="*60 + "\n")

    # SLIDE 1: Cover (Static Template)
    print("📄 Generating Slide 1 (Cover)...")
    slide_1_path = build_slide_1_cover(out_dir)
    manifest["slides"].append({"slide": 1, "type": "cover", "path": slide_1_path})
    print(f"✅ Slide 1 complete: {slide_1_path}\n")

    # SLIDES 2-4: Dynamic News Content
    for slide in slides_data["slides"]:
        slide_num = slide["slide"]
        headline = slide["headline"]
        insight = slide["insight"]

        print(f"📰 Generating Slide {slide_num} (News)...")
        print(f"   Headline: {headline}")
        print(f"   Insight: {insight}")
        
        # Try Leonardo Generation (with Text)
        news_slide_path = generate_leonardo_slide(
            out_dir,
            slide_num,
            headline,
            insight
        )
        
        # Fallback if AI fails (e.g. no credits or error)
        if not news_slide_path:
             print("⚠️ Leonardo failed. Falling back to PIL template...")
             from ai_brain.yoi_templates import build_news_slide
             news_slide_path = build_news_slide(out_dir, slide_num, headline, insight)
        
        manifest["slides"].append({
            "slide": slide_num,
            "type": "news",
            "headline": headline,
            "insight": insight,
            "path": news_slide_path
        })
        print(f"✅ Slide {slide_num} complete: {news_slide_path}\n")

    # SLIDE 5: CTA (Static Template)
    print("📄 Generating Slide 5 (CTA)...")
    slide_5_path = build_slide_5_cta(out_dir)
    manifest["slides"].append({"slide": 5, "type": "cta", "path": slide_5_path})
    print(f"✅ Slide 5 complete: {slide_5_path}\n")

    # Save manifest
    with open(f"{out_dir}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("="*60)
    print("✅ CAROUSEL COMPLETE!")
    print("="*60)
    print(f"\n📁 Output directory: {out_dir}")
    print(f"📊 Total slides: 5 (Cover + 3 News + CTA)")
    print(f"💰 Leonardo credits used: 0 (100% PIL)")
    print("\n🎯 All slides ready for Instagram upload!")


if __name__ == "__main__":
    main()
