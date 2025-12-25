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

def draw_grid_background(draw, width, height, grid_size=40, color="#f0f0f0"):
    """Draw light grid pattern on background"""
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=color, width=1)


def draw_border_dots(draw, width, height, dot_size=12, spacing=35):
    """Draw decorative dots on top and bottom borders"""
    y_top = 45
    y_bottom = height - 50
    
    for x in range(90, width - 90, spacing):
        # Top dots
        draw.ellipse([(x, y_top), (x + dot_size, y_top + dot_size)], fill="black")
        # Bottom dots
        draw.ellipse([(x, y_bottom), (x + dot_size, y_bottom + dot_size)], fill="black")


def draw_rounded_rectangle(draw, xy, radius, outline="black", fill=None, width=3):
    """Draw a rounded rectangle frame"""
    x1, y1, x2, y2 = xy
    
    # Draw the rectangles for sides with rounded corners
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill, outline=outline, width=width)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill, outline=outline, width=width)
    
    # Draw the four corner circles
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill, outline=outline, width=width)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill, outline=outline, width=width)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill, outline=outline, width=width)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill, outline=outline, width=width)


def get_fonts():
    """Load fonts with fallbacks"""
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 52)
        subtitle_font = ImageFont.truetype("arial.ttf", 38)
        body_font = ImageFont.truetype("arial.ttf", 32)
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
    Uses Segoe UI Emoji on Windows.
    """
    try:
        font = ImageFont.truetype("seguiemj.ttf", size)
        # Check color support (PIL 10+)
        has_color = True 
    except:
        # Fallback to default if seguiemj not found
        try:
            font = ImageFont.truetype("arial.ttf", size)
            has_color = False
        except:
            return

    # Draw to temp for rotation
    # Emojis are often square-ish, make temp buffer big enough
    buf_size = int(size * 1.5)
    temp = Image.new('RGBA', (buf_size, buf_size), (0,0,0,0))
    temp_draw = ImageDraw.Draw(temp)
    
    # Center text in temp
    # Use embedded_color=True for PIL > 10
    try:
        temp_draw.text((buf_size//2, buf_size//2), emoji_char, font=font, anchor="mm", embedded_color=True)
    except TypeError:
         # Fallback for older PIL
        fill = "black" if not has_color else "white" # Some system fonts might need color set
        temp_draw.text((buf_size//2, buf_size//2), emoji_char, font=font, anchor="mm", fill=fill)
        
    # Rotate
    if angle != 0:
        rotated = temp.rotate(angle, expand=True, resample=Image.BICUBIC)
    else:
        rotated = temp

    # Paste
    # Calculate offset
    rw, rh = rotated.size
    img.paste(rotated, (x - rw//2, y - rh//2), rotated)


def draw_arrow_curved_clean(draw, start, end, color="#FF6600", width=6):
    """
    Draw a smoother curved arrow using PIL arc/chord or Bezier
    """
    x1, y1 = start
    x2, y2 = end
    
    # Simple quadratic bezier
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    # Offset control point to create curve
    cx = mx - (y2 - y1) * 0.3
    cy = my + (x2 - x1) * 0.3
    
    steps = 15
    points = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
        by = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
        points.append((bx, by))
        
    draw.line(points, fill=color, width=width, joint="curve")
    
    # Arrow head
    # Angle of last segment
    lx, ly = points[-2]
    import math
    angle = math.atan2(y2 - ly, x2 - lx)
    
    head_len = 25
    arrow_angle = math.radians(20)
    
    p1 = (x2 - head_len * math.cos(angle - arrow_angle), y2 - head_len * math.sin(angle - arrow_angle))
    p2 = (x2 - head_len * math.cos(angle + arrow_angle), y2 - head_len * math.sin(angle + arrow_angle))
    
    draw.polygon([p1, (x2, y2), p2], fill=color)

def draw_scribble_arrow_pink(draw, x, y, size):
    """Simple pink decorative arrow"""
    color = "#FF66CC"
    x, y = int(x), int(y)
    draw.arc([x, y, x+60, y+60], 180, 0, fill=color, width=5)
    draw.line([x+60, y+30, x+80, y-10], fill=color, width=5)
    # Head
    draw.polygon([(x+80, y-10), (x+70, y), (x+85, y+5)], fill=color)


# ============================================

def build_slide_1_cover(output_dir, logo_path="assets/yoi_logo.png"):
    """
    Create Slide 1 - Cover slide with YOI branding AND Emoji Graphics
    """
    # Create base image
    width, height = 1080, 1350
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # 1. Background Grid & Dots
    draw_grid_background(draw, width, height)
    draw_border_dots(draw, width, height)
    
    # 2. Main Frame
    frame_box = (150, 220, 930, 1020) 
    
    # Shadow
    shadow_offset = 15
    draw_rounded_rectangle(draw, (frame_box[0]+shadow_offset, frame_box[1]+shadow_offset, frame_box[2]+shadow_offset, frame_box[3]+shadow_offset), 
                          radius=40, outline=None, fill="#EEEEEE", width=0)
    # Main Frame
    draw_rounded_rectangle(draw, frame_box, radius=40, outline="black", fill="white", width=6)
    
    # 3. YOI Logo (Top Left)
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((150, 150), Image.LANCZOS)
        img.paste(logo, (80, 50), logo if logo.mode == 'RGBA' else None)
    except:
        pass
        
    # 4. Social Media Icons (Top Center floating out of frame)
    # Using Emojis now for cleaner look
    icon_y = 180
    
    # TikTok -> Music Note 🎵 (or similar)
    draw_emoji_icon(img, 350, icon_y + 20, "🎵", 100, angle=-10)
    
    # Instagram -> Camera 📸
    draw_emoji_icon(img, 500, icon_y - 20, "📸", 110, angle=0)
    
    # Facebook -> Blue Circle + 'f' or just Blue Book 📘 as abstract
    # Let's use 🔵 and draw 'f' on top for best look, OR just use valid Facebook-ish logic
    # Actually, emoji 📘 is okay, or we stick to the nice manual one I wrote earlier?
    # User said "stick to emojis". Let's use 🔷 (Large Blue Diamond) or similar? 
    # Or just use the manual "f" because it looked okay? 
    # Let's use the Emoji approach for consistency -> 🌐 (Globe) or 👥 (People)?
    # Actually, let's mix: Draw a blue circle emoji 🔵 and put text "f" on it?
    draw_emoji_icon(img, 650, icon_y + 20, "🔵", 100)
    # Draw 'f' on top of the blue circle
    try:
        f_font = ImageFont.truetype("arialbd.ttf", 60)
        draw.text((650, icon_y + 20), "f", font=f_font, fill="white", anchor="mm")
    except:
        pass
    
    # 5. Decorative: Pencil (Top Right)
    # ✏️
    draw_emoji_icon(img, 930, 200, "✏️", 200, angle=-45)
    
    # 6. Typography
    title_font, subtitle_font, body_font, small_font = get_fonts()
    try:
        headline_font = ImageFont.truetype("arialbd.ttf", 68)
        stop_font = ImageFont.truetype("arialbd.ttf", 55)
    except:
        headline_font = title_font
        stop_font = title_font

    # "Stop scrolling" Group
    stop_y = 420
    # Stop Sign 🛑 + Hand ✋
    draw_emoji_icon(img, 180, stop_y, "🛑", 90)
    draw_emoji_icon(img, 180, stop_y, "✋", 50) # Overlay hand? might look messy. Just Stop Sign is clear.
    # OR: Hand ✋ on left, Stop Sign 🛑 on right?
    # Reference had Stop Sign icon. Let's start with just 🛑
    
    draw.text((260, stop_y - 30), "Stop scrolling", font=stop_font, fill="black")
    
    # Arrow pointing to Instagram icon
    draw_arrow_curved_clean(draw, (280, 380), (450, 240), color="#FF6600", width=5)
    
    # Main Headline
    message = '"These 5 marketing\nshifts are changing\neverything in 2025."'
    # Center text
    text_bbox = draw.multiline_textbbox((0,0), message, font=headline_font, spacing=10)
    text_w = text_bbox[2] - text_bbox[0]
    text_x = (width - text_w) // 2
    draw.multiline_text((text_x, 600), message, font=headline_font, fill="black", align="center", spacing=10)
    
    # 7. "NEW IN" Badge (Bottom Center)
    badge_w, badge_h = 240, 90
    badge_x = (width - badge_w) // 2
    badge_y = 880
    
    # Oval background (Yellow with black border)
    draw.ellipse([(badge_x, badge_y), (badge_x+badge_w, badge_y+badge_h)], fill="#FFFA50", outline="black", width=4)
    # Text
    try:
        badge_font = ImageFont.truetype("arialbd.ttf", 36)
    except:
        badge_font = body_font
    
    bw_bbox = draw.textbbox((0,0), "NEW IN", font=badge_font)
    bw = bw_bbox[2] - bw_bbox[0]
    draw.text((badge_x + (badge_w-bw)//2, badge_y + 25), "NEW IN", font=badge_font, fill="black")
    
    # 8. Bottom Graphics
    # Magnifying Glass 🔍
    draw_emoji_icon(img, 200, 1050, "🔍", 180, angle=-15)
    
    # Pink Scribble (Bottom Right)
    draw_scribble_arrow_pink(draw, 850, 950, 100)
    
    # Save
    out_path = os.path.join(output_dir, "slide_1_cover.png")
    img.save(out_path, "PNG")
    return out_path



# ============================================
# SLIDES 2-4: NEWS CONTENT (DYNAMIC)
# ============================================

def build_news_slide(output_dir, slide_num, headline, insight, logo_path="assets/yoi_logo.png"):
    """
    Create news slide (2-4) with professional emoji accents and polished typography.
    """
    # Pastel gradient backgrounds for each slide (consistent but distinct)
    bg_colors = [
        ((255, 248, 240), (255, 235, 220)),  # Slide 2: Very light peach
        ((240, 248, 255), (220, 240, 255)),  # Slide 3: Very light blue
        ((248, 240, 255), (240, 225, 255)),  # Slide 4: Very light purple
    ]
    
    color1, color2 = bg_colors[(slide_num - 2) % 3]
    
    # Create base image with gradeint
    width, height = 1080, 1350
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # Draw diagonal gradient background
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Grid (subtle)
    draw_grid_background(draw, width, height, grid_size=40, color="#e0e0e0")
    
    # Border dots
    draw_border_dots(draw, width, height, dot_size=14)
    
    # YOI Logo
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((150, 150), Image.LANCZOS)
        img.paste(logo, (80, 50), logo if logo.mode == 'RGBA' else None)
    except:
        pass
    
    # Main Content Frame
    frame_box = (120, 260, 960, 1100)
    # Shadow
    draw_rounded_rectangle(draw, (frame_box[0]+10, frame_box[1]+10, frame_box[2]+10, frame_box[3]+10), 
                          radius=30, outline=None, fill="#DDDDDD", width=0)
    # Frame
    draw_rounded_rectangle(draw, frame_box, radius=30, outline="black", fill="white", width=5)
    
    # Fonts
    title_font, subtitle_font, body_font, small_font = get_fonts()
    try:
        headline_font = ImageFont.truetype("arialbd.ttf", 58) # Slightly smaller than cover for longer headlines
        insight_font = ImageFont.truetype("arial.ttf", 42)
        badge_font = ImageFont.truetype("arialbd.ttf", 32)
    except:
        headline_font = title_font
        insight_font = subtitle_font
        badge_font = body_font

    # "TRENDING" Badge (Top Left of frame)
    badge_x, badge_y = 160, 290
    # Custom Oval Badge (Orange)
    draw.ellipse([(badge_x-10, badge_y-10), (badge_x+240, badge_y+60)], fill="#FF6600", outline="black", width=3)
    draw.text((badge_x+25, badge_y+5), "🔥 TRENDING", font=badge_font, fill="white")
    
    # Decorative: Pin 📌 or Sparkle ✨
    draw_emoji_icon(img, 920, 250, "📌", 100, angle=20)
    
    # HEADLINE
    # Wrap text
    headline_lines = wrap_text(headline, headline_font, draw, 750)
    y_pos = 420
    
    for line in headline_lines:
        msg_bbox = draw.textbbox((0,0), line, font=headline_font)
        msg_w = msg_bbox[2] - msg_bbox[0]
        x_pos = (width - msg_w) // 2
        
        # Text Shadow (Hard black for pop)
        draw.text((x_pos+2, y_pos+2), line, font=headline_font, fill="#DDDDDD")
        draw.text((x_pos, y_pos), line, font=headline_font, fill="black")
        y_pos += 75
        
    # Divider Line
    div_y = y_pos + 30
    draw.line([(300, div_y), (780, div_y)], fill="#EEEEEE", width=4)
    
    # INSIGHT
    y_pos += 80
    insight_lines = wrap_text(insight, insight_font, draw, 750)
    
    # Draw simple "Insight" label or icon
    draw_emoji_icon(img, 540, y_pos - 40, "💡", 60) # Lightbulb above insight
    
    for line in insight_lines:
        msg_bbox = draw.textbbox((0,0), line, font=insight_font)
        msg_w = msg_bbox[2] - msg_bbox[0]
        x_pos = (width - msg_w) // 2
        
        draw.text((x_pos, y_pos), line, font=insight_font, fill="#444444")
        y_pos += 55
        
    # Slide Number (Bottom Right of frame)
    # Circle
    circle_x, circle_y = 850, 1000
    draw.ellipse([(circle_x, circle_y), (circle_x+80, circle_y+80)], fill="black", outline=None)
    draw.text((circle_x+22, circle_y+20), f"{slide_num}", font=badge_font, fill="white")
    
    # Save
    out_path = os.path.join(output_dir, f"slide_{slide_num}.png")
    img.save(out_path, "PNG")
    return out_path


# ============================================
# SLIDE 5: CTA (STATIC)
# ============================================

def build_slide_5_cta(output_dir, logo_path="assets/yoi_logo.png"):
    """
    Create Slide 5 - Thank you / CTA slide with Socials
    """
    width, height = 1080, 1350
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # 1. Background
    draw_grid_background(draw, width, height)
    draw_border_dots(draw, width, height)
    
    # 2. Frame
    frame_box = (150, 300, 930, 1050)
    draw_rounded_rectangle(draw, (frame_box[0]+15, frame_box[1]+15, frame_box[2]+15, frame_box[3]+15), 
                          radius=40, outline=None, fill="#EEEEEE", width=0)
    draw_rounded_rectangle(draw, frame_box, radius=40, outline="black", fill="white", width=6)
    
    # 3. Logo
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((200, 200), Image.LANCZOS)
        # Center logo above frame
        img.paste(logo, (440, 150), logo if logo.mode == 'RGBA' else None)
    except:
        pass
        
    # Fonts
    title_font, subtitle_font, body_font, small_font = get_fonts()
    try:
        ct_font = ImageFont.truetype("arialbd.ttf", 60)
        action_font = ImageFont.truetype("arialbd.ttf", 45)
    except:
        ct_font = title_font
        action_font = subtitle_font
        
    # 4. Text Content
    # "Thank You"
    draw.text((380, 450), "Thank You", font=ct_font, fill="black")
    draw.text((410, 520), "For Reading!", font=title_font, fill="black")
    
    # 5. Social Icons Grid
    # Re-use our nice emojis
    icon_y = 700
    spacing = 180
    start_x = (width - (spacing * 2)) // 2
    
    # Labels
    draw.text((width//2 - 100, 620), "Follow for more:", font=body_font, fill="#666666")
    
    # Icons
    draw_emoji_icon(img, start_x, icon_y, "📸", 100) # Instagram
    draw_emoji_icon(img, start_x + spacing, icon_y, "🎵", 90) # TikTok
    draw_emoji_icon(img, start_x + spacing*2, icon_y, "🔵", 90) # Facebook
    try:
        f_font = ImageFont.truetype("arialbd.ttf", 50)
        draw.text((start_x + spacing*2, icon_y), "f", font=f_font, fill="white", anchor="mm")
    except:
        pass

    # 6. "Save for Later"
    # Bookmark Icon
    draw_emoji_icon(img, 900, 300, "🔖", 120, angle=0)
    # Simple arrow pointing to bookmark from text?
    
    # Final CTA Button
    btn_w, btn_h = 400, 100
    btn_x = (width - btn_w) // 2
    btn_y = 880
    
    draw_rounded_rectangle(draw, (btn_x, btn_y, btn_x+btn_w, btn_y+btn_h), radius=50, outline="black", fill="#FFFA50", width=4)
    draw.text((btn_x + 60, btn_y + 25), "@YOIMarketing", font=action_font, fill="black")
    
    # Save
    out_path = os.path.join(output_dir, "slide_5_cta.png")
    img.save(out_path, "PNG")
    return out_path
