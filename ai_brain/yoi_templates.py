"""
YOI Marketing Carousel Templates - 100% PIL Implementation
Recreates the exact design style with grid background, decorative elements, and news content
"""
import os
from PIL import Image, ImageDraw, ImageFont
from PIL import Image, ImageDraw, ImageFont, ImagePath
import math
from datetime import datetime


# ============================================
# HELPER FUNCTIONS
# ============================================

def draw_grid_background(draw, width, height, grid_size=40, color="#222222"):
    """Draw dark grid pattern on background (for fallbacks)"""
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=color, width=1)


def resolve_background(slide_type):
    """
    Static background resolver - NO AI, NO FALLBACK.
    
    Args:
        slide_type: "cover" | "news" | "insight" | "cta"
    
    Returns:
        Absolute path to background file
    
    Raises:
        FileNotFoundError if background missing
    """
    mapping = {
        "cover": "assets/backgrounds/bg_cover.jpg",
        "news": "assets/backgrounds/bg_news.jpg",
        "insight": "assets/backgrounds/bg_insight.jpg",
        "cta": "assets/backgrounds/bg_cta.jpg"
    }
    
    bg_path = mapping.get(slide_type)
    
    if not bg_path:
        raise ValueError(f"Invalid slide_type: {slide_type}")
    
    if not os.path.exists(bg_path):
        raise FileNotFoundError(
            f"Background missing: {bg_path}\n"
            f"Required for slide_type='{slide_type}'\n"
            f"Please add static backgrounds to assets/backgrounds/"
        )
    
    return bg_path


def load_background(slide_type, bg_image_path=None, width=1080, height=1350):
    """
    CENTRAL BACKGROUND LOADER - static backgrounds only.
    
    Args:
        slide_type: "cover" | "news" | "insight" | "cta"
        bg_image_path: IGNORED (reserved for future use)
        width, height: Canvas dimensions
    
    Returns:
        PIL Image with background loaded
    """
    W, H = width, height
    
    # Resolve static background
    bg_source = resolve_background(slide_type)
    
    # Load background
    try:
        with Image.open(bg_source) as raw_bg:
            bg = raw_bg.convert("RGBA")
            ratio = max(W / bg.width, H / bg.height)
            new_size = (int(bg.width * ratio), int(bg.height * ratio))
            bg = bg.resize(new_size, Image.Resampling.LANCZOS)
            left = (bg.width - W) / 2
            top = (bg.height - H) / 2
            bg = bg.crop((left, top, left + W, top + H))
            return bg
    except Exception as e:
        raise RuntimeError(f"Failed to load background {bg_source}: {e}")


def draw_top_brand_bar(img, slide_num, logo_path="assets/yoi_logo.png"):
    W = img.width
    logo_size = 100
    logo_x = 60
    
    # Logo with subtle shadow
    logo_y = 60
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        
        # Shadow for visibility
        shadow = Image.new("RGBA", (logo_size + 10, logo_size + 10), (0, 0, 0, 50))
        img.paste(shadow, (logo_x - 2, logo_y - 2), shadow)
        img.paste(logo, (logo_x, logo_y), logo if logo.mode == 'RGBA' else None)
        
        logo_center_y = logo_y + logo_size // 2
    except:
        logo_center_y = 60 + 50
    
    # Slide number with optical alignment
    try:
        number_font = ImageFont.truetype("arialbd.ttf", 140)
    except:
        number_font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(img)
    
    # Get text bbox for centering
    num_text = f"0{slide_num}"
    bbox = draw.textbbox((0, 0), num_text, font=number_font)
    text_height = bbox[3] - bbox[1]
    
    # Align number center with logo center
    number_y = logo_center_y - text_height // 2
    number_x = W - 220
    
    # Shadow for visibility
    draw.text((number_x + 2, number_y + 2), num_text, font=number_font, fill=(0, 0, 0, 80))
    draw.text((number_x, number_y), num_text, font=number_font, fill=(255, 255, 255, 180))


def draw_glass_card(img, xy, radius=40, fill_color=(20, 20, 20, 210), border_color=(255, 255, 255, 40)):
    """
    Simulates a DARK frosted glass effect.
    Fill: Dark Gray/Black with high opacity (210/255) for readability.
    Border: Faint White to define edges.
    """
    draw = ImageDraw.Draw(img, "RGBA")
    x1, y1, x2, y2 = xy
    
    # Shadows (Deep black soft shadow)
    shadow_offset = 10
    draw.rounded_rectangle([x1+shadow_offset, y1+shadow_offset, x2+shadow_offset, y2+shadow_offset], 
                          radius=radius, fill=(0,0,0,120))
    
    # Glass Body
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill_color)
    
    # Glass Highlight/Border
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, outline=border_color, width=2)
    
    return draw


