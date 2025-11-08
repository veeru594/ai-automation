# app.py — YOI Media Carousel Generator (Enhanced for n8n + Drive Upload)
import os
import time
import json
import base64
import pathlib
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
# from stability_client import generate_image, ImageGenerationError # Leonardo later

# ---- Environment ----
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

from stability_client import generate_image, ImageGenerationError # Leonardo later

OUTPUT_DIR = pathlib.Path(os.getenv("OUTPUT_DIR", "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE = pathlib.Path(os.getenv("METADATA_FILE", "log.json"))
MAX_IMAGE_AGE_DAYS = int(os.getenv("MAX_IMAGE_AGE_DAYS", "7"))

# ---- Logging ----
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("yoi_carousel")

app = Flask(__name__)

# ---- Carousel Templates ----
CAROUSEL_TEMPLATES = {
    "daily_updates": {
        "meta": {
            "prompt_template": "Daily Digital Marketing Updates",
            "format": "1080x1350",
            "brand": "YOI Media"
        },
        "slides": [
            {"focus": "Hook", "copy": "STOP scrolling — this week changed digital marketing 👇"},
            {"focus": "Problem", "copy": "You blinked — and Meta dropped 3 new ad features."},
            {"focus": "Insight", "copy": "Algorithms aren’t dying — they’re learning faster than you post."},
            {"focus": "Framework", "copy": "3 updates you must act on: Reels AI Captions, Google SGE Beta, TikTok Shop Ads."},
            {"focus": "Proof", "copy": "Our client applied this — 48K organic reach in 3 days."},
            {"focus": "CTA", "copy": "Save + follow @yoimarketing for daily updates ⚡"}
        ]
    },
    "awareness": {
        "meta": {
            "prompt_template": "Digital Marketing Awareness",
            "format": "1080x1080",
            "brand": "YOI Media"
        },
        "slides": [
            {"focus": "Hook", "copy": "EVERYONE says they ‘do digital marketing’ — but do they?"},
            {"focus": "Problem", "copy": "Most brands post → pray → hope for reach."},
            {"focus": "Insight", "copy": "Marketing isn’t posting. It’s positioning."},
            {"focus": "Framework", "copy": "The 4 Pillars of Digital Awareness → Content, Target, Consistency, Conversion."},
            {"focus": "Proof", "copy": "YOI clients grew 4× reach after fixing their positioning."},
            {"focus": "CTA", "copy": "Follow @yoimarketing to learn digital the smart way 🧠"}
        ]
    }
}

# ---- Helper Functions ----
def write_metadata(entry):
    try:
        data = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []
        data.append(entry)
        METADATA_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        logger.exception("Failed to write metadata: %s", e)


def cleanup_outputs():
    now = datetime.utcnow()
    cutoff = now - timedelta(days=MAX_IMAGE_AGE_DAYS)
    for f in OUTPUT_DIR.glob("*.png"):
        if datetime.utcfromtimestamp(f.stat().st_mtime) < cutoff:
            try:
                f.unlink()
                logger.info("Deleted old file: %s", f.name)
            except Exception:
                logger.warning("Failed to delete file: %s", f.name)


def overlay_slide_number(image_path: str, text: str):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = int(width / 25)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    x = (width - bbox[2]) / 2
    y = height - 80
    draw.rectangle([(x - 20, y - 10), (x + bbox[2] + 20, y + bbox[3] + 10)], fill=(0, 0, 0, 130))
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    img = Image.alpha_composite(img, overlay)
    img.convert("RGB").save(image_path, "PNG")

# ---- Routes ----
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()}), 200


# ✅ Serve output images for n8n / Drive upload
@app.route("/outputs/<path:filename>", methods=["GET"])
def serve_output(filename):
    """
    Allows n8n or remote apps to download generated images via URL.
    """
    safe_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(safe_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/generate_carousel", methods=["POST"])
def generate_carousel():
    """
    Accepts JSON:
    { "template": "daily_updates" or "awareness", "prompt": optional unified text }
    """
    payload = request.get_json(force=True)
    template_key = payload.get("template", "daily_updates")
    user_prompt = payload.get("prompt")

    if user_prompt:
        logger.info("Received custom unified prompt")
        prompt_context = user_prompt
    else:
        prompt_context = f"Default {template_key} prompt"

    if template_key not in CAROUSEL_TEMPLATES:
        return jsonify({"error": f"Invalid template key '{template_key}'"}), 400

    template = CAROUSEL_TEMPLATES[template_key]
    slides_data = []
    logger.info("Generating carousel: %s", template_key)

    for idx, slide in enumerate(template["slides"], start=1):
        # build the exact prompt that will go to Stability
        prompt_to_stability = f"""
Create a single Instagram carousel slide ({template['meta']['format']})
in the YOI Media brand style (90% minimal, 10% pop).
Colors: #000000, #ffffff, #ff6600.
Include the YOI Media logo bottom-right.
Slide type: {slide['focus']}.
Context copy: "{slide['copy']}".
Overall context (from n8n if provided): "{prompt_context}"
Ensure composition, hierarchy, and no embedded text in the image.
        """

        logger.info("Generating slide %s with prompt (first 200 chars): %s", idx, prompt_to_stability[:200])

        try:
            # call the Stability AI wrapper (must return {"b64":..., "source":..., "raw_response": {...}})
            result = generate_image(prompt_to_stability)

            # make sure we always have the raw response for debugging
            raw_resp = None
            if isinstance(result, dict):
                raw_resp = result.get("raw_response")

            # validate presence of base64 data
            b64str = result.get("b64") or result.get("data") or result.get("image_b64")
            if not b64str:
                raise Exception("No base64 string found in generator result. Keys present: " + ",".join(result.keys()))

            # decode and save image
            timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            filename = f"{timestamp}_{template_key}_slide{idx}.png"
            filepath = OUTPUT_DIR / filename

            image_bytes = base64.b64decode(b64str)
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            # overlay slide number at the bottom
            overlay_slide_number(filepath, f"Slide {idx} of {len(template['slides'])}")

            slides_data.append({
                "index": idx,
                "focus": slide["focus"],
                "copy": slide["copy"],
                "filename": filename,
                "local_path": str(filepath),
                "file_url": f"http://127.0.0.1:5000/outputs/{filename}",
                "source": result.get("source"),
                "raw_response": raw_resp
            })

            # small delay to prevent rate limiting
            time.sleep(2)

        except Exception as e:
            logger.exception("Slide %d failed: %s", idx, e)
            slides_data.append({
                "index": idx,
                "error": str(e),
                "prompt_sent": prompt_to_stability
            })

    # cleanup and log metadata
    cleanup_outputs()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "template": template_key,
        "slides": slides_data
    }
    write_metadata(entry)

    return jsonify({
        "status": "success",
        "post_type": "carousel",
        "brand": template["meta"]["brand"],
        "meta": template["meta"],
        "slides": slides_data,
        "generated_at": datetime.utcnow().isoformat()
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
