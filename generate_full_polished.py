
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_brain.yoi_templates import build_slide_1_cover, build_news_slide, build_slide_5_cta

def generate_full_carousel():
    out_dir = "outputs/full_carousel_polished"
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating Cover Slide...")
    build_slide_1_cover(out_dir, "assets/yoi_logo.png")
    
    print("Generating News Slides...")
    news_items = [
        ("AI Marketing Trends 2025", "Hyper-personalization is becoming the norm."),
        ("Social Media Shift", "Video content continues to dominate over static images."),
        ("SEO Revolution", "Search engines are prioritizing helpful content over keywords.")
    ]
    
    for i, (head, insight) in enumerate(news_items):
        build_news_slide(out_dir, i+2, head, insight, "assets/yoi_logo.png")
        
    print("Generating CTA Slide...")
    build_slide_5_cta(out_dir, "assets/yoi_logo.png")
    
    print(f"Done! Check {out_dir}")

if __name__ == "__main__":
    generate_full_carousel()
