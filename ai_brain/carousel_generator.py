import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from ai_brain.config import OUTPUT_DIR

# helper resize from request size -> IG size
def resize_to_ig(path):
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((1080, 1350), Image.LANCZOS)
        img.save(path, "PNG")
    except Exception as e:
        return {"error": f"Resize failed: {e}"}
    return {"ok": True, "path": path}

def make_dir(prefix="yoi_carousel"):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"{prefix}_{ts}")
    os.makedirs(path, exist_ok=True)
    return path

# Slide 1 & 5 are static saved locally (no credit)
def build_static_cover(path, topic):
    # Create a simple grid + dotted border + placeholder text as requested (real text)
    img = Image.new("RGB", (1080, 1350), "white")
    draw = ImageDraw.Draw(img)
    # Draw simple light grid
    step = 40
    for x in range(0, 1080, step):
        draw.line([(x, 0), (x, 1350)], fill="#efefef", width=1)
    for y in range(0, 1350, step):
        draw.line([(0, y), (1080, y)], fill="#efefef", width=1)

    # simple dotted top and bottom rows
    dot_x = 30
    for i in range(10, 1080 - 10, 30):
        draw.ellipse([(i, 20), (i+10, 30)], fill="black")
        draw.ellipse([(i, 1320), (i+10, 1330)], fill="black")

    # Put brand marker and headline text
    font_path = None
    try:
        # try default PIL font; user can customize later
        title_font = ImageFont.truetype(font_path or "arial.ttf", 48)
        body_font = ImageFont.truetype(font_path or "arial.ttf", 36)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Draw headline (real text as chosen)
    headline = "Stop scrolling"
    sub = topic if len(topic) < 60 else topic[:57] + "..."
    draw.text((80, 160), headline, font=title_font, fill="black")
    draw.text((80, 260), sub, font=body_font, fill="black")

    out = os.path.join(path, "slide_1_cover.png")
    img.save(out, "PNG")
    return out

def build_static_cta(path):
    img = Image.new("RGB", (1080, 1350), "white")
    draw = ImageDraw.Draw(img)
    # grid background
    step = 40
    for x in range(0, 1080, step):
        draw.line([(x, 0), (x, 1350)], fill="#efefef", width=1)
    for y in range(0, 1350, step):
        draw.line([(0, y), (1080, y)], fill="#efefef", width=1)

    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        title_font = ImageFont.load_default()
    draw.text((120, 500), "Thank you for reading!", font=title_font, fill="black")
    draw.text((120, 580), "Follow @YOIMarketing for more updates!", font=title_font, fill="black")
    out = os.path.join(path, "slide_5_cta.png")
    img.save(out, "PNG")
    return out

# Leonardo prompt for BACKGROUND ONLY (text will be added via PIL)
def build_leonardo_background_prompt(slide_num: int) -> tuple:
    """
    Generate modern gradient background for Instagram carousel
    Returns: (positive_prompt, negative_prompt)
    """
    colors = [
        ("vibrant orange", "deep purple", "modern tech"),
        ("electric blue", "cyan", "digital innovation"),
        ("coral pink", "golden yellow", "creative energy")
    ]
    
    color1, color2, theme = colors[(slide_num - 2) % 3]
    
    positive_prompt = f"""
Professional Instagram carousel background, {theme} aesthetic.
Smooth gradient from {color1} to {color2}, diagonal flow.
Clean, modern, minimalist design.
1080x1350 aspect ratio, vertical format.
NO text, NO icons, NO illustrations - pure gradient only.
Soft, premium feel with subtle depth.
"""

    # CRITICAL: Negative prompt blocks unwanted elements that would clash with text
    negative_prompt = """
text, words, letters, numbers, typography, captions, titles, labels,
icons, symbols, logos, shapes, geometric shapes, circles, squares,
illustrations, drawings, sketches, cartoon, anime,
people, faces, portraits, hands, body parts,
objects, items, products, buildings, nature,
watermark, signature, copyright, username,
frames, borders, boxes, patterns with high detail,
cluttered, busy, complex, noisy, messy
"""
    
    return (positive_prompt.strip(), negative_prompt.strip())