def get_fonts():
    """Load fonts with fallbacks"""
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 60)
        subtitle_font = ImageFont.truetype("arial.ttf", 40)
        body_font = ImageFont.truetype("arial.ttf", 34)
        small_font = ImageFont.truetype("arial.ttf", 24)
        return title_font, subtitle_font, body_font, small_font
    except:
        # Fallback
        default = ImageFont.load_default()
        return default, default, default, default


def wrap_text(text, font, draw, max_width):
    """Wrap text to fit within max_width"""
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


# ============================================
# GRAPHIC HELPERS (EMOJI EDITION)
# ============================================

def draw_emoji_icon(img, x, y, emoji_char, size, angle=0):
    """
    Draw an emoji at x, y with rotation support.
    """
    try:
        font = ImageFont.truetype("seguiemj.ttf", size)
        has_color = True 
    except:
        try:
            font = ImageFont.truetype("arial.ttf", size)
            has_color = False
        except:
            return

    # Draw to temp for rotation
    buf_size = int(size * 1.5)
    temp = Image.new('RGBA', (buf_size, buf_size), (0,0,0,0))
    temp_draw = ImageDraw.Draw(temp)
    
    try:
        temp_draw.text((buf_size//2, buf_size//2), emoji_char, font=font, anchor="mm", embedded_color=True)
    except TypeError:
        fill = "white" # Icon default white in dark mode if not emoji
        temp_draw.text((buf_size//2, buf_size//2), emoji_char, font=font, anchor="mm", fill=fill)
        
    if angle != 0:
        rotated = temp.rotate(angle, expand=True, resample=Image.BICUBIC)
    else:
        rotated = temp

    # Paste
    rw, rh = rotated.size
    img.paste(rotated, (x - rw//2, y - rh//2), rotated)


# ============================================
# SLIDE 1: COVER (DARK MODE)
# ============================================

def build_slide_1_cover(output_dir, logo_path="assets/yoi_logo.png", bg_image_path=None):
    W, H = 1080, 1350
    
    # 1️⃣ BACKGROUND
    img = load_background("cover", bg_image_path, W, H)
    
    # 2️⃣ GLASS CARD
    card_top = 600
    draw_glass_card(img, (50, card_top, W-50, H-100), radius=50, fill_color=(15, 15, 15, 230))
    draw = ImageDraw.Draw(img)

    # 3️⃣ LOGO
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((140, 140), Image.LANCZOS)
        glow = Image.new("RGBA", (180, 180), (255,255,255,0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([0,0,180,180], fill=(255,255,255,50))
        img.paste(glow, (W - 200, 80), glow)
        img.paste(logo, (W - 180, 100), logo if logo.mode == 'RGBA' else None)
    except:
        pass

    # 4️⃣ TEXT CONTENT
    try:
        eyebrow_font = ImageFont.truetype("arialbd.ttf", 32)
        headline_font = ImageFont.truetype("arialbd.ttf", 95)
        sub_font = ImageFont.truetype("arial.ttf", 45)
    except:
        eyebrow_font = ImageFont.load_default()
        headline_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    padding_x = 100
    current_y = card_top + 100

    # Pill
    pill_w, pill_h = 350, 70
    pill_y = current_y
    draw.rounded_rectangle([padding_x, pill_y, padding_x+pill_w, pill_y+pill_h], radius=35, fill="#FFCC00")
    
    pill_text = "⚠️ MARKET ALERT"
    text_bbox = draw.textbbox((0, 0), pill_text, font=eyebrow_font)
    text_h = text_bbox[3] - text_bbox[1]
    text_y = pill_y + (pill_h - text_h) // 2
    draw.text((padding_x + 40, text_y), pill_text, font=eyebrow_font, fill="black")

    current_y += 140

    # TEXT NORMALIZATION
    message = "MARKETING SHIFTS".replace("\n", " ").strip()
    draw.text((padding_x, current_y), message, font=headline_font, fill="white", spacing=20)
    
    current_y += 150

    # TEXT NORMALIZATION
    sub_msg = "Today's Marketing Updates".replace("\n", " ").strip()
    draw.text((padding_x, current_y), sub_msg, font=sub_font, fill="#CCCCCC", spacing=15)

    draw_emoji_icon(img, W-150, H-200, "👉", 80)

    out_path = os.path.join(output_dir, "slide_1_cover.png")
    img.save(out_path, "PNG")
    return out_path


# ============================================
# SLIDES 2-4: NEWS CONTENT (DARK MODE)
# ============================================

def build_news_slide(output_dir, slide_num, headline, insight, logo_path="assets/yoi_logo.png", bg_image_path=None):
    os.makedirs(output_dir, exist_ok=True)
    W, H = 1080, 1350
    
    # TEXT NORMALIZATION
    headline = headline.replace("\n", " ").strip()
    insight = insight.replace("\n", " ").strip()
    
    # 1️⃣ BACKGROUND
    img = load_background("news", bg_image_path, W, H)
    
    # 2️⃣ TOP BRAND BAR
    draw_top_brand_bar(img, slide_num, logo_path)
    
    # 3️⃣ GLASS CARD
    draw_glass_card(img, (60, 250, W-60, H-200), radius=50, fill_color=(20, 20, 20, 240))
    draw = ImageDraw.Draw(img)

    # 4️⃣ TEXT CONTENT
    try:
        headline_font = ImageFont.truetype("arialbd.ttf", 60)
        insight_title_font = ImageFont.truetype("arialbd.ttf", 35)
        insight_font = ImageFont.truetype("arial.ttf", 45)
        pill_font = ImageFont.truetype("arialbd.ttf", 30)
    except:
        headline_font = ImageFont.load_default()
        insight_title_font = ImageFont.load_default()
        insight_font = ImageFont.load_default()
        pill_font = ImageFont.load_default()

    text_x = 120
    current_y = 350
    
    # BREAKING Pill
    draw.rounded_rectangle([text_x, current_y, text_x+220, current_y+60], radius=15, fill="#FF4500")
    draw.text((text_x+30, current_y+10), "BREAKING", font=pill_font, fill="white")
    
    current_y += 120

    # Headline
    headline_lines = wrap_text(headline, headline_font, draw, 800)
    for line in headline_lines:
        draw.text((text_x, current_y), line, font=headline_font, fill="white")
        current_y += 85

    current_y += 60
    draw.line([(text_x, current_y), (W-text_x, current_y)], fill="#444444", width=2)

    current_y += 60
    draw.text((text_x, current_y), "TACTICAL INSIGHT", font=insight_title_font, fill="#FFCC00")
    
    current_y += 70
    insight_lines = wrap_text(insight, insight_font, draw, 800)
    for line in insight_lines:
        draw.text((text_x, current_y), line, font=insight_font, fill="#DDDDDD")
        current_y += 60

    out_path = os.path.join(output_dir, f"slide_{slide_num}.png")
    img.save(out_path, "PNG")
    return out_path


# ============================================
# SLIDE 5: CTA (DARK MODE)
# ============================================

def build_slide_5_cta(output_dir, logo_path="assets/yoi_logo.png"):
    W, H = 1080, 1350
    
    # 1️⃣ BACKGROUND (central loader)
    img = load_background("cta", None, W, H)
    
    # 2️⃣ GLASS CARD
    draw_glass_card(img, (80, 200, W-80, 1150), radius=60, fill_color=(20, 20, 20, 255))
    draw = ImageDraw.Draw(img)
    
    # 3️⃣ LOGO (centered top)
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((220, 220), Image.LANCZOS)
        img.paste(logo, (W//2 - 110, 300), logo if logo.mode == 'RGBA' else None)
    except:
        pass
    
    # 4️⃣ TEXT CONTENT
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 70)
        body_font = ImageFont.truetype("arial.ttf", 40)
        button_font = ImageFont.truetype("arialbd.ttf", 35)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        button_font = ImageFont.load_default()
    
    draw.text((W//2, 600), "Stay Ahead.", font=title_font, fill="white", anchor="mm")
    draw.text((W//2, 750), "Join 10k+ Marketers\\nmastering AI with us.", font=body_font, fill="#AAAAAA", anchor="mm", align="center")
    
    # Icons
    icon_y = 920
    spacing = 180
    start_x = (W - (spacing * 2)) // 2
    draw_emoji_icon(img, start_x, icon_y, "📸", 100)
    draw_emoji_icon(img, start_x + spacing, icon_y, "🎵", 100)
    draw_emoji_icon(img, start_x + spacing*2, icon_y, "👥", 100)
    
    # Button
    draw.rounded_rectangle([300, 1050, 780, 1180], radius=40, fill="#FF6600")
    draw.text((540, 1115), "Follow @YOIMarketing", font=button_font, fill="white", anchor="mm")
    
    out_path = os.path.join(output_dir, "slide_5_cta.png")
    img.save(out_path, "PNG")
    return out_path