def add_text_overlay(image_path: str, headline: str, insight: str, slide_num: int) -> dict:
    """Overlay professional text on background image using PIL"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Open the Leonardo-generated background
        img = Image.open(image_path).convert("RGBA")
        
        # Create text layer
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Load fonts (try multiple options for compatibility)
        try:
            headline_font = ImageFont.truetype("arialbd.ttf", 72)  # Bold
            body_font = ImageFont.truetype("arial.ttf", 48)
            slide_font = ImageFont.truetype("arial.ttf", 32)
        except:
            try:
                headline_font = ImageFont.truetype("Arial Bold.ttf", 72)
                body_font = ImageFont.truetype("Arial.ttf", 48)
                slide_font = ImageFont.truetype("Arial.ttf", 32)
            except:
                # Fallback to default
                headline_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
                slide_font = ImageFont.load_default()
        
        # Add semi-transparent overlay for better text readability
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 100))  # Dark overlay, 40% opacity
        img = Image.alpha_composite(img, overlay)
        
        # Text wrapping helper
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                
                if width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
        
        # Wrap headline and insight
        max_width = 900  # Leave margins
        headline_lines = wrap_text(headline, headline_font, max_width)
        insight_lines = wrap_text(insight, body_font, max_width)
        
        # Draw headline (top third)
        y_pos = 200
        for line in headline_lines:
            bbox = draw.textbbox((0, 0), line, font=headline_font)
            text_width = bbox[2] - bbox[0]
            x_pos = (1080 - text_width) // 2  # Center
            
            # Text shadow for depth
            draw.text((x_pos + 3, y_pos + 3), line, font=headline_font, fill=(0, 0, 0, 180))
            draw.text((x_pos, y_pos), line, font=headline_font, fill=(255, 255, 255, 255))
            y_pos += 90
        
        # Draw insight (middle)
        y_pos += 80
        for line in insight_lines:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            text_width = bbox[2] - bbox[0]
            x_pos = (1080 - text_width) // 2
            
            draw.text((x_pos + 2, y_pos + 2), line, font=body_font, fill=(0, 0, 0, 150))
            draw.text((x_pos, y_pos), line, font=body_font, fill=(255, 255, 255, 230))
            y_pos += 65
        
        # Draw slide number (bottom right)
        slide_text = f"Slide {slide_num}"
        draw.text((920, 1280), slide_text, font=slide_font, fill=(255, 255, 255, 200))
        
        # Composite text layer onto image
        final_img = Image.alpha_composite(img, txt_layer)
        final_img = final_img.convert("RGB")
        
        # Save
        final_img.save(image_path, "PNG")
        
        return {"ok": True, "path": image_path}
        
    except Exception as e:
        return {"error": f"Text overlay failed: {e}"}
        

# ==========================================
# DIRECT LEONARDO GENERATION (WITH TEXT)
# ==========================================

from image_generation.leonardo_client import generate_image_with_poll

def build_leonardo_text_prompt(title: str, content: str) -> str:
    """
    Constructs the prompt for Leonardo to generate the full slide including text.
    """
    return f"""
Create a high-quality Instagram carousel background visual.

Topic: {{TOPIC}}

Guidelines:
- Do NOT include long text or paragraphs
- If text appears, it must be minimal and generic
- Leave clear negative space suitable for overlaying text later
- Clean, modern, professional aesthetic
- Visually strong but not cluttered

Technical:
- Square (1:1)
- High contrast
- Sharp, production-quality image

"""

def generate_leonardo_slide(output_dir: str, slide_num: int, title: str, content: str) -> str:
    """
    Generates a slide using Leonardo AI with the text embedded in the prompt.
    """
    prompt = build_leonardo_text_prompt(title, content)
    
    out_path = os.path.join(output_dir, f"slide_{slide_num}.png")
    
    print(f"   [Leonardo] Sending Prompt: {title}...")
    
    # Use config default model ID (fallback or env var)
    # The user is responsible for ensuring LEONARDO_MODEL_ID is valid in .env
    result = generate_image_with_poll(
        prompt=prompt,
        out_path=out_path,
        negative_prompt="blurry, ugly, distorted text, unreadable, watermark, low quality, pixelated"
    )
    
    if result.get("error"):
        print(f"   [Leonardo Error] {result['error']}")
        # Fallback? For now, just return None or raise
        return None
        
    return result.get("path")
